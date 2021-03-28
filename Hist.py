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
        assert (len(bin_edges) == len(val)+1), "Wrong bin size"
        assert (len(val)==len(var)), "Wrong var size" 
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
        val = uproot_hist.to_numpy()[0]
        var = uproot_hist.variances()
        return cls(bin_edges,val,var,**kwargs)       
    def add(self,hist,kwargs={}):
        assert (list(self.bin_edges) == list(hist.bin_edges)), "must have same bins"
        val = self.val + hist.val
        var = self.var + hist.var
        sys = self.sys.add(hist.sys)
        name = "{} {}".format(self.name, hist.name)
        return Hist1D(self.bin_edges,val,var,sys=sys, **kwargs)
    def stdev(self):
        return self.var**.5
    def bin_center(self):
        return average_list_pairs(self.bin_edges)
    def __str__(self):
        return "Name: {}".format(self.name, np.sum(self.val), np.sum(self.var), self.bin_edges[0], self.bin_edges[-1])
    def __repr__(self):
        return "Name: {} Sum:{:.2f} Var:{:.2f} Range:{}-{} nBins: {}".format(self.name, np.sum(self.val), np.sum(self.var), self.bin_edges[0], self.bin_edges[-1],
       self.n_bins())
    def n_bins(self):
        return len(self.val)
    def range(self, min_range,max_range):
        bins = self.bin_edges
        mask = (bins>min_range)*(bins<max_range)
        mask_reduced = np.asarray(average_list_pairs(mask*1))==1
        return Hist1D(bins[mask], self.val[mask_reduced], self.var[mask_reduced],plt_kwargs=self.plt_kwargs)
    def plot(self,ax,kwargs={}):
        _kwargs = {**self.plt_kwargs,**kwargs}
        ax.errorbar(self.bin_center(),self.val,yerr=self.stdev(),**_kwargs)
    