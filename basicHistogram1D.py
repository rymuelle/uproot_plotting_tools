import matplotlib
matplotlib.rcParams['text.usetex'] = True
import matplotlib.pyplot as plt
import mplhep as hep
import numpy as np
import uproot
import sys
sys.path.append('./src')
from uproot_plotting_tools.utils import safe_divide

# no overflow
# systematics are sorted based on net negative or positive to down/up
# systematics are added linearly
# systematic histograms are assumed to be non relative to nom value
class basicHistogram1D:
    def __init__(self,name,bin_edges,bin_values=[],bin_std=[],sys_values=[],plot_kwargs={},category=None,blinded=True):
        self.name = name
        self.category = category #typically, background, signal, data etc...
        self.plot_kwargs = plot_kwargs
        self.color = self.set_default('color','black')
        self.label = self.set_default('label',None)
        self.bin_edges = bin_edges
        self.n_bins = len(bin_edges) - 1
        #set bin values
        self.bin_values = self.check_value(bin_values)
        self.bin_std = self.check_value(bin_std)
        #add in sys
        self.has_sys = len(sys_values) > 0
        #only computer systematics if bin has set values
        self.sys_up = self.zero_array()
        self.sys_down = self.zero_array()
        if self.has_sys:
            for sys in sys_values:
                self.add_sys(sys)
    @classmethod
    def from_uproot(cls,name,uproot_hist,uproot_sys=[],plot_kwargs={},category=None):
        bin_edges,values,std = cls.get_hist_uproot(cls,uproot_hist)
        sys_list = []
        for sys in uproot_sys:
            _,sys_value,_ = cls.get_hist_uproot(cls,sys)
            sys_list.append(sys_value)
        return cls(name,bin_edges,bin_values=values,bin_std=std,sys_values=sys_list,plot_kwargs=plot_kwargs,category=category)
    @property
    def check_sys(self):
        return np.sum(np.abs(self.sys_up) + np.abs(self.sys_down)) > 0
    def set_default(self,key,default):
        if key not in self.plot_kwargs: return default
        return self.plot_kwargs[key]    
    @property
    def bin_variance(self):
        return self.bin_std ** 2
    @bin_variance.setter
    def bin_variance(self,var):
        self.bin_std = self.check_value(var) ** .5  
    @property
    def bin_center(self):
        return [(self.bin_edges[i]+self.bin_edges[i+1])/2. for i in range(self.n_bins)]

    def check_value(self,value):
        if len(value)!=0: 
            assert (len(value) == self.n_bins), "Bin values must have same length as bins!"
            return np.asarray(value)
        return self.zero_array()    
    def add_sys(self,sys_values):
        sys_array = np.asarray(sys_values)
        sys_delta = sys_array - self.bin_values
        if np.sum(sys_delta)>0: self.sys_up += sys_delta
        else: self.sys_down += sys_delta
        self.has_sys = True
    def zero_array(self):
        return  np.full(self.n_bins,0.)   
    def get_hist_uproot(self,hist):
        bins = hist.bins
        bin_edges = [bins[i][0] for i in range(len(bins))] #converts from 2D list to 1D edges list
        bin_edges.append(bins[-1][1])
        values = hist.values
        var = hist.variances
        std = var ** .5
        return bin_edges, values, std
    def sum_and_error(self): 
        return np.sum(self.bin_values), np.sum(self.bin_variance) ** .5
    def plot(self,kwargs={},error_bars=True, draw_sys=True, label=False):
        args = [self.bin_values,self.bin_edges]
        if error_bars: self.plot_kwargs['yerr'] = self.bin_std
        
        self.tmp_kwargs = {**self.plot_kwargs,**kwargs}
        if not label: self.tmp_kwargs.pop("label",None)
        hep.histplot(*args, **self.tmp_kwargs) 
    def plot_sys(self,kwargs={}):
        if self.check_sys:
            self.sys_up_block = self.double_list(self.sys_up+self.bin_values)
            self.sys_down_block = self.double_list(self.sys_down+self.bin_values)
            self.tmp_kwargs = {"color":self.color,**kwargs}
            if "ax" in  self.tmp_kwargs:
                self.tmp_kwargs.pop("ax",None)
                kwargs['ax'].fill_between(self.block_bins,self.sys_up_block,self.sys_down_block, **self.tmp_kwargs)
            else: plt.fill_between(self.block_bins,self.sys_up_block,self.sys_down_block, **self.tmp_kwargs)
    #this allows for nice blocky plotting of systematics
    def double_list(self,l_list):
        output = []
        for i,l in enumerate(l_list):
            output.append(l)
            output.append(l)
        return np.asarray(output)
    #blocky bin edges for fill between
    @property
    def block_bins(self):
        return self.double_list(self.bin_edges)[1:-1]
    def add(self, bh1d, inherits=False):
        assert self.shares_bins(bh1d), "Bin alignment error!"
        self.bin_values += bh1d.bin_values
        self.bin_variance += bh1d.bin_variance
        self.sys_up += bh1d.sys_up
        self.sys_down += bh1d.sys_down
        if inherits:
            self.category = bh1d.category
            self.plot_kwargs = bh1d.plot_kwargs
            self.color = bh1d.color
            self.label = bh1d.label
    def divide(self, bh1d):
        assert self.shares_bins(bh1d), "Bin alignment error!"
        denom =  bh1d.bin_values
        self.bin_values = safe_divide(self.bin_values, denom)
        self.bin_std = safe_divide(self.bin_std, denom)
        self.sys_up = safe_divide(self.sys_up, denom)
        self.sys_down = safe_divide(self.sys_down, denom)
    def scale(self,factor):
        self.bin_values = factor*self.bin_values
        self.bin_std = factor*self.bin_std
        self.sys_up = factor*self.sys_up
        self.sys_down = factor*self.sys_down
    def shares_bins(self,bh1d):
        return self.bin_edges == bh1d.bin_edges

if __name__=="__main__":

    bin_edges  = [0,1,2]
    bin_values = [10,-10]
    bin_std    = [3,4]
    sys        = [[11,-8],[9,-10]]
    name       = "test hist"
    kwargs     = {"color":"red","label":"example label"}

    test_hist = basicHistogram1D(name,bin_edges,bin_values=bin_values,bin_std=bin_std,sys_values=sys,plot_kwargs=kwargs)
    test_hist_no_unc = basicHistogram1D(name,bin_edges,bin_values=[-10,10],plot_kwargs={"color":"blue"})
    test_hist_different_size = basicHistogram1D(name,[1,2])

    assert test_hist.bin_edges == [0, 1, 2]
    assert (test_hist.bin_variance == [9,16]).all()
    assert (test_hist.zero_array() == [0.,0.]).all()
    assert (test_hist.sys_up == [1., 2.]).all()
    assert (test_hist.sys_down == [-1.,  0.]).all()
    assert test_hist.bin_center == [0.5, 1.5]
    test_hist.add(test_hist)
    def close_enough(array1,array2,max_delta=1e-10):
        return np.mean(test_hist.bin_variance - [18., 32.])<max_delta
    assert (test_hist.bin_values == [ 20,-20]).all()
    assert close_enough(test_hist.bin_variance,[18., 32.])
    assert close_enough(test_hist.bin_std,[4.24264069, 5.65685425])
    assert close_enough(test_hist.sys_down,[-2.,  0.])

    test_hist.plot(label=True)
    test_hist.plot_sys()
    test_hist_no_unc.plot(kwargs={"histtype":"fill", "alpha":.5})
    test_hist.bin_std, test_hist_no_unc.bin_std
    plt.legend()
    plt.savefig("demo_hist.png")