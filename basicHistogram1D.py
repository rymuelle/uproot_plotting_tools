import matplotlib
matplotlib.rcParams['text.usetex'] = True
import matplotlib.pyplot as plt
import mplhep as hep
import numpy as np
import uproot

# no overflow
# systematics are sorted based on net negative or positive to down/up
# systematics are added linearly
# systematic histograms are assumed to be non relative to nom value
class basicHistogram1D:
    def __init__(self,name,bin_edges,bin_values=[],bin_std=[],sys_values=[],plot_kwargs={}):
        self.name = name
        self.plot_kwargs = plot_kwargs
        if 'color' in self.plot_kwargs:
            self.color = self.plot_kwargs['color']
        else:
            self.color = 'black'
        self.bin_edges = bin_edges
        self.n_bins = len(bin_edges) - 1
        #set bin values
        if bin_values: 
            assert (len(bin_values) == self.n_bins), "Bin values must have same length as bins!"
            self.bin_values = np.asarray(bin_values)
        else: self.bin_values = self.zero_array()
        #set bin standard deviation
        if bin_std: 
            assert (len(bin_std) == self.n_bins), "Bin std must have same length as bins!"
            self.bin_std = np.asarray(bin_std)
        else: self.bin_std = self.zero_array()
        self.has_sys = bool(sys_values)
        #only computer systematics if bin has set values
        if bin_values and self.has_sys:
            self.sys_up = self.zero_array()
            self.sys_down = self.zero_array()
            for sys in sys_values:
                self.add_sys(sys)
    @classmethod
    def from_uproot(name,uproot_hist,uproot_sys=[],plot_kwargs={}):
        bins,values,std = self.get_hist_uproot(uproot_hist)
        sys_list = []
        for sys in uproot_sys:
            _,sys_value,_ = self.get_hist_uproot(uproot_hist)
            sys_list.append(sys_value)
        return cls(name,bin_edges,bin_values=values,bin_std=std,sys_hists=sys_list,plot_kwargs=plot_kwargs)
    @property
    def bin_variance(self):
        return self.bin_std ** 2
    @bin_variance.setter
    def bin_variance(self,var):
        self.bin_std = var ** .5
    @property
    def bin_center(self):
        return [(self.bin_edges[i]+self.bin_edges[i+1])/2. for i in range(self.n_bins)]
    def add_sys(self,sys_values):
        sys_array = np.asarray(sys_values)
        sys_delta = sys_array - self.bin_values
        if np.sum(sys_delta)>0: self.sys_up += sys_delta
        else: self.sys_down += sys_delta
        self.has_sys = True
    def zero_array(self):
        return  np.full(self.n_bins,0.)   
    def get_hist_uproot(self,uproot_hist):
        hist = uproot_dir[hname] 
        bins = hist.bins
        bin_edges = [bins[i][0] for i in range(len(bins)-1)] #converts from 2D list to 1D edges list
        values = hist.values
        var = hist.variances
        std = var ** .5
        return bins, values, std
    def hist_sum_and_error(self): 
        return np.sum(self.bin_values), np.sum(self.bin_variance) ** .5
    def plot(self,kwargs={},error_bars=True, draw_sys=True):
        args = [self.bin_values,self.bin_edges]
        if error_bars: self.plot_kwargs['yerr'] = self.bin_std
        hep.histplot(*args, **self.plot_kwargs, **kwargs)    
        if self.has_sys and draw_sys:
            self.sys_up_block = self.double_list(self.sys_up+self.bin_values)
            self.sys_down_block = self.double_list(self.sys_down+self.bin_values)
            plt.fill_between(self.block_bins,self.sys_up_block,self.sys_down_block, alpha=.3,color=self.color)
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
    def add(self,bh1d):
        assert self.bin_edges == bh1d.bin_edges, "Bin alignment error!"
        self.bin_values += bh1d.bin_values
        self.bin_variance += bh1d.bin_variance
        self.sys_up += bh1d.sys_up
        self.sys_down += bh1d.sys_down

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

    test_hist.plot()
    test_hist_no_unc.plot(kwargs={"histtype":"fill", "alpha":.5})
    test_hist.bin_std, test_hist_no_unc.bin_std
    plt.legend()
    plt.savefig("demo_hist.png")