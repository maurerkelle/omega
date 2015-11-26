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

from .omega import Omega

class RectConcreteDesign(object):
    def __init__(self):
        # parameters
        self.w = 1.0        # width
        self.h = 1.0        # height
        self.d1 = 0.1       # d1
        self.d2 = 0.1       # d2
        self.MEd = 1.0      # bending moment
        self.NEd = 0.0      # normal force
        self.fcd = 14.1667  # compression strength

        # calculated params
        self._d = 0.0
        self._MEd = 0.0
        self._NEd = 0.0
        self._mus1ed = 0.0
        self._zs = 0.0
        self._As1 = 0.0
        self._As2 = 0.0

        # ###
        self._omega = Omega() # TODO how to set its parameters?


    # parameter is a dictionary, e.g.:
    # param["w"] = 1.0
    # param["h"] = 3.0...
    # you got the point!
    def set_params(self, parameter):
        keys = parameter.keys()
        for key in keys:
            self.__dict__[key] = parameter[key] # i love python!
        self.recalc()

    def recalc(self):
        self._d = self.h - self.d1
        self._zs = self._d - self.h*0.5
        MEds = self.MEd - self.NEd * self._zs
        geomFac = (self.w * self._d * self._d * 1000.0 * self.fcd)  # TODO 1000???
        lim_MEds = self._omega.lim_mus1ed() * geomFac
        diff_MEds = 0.0
        self._mus1ed = MEds / geomFac
        if lim_MEds < MEds:
            self._mus1ed = self._omega.lim_mus1ed()
            diff_MEds = MEds - lim_MEds

        self._omega.calc_equilibrium(self._mus1ed)
        self._As1 = 10000.0*(1.0 / (1000.0*self._omega.fyd)) * (self._omega.omega_1 * self.w * self._d * 1000.0*self.fcd + self._NEd)  # AS1: cm²
        self._As2 = 10000.0*(diff_MEds / (self._d - self.d2))/(1000.0*self._omega.fyd)

