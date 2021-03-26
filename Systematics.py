import numpy as np
from copy import deepcopy

class Systematics:
    '''
    Simple helper class to manage systematics.
    Systematics are added linearly or in quadrature. In quadrature may result in funny behavior as sign information is lost.
    '''
    def __init__(self,name=[],down=[],up=[]):
        self._sys_name = deepcopy(name)
        self._sys_down = deepcopy(down)
        self._sys_up = deepcopy(up)
    def total_sys(self, sys, in_quad=0):
        sys = deepcopy(sys)
        if not in_quad:
            return np.sum(sys,axis=0)
        else:
            sign = np.sign(np.sum(sys,axis=0))
            sys_squared = np.power(sys,2)
            sys_sum = np.sum(sys_squared,axis=0)
            return np.power(sys_sum,.5)*sign
    def sys_up(self, in_quad=0):
        return self.total_sys(self._sys_up, in_quad=in_quad)
    def sys_down(self, in_quad=0):
        return self.total_sys(self._sys_down, in_quad=in_quad)
    def add_sys(self, name, sys_up, sys_down):
        if len(self._sys_down) > 0:
            assert len(self._sys_down[0]) == len(sys_down), "Sys down length much match., {} vs {}".format(len(self._sys_down[0]), len(sys_down))
            assert len(self._sys_up[0]) == len(sys_up), "Sys up length much match., {} vs {}".format(len(self._sys_up[0]), len(sys_up))
        syst_zip = zip(sys_up,sys_down)
        sys_zip_sorted = list(map(sorted,syst_zip))
        down, up = list(zip(*sys_zip_sorted))
        self._sys_name.append(name)
        self._sys_down.append(down)
        self._sys_up.append(up)
    def add(self,syst):
        name = list(self._sys_name)+list(syst._sys_name)
        down = list(self._sys_down)+list(syst._sys_down)
        up = list(self._sys_up)+list(syst._sys_up)
        return Systematics(name=name,down=down,up=up)
    def __repr__(self):
        return "{} down: {} up: {}".format(self._sys_name, np.sum(self.sys_down()), np.sum(self.sys_up()) )
    def __str__(self):
        return "down: {} up: {}".format(self._sys_name, np.sum(self.sys_down()), np.sum(self.sys_up()) )

if __name__=="__main__":
    syst = Systematics()
    syst_down = [-1,-2,3]
    syst_up = [1,2,-3]
    syst.add_sys("test1", syst_up, syst_down)
    assert syst == "['test1'] down: -6 up: 6"