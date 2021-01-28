import sys
sys.path.append('./src')
from uproot_plotting_tools.basicHistogram1D import basicHistogram1D
from uproot_plotting_tools.utils import safe_divide
import numpy as np
import matplotlib
matplotlib.rcParams['text.usetex'] = True
import matplotlib.pyplot as plt
import mplhep as hep


class mplStackPlot:
    def __init__(self,name, bh1d_list=[],blinded=True, label=""):
        self.name = name
        self.n_hists = len(bh1d_list)
        self.bin_edges = bh1d_list[0].bin_edges
        self.n_bins = bh1d_list[0].n_bins
        self.bh1d_list = bh1d_list
        self.label = label
        assert self.all_bins_match(), "All bins must match!"
    def all_bins_match(self):
        return np.asarray([self.bh1d_list[0].shares_bins( self.bh1d_list[i+1]) for i in range(self.n_hists-1)]).all()
    def return_hist_stack(self,name,hist_mask,plot_kwargs={},category=None):
        _temp_bh1d = basicHistogram1D("",self.bin_edges,plot_kwargs=plot_kwargs,category=category)
        for mask, bh1d in zip(hist_mask,self.bh1d_list):
            if mask: _temp_bh1d.add(bh1d, inherits=True)
        return _temp_bh1d
    def return_hist_by_label(self, label):
        mask = [label==bh1d.label for bh1d in self.bh1d_list]
        return self.return_hist_stack("",mask)
    def category_mask(self,category):
        return [category==bh1d.category for bh1d in self.bh1d_list]
    def return_hist_by_category(self, category):
        mask = self.category_mask(category)
        return self.return_hist_stack("",mask)
    def unique_labels(self, mask=[]):
        return np.unique([bh1d.label for bh1d,m in zip(self.bh1d_list,mask) if m])
    def return_label_stack_by_category(self,category):
        mask = self.category_mask(category)
        stack = []
        for label in self.unique_labels(mask):
            bh1d = self.return_hist_by_label(label)
            stack.append(bh1d)
        return stack
    def plot_stack_by_category(self, category,kwargs={}):
        #sum of hists
        bh1d_list = self.return_label_stack_by_category(category)
        bh1d_list = sorted(bh1d_list,key=lambda x: x.sum_and_error()[0])
        values = [bh1d.bin_values for bh1d in bh1d_list]
        colors = [bh1d.color for bh1d in bh1d_list]
        labels = [bh1d.label for bh1d in bh1d_list]
        hep.histplot(values, self.bin_edges,color=colors,label=labels,**kwargs)  
    def make_stack_ratio_plot(self,yscale="log",y_lim=10e2):
        figsize = np.asarray([10,12])*1.5
        f, axs = plt.subplots(2,1, sharex=True, gridspec_kw={'height_ratios':[4,1]},figsize=figsize)
        bin_edges = self.bin_edges
        
        #metadata:
        axs[0].set_ylabel('Events')
        axs[0].set_ylim([1,y_lim])
        axs[0].set_yscale(yscale)
        axs[1].set_xlabel(self.label,horizontalalignment='center')
        
        #top plot
        kwargs = {"histtype":"fill","stack":True, "ax":axs[0]}
        self.plot_stack_by_category("background",kwargs=kwargs)
        sum_bck = self.return_hist_by_category("background")
        sum_bck.plot(kwargs={"color":"black", "ax":axs[0]})
        sum_bck.plot_sys(kwargs={"color":"blue", "ax":axs[0]})
    
        self.plot_stack_by_category("signal",kwargs={"ax":axs[0]})
    
        sum_data = self.return_hist_by_category("data")
        axs[0].errorbar(sum_data.bin_center,sum_data.bin_values,yerr=sum_data.bin_std, linestyle="", marker=".", color="black", label="data")
        axs[0].legend()
            
        #ratio:
        axs[1].set_ylim([0,2])
        ratio_data = basicHistogram1D("ratio_data",bin_edges)
        ratio_data.add(sum_data)
        ratio_data.divide(sum_bck)
        axs[1].errorbar(ratio_data.bin_center,ratio_data.bin_values,yerr=ratio_data.bin_std, linestyle="", marker="o", color="black", label="data")   
        
        blk_values = sum_bck.double_list(sum_bck.bin_values)
        blk_std = safe_divide(sum_bck.double_list(sum_bck.bin_std),blk_values)
        sys_up = safe_divide(sum_bck.double_list(sum_bck.sys_up),blk_values) + 1
        sys_down = safe_divide(sum_bck.double_list(sum_bck.sys_down),blk_values) +1
        
        block_bin = sum_bck.block_bins
        axs[1].fill_between(block_bin,sys_up,sys_down, color='blue', alpha=.25)
        axs[1].fill_between(block_bin,blk_std+1,1-blk_std, color='black', alpha=.25)
        return f,axs