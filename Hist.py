import numpy as np
import uproot 
from uproot_plotting_tools.Systematics import Systematics
from copy import deepcopy
from uproot_plotting_tools.utils import average_list_pairs

class Hist1D:
    '''
    Basic custom hist class that supports systematics and works with uproot.
     
    '''
    def __init__(self, bin_edges, val, var, sys=Systematics(), name=0, title=0, category=0, plt_kwargs={}):
        self.bin_edges = deepcopy(bin_edges)
        self.val = np.array(deepcopy(val))
        self.var = np.array(deepcopy(var))
        self.sys = sys
        self.name = name
        self.title = title
        self.category = category
        self.plt_kwargs = plt_kwargs
    @classmethod
    def from_uproot(cls, uproot_hist, kwargs={}):
        bin_edges = uproot_hist.to_numpy()[1]
        bin_center = average_list_pairs(bin_edges)
        val = uproot_hist.to_numpy()[0]
        var = uproot_hist.variances()
        return cls(bin_edges,val,var,**kwargs)       
    def add(self,hist,kwargs={}):
        assert (list(self.bin_edges) == list(hist.bin_edges)), "must have same bins"
        val = self.val, hist.val
        var = self.var + hist.var
        sys = self.sys.add(hist.sys)
        name = "{} {}".format(self.name, hist.name)
        return Hist1D(self.bin_edges,val,var,sys=sys, **kwargs)
    def __str__(self):
        return "Name: {}".format(self.name, np.sum(self.val), np.sum(self.var), self.bin_edges[0], self.bin_edges[-1])
    def __repr__(self):
        return "Name: {} Sum:{} Var:{} Range:{} to {}".format(self.name, np.sum(self.val), np.sum(self.var), self.bin_edges[0], self.bin_edges[-1])
    def standard_dev(self):
        return self.var**.5