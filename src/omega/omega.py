#
#   Copyright (C) 2015  Sven Kromminga
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

__author__ = 'Sven Kromminga'

import math
import sys


def simple_alpha_r(eps_c2d):
    """ calculate alpha_r for a concrete C50/60 and with sigma-eps as parabola-rectangle function """
    eps_c2d = abs(eps_c2d)
    if eps_c2d <= 2.0:
        return (6.0 * eps_c2d - math.pow(eps_c2d, 2.0)) / 12.0
    elif eps_c2d <= 3.5:
        return (3.0 * eps_c2d - 2.0) / (3.0 * eps_c2d)
    else:
        return 0.0


def simlpe_ka(eps_c2d):
    """calculate k_a for a concrete C50/60 and with sigma-eps as parabola-rectangle function"""
    eps_c2d = abs(eps_c2d)
    if eps_c2d <= 2.0:
        return (8.0 - eps_c2d)/(24.0-4.0*eps_c2d)
    elif eps_c2d <= 3.5:
        return (3.0*math.pow(eps_c2d, 2.0)-4.0*eps_c2d+2.0)/(6.0*math.pow(eps_c2d, 2.0)-4.0*eps_c2d)
    else:
        return 0.0


class Omega(object):
    def __init__(self):
        self.equilibrium = False
        self.omega_1 = 0.0
        self.xi = 0.0
        self.zeta = 0.0
        self.epsc2 = 0.0
        self.epss1 = 0.0
        self.vsigma = 0.0

        # TODO create getter/setter with a final call on recalc_values for each
        # default values
        self.n = 2.0
        self.ec2 = 2.0
        self.ec2u = 3.5
        self.epsmax = 25.0
        self.fyk = 500.0
        self.ftkcal = 525.0
        self.gammay = 1.15
        self.Es = 200000.0
        self.epsinc = 0.0001
        self.epss1_lim = 2.174
        self.epsc2_lim = 3.5

        # calculated values
        self.Xu = 0.0
        self.fyd = 0.0
        self.eps_yd = 0.0
        self.eps_ydiff = 0.0
        self.my = 0.0
        self.recalc_values()

    def recalc_values(self):
        self.Xu = self.ec2u / self.ec2
        self.fyd = self.fyk / self.gammay
        self.eps_yd = self.fyd / (self.Es / 1000.0)
        self.eps_ydiff = (self.epsmax-self.eps_yd)
        self.my = (self.ftkcal-self.fyk)/self.gammay

    def alpha_r(self, epsc2d):
        if epsc2d == 0.0:
            return 0.0
        x2 = epsc2d / self.ec2
        n1 = self.n + 1.0
        n1_x2 = n1*x2
        if x2 <= 1.0:
            return (n1_x2-1.0 + math.pow(1.0 - x2, n1)) / n1_x2
        elif x2 <= self.Xu:
            return (n1_x2-1.0)/n1_x2
        else:
            return 0.0

    def ka(self, epsc2d):
        if epsc2d < 0.000001:  # TODO arbitrary limit
            return 1.0/3.0  # TODO is this correct...?
        x2 = epsc2d / self.ec2
        n1 = self.n + 1.0
        n2 = self.n + 2.0
        n2_x2 = n2*x2
        n2_x22 = n2*x2*x2
        if x2 <= 1.0:
            z = (n1*n2_x22-2.0*n2_x2+2.0-2.0*math.pow(1.0-x2, n2))
            return z / (2.0*n1*n2_x22-2.0*n2_x2+2.0*n2_x2*math.pow(1.0-x2, n1))
        elif x2 <= self.Xu:
            return (n1*n2_x22-2.0*n2_x2+2.0)/(2.0*n1*n2_x22-2.0*n2_x2)
        else:
            return 0.0

    # there are 2 functions, this one and the one below _calc_equilibrium
    def calc_equilibrium(self, mus1ed):
        self.epss1 = self.epsmax
        self.epsc2 = 0.0
        self.omega_1 = 0.0
        while self.epss1 >= 0.0:    # start epss1 = epsmax... decrease epss1
            _eps_c2d = abs(self.epsc2)
            self.xi = _eps_c2d/(_eps_c2d + self.epss1)
            _alph_r = self.alpha_r(_eps_c2d)
            _k_a = self.ka(_eps_c2d)
            self.zeta = 1.0 - _k_a * self.xi
            _omega_1 = _alph_r * self.xi

            # calc steel yield stress
            _sigma_sd = 0.0
            if self.epss1 <= self.eps_yd:
                _sigma_sd = (self.Es/1000.0) * self.epss1
            else:
                _sigma_sd = self.fyd + self.my * (self.epss1-self.eps_yd)/self.eps_ydiff
                self.vsigma = _sigma_sd/self.fyd

            _mus1ed_r = self.zeta*_omega_1
            if _mus1ed_r >= mus1ed:
                self.equilibrium = True
                self.omega_1 = _omega_1
                return (self.equilibrium, self.omega_1)

            # start bei epsc2 = 0
            # start bei epss1 = 25
            # dann zunächst die Betondehnung rauf bis 3,5
            # ab dort dann die Stahldehnung runter
            # Warum? Gleichgewicht! kleines Moment => kleine Betondruckkraft => kleine Betondehnung
            if (_eps_c2d + self.epsinc) <= 3.5:
                self.epsc2 -= self.epsinc
            else:
                self.epsc2 = -3.5
                self.epss1 -= self.epsinc

        self.equilibrium = False
        self.omega_1 = -1.0
        return self.equilibrium, self.omega_1

    # TODO make this call a c-function
    def _calc_equilibrium(self, mus1ed):
        return 0.0, 0.0

    def print_equilibrium(self, mus1ed, out=sys.stdout):
        out.write(self.equilibrium_string(mus1ed)+"\n")

    def equilibrium_string(self, mus1ed):
        self.calc_equilibrium(mus1ed)
        ret_string = "%f, %f, %f, %f, %f, %f, %f " % (mus1ed, self.omega_1, self.xi, self.zeta, self.epsc2, self.epss1, self.vsigma)
        return ret_string

    def lim_mus1ed(self):
        __epss1 = self.epss1_lim
        __epsc2 = self.epsc2_lim
        _eps_c2d = abs(__epsc2)
        __xi = _eps_c2d / (_eps_c2d + __epss1)
        _alph_r = self.alpha_r(_eps_c2d)
        _k_a = self.ka(_eps_c2d)
        _zeta = 1.0 - _k_a * __xi
        mus1ed = _alph_r * _zeta * __xi
        return mus1ed


def print_omega_table(out=sys.stdout):
    o = Omega()
    mus1ed = 0.01
    for i in range(0,37):
        o.print_equilibrium(mus1ed, out)
        mus1ed += 0.01
    o.print_equilibrium(0.371, out)
    o.print_equilibrium(0.296, out)
    o.print_equilibrium(0.181, out)


def _static_calc_equilibrium(epsmax):
    pass