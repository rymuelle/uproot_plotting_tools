from uproot_plotting_tools.basicHistStack import basicHistStack
import numpy as np
import matplotlib.pyplot as plt
import mplhep as hep

class mplStackPlot:
    def __init__(self,name,bin_edges,y_list,y_list_var=[],y_list_sys=[],labels=[],colors=[]):
        self.name = name
        self.bin_edges = bin_edges
        self.nBins = len(bin_edges)-1
        self.y_list = np.asarray(y_list)
        self.y_list_var = np.asarray(y_list_var)
        self.y_list_sys = np.asarray(y_list_sys)
        self.labels = list(labels)
        self.colors = list(colors)
        self.y_sum = np.sum(y_list,axis=0)
        self.y_sum_var = np.sum(y_list_var,axis=0)
        self.y_sum_list_sys = np.sum(y_list_sys,axis=0)
    @classmethod
    def from_basic_hist_stack_label(cls,hist_stack,label):
        value_list, var_list, sys_list, plotting_kwargs_list = hist_stack.return_type(label)
        colors = [x['color'] for x in plotting_kwargs_list ]
        labels = [x['label'] for x in plotting_kwargs_list ]
        args = [hist_stack.name, hist_stack.bin_edges, value_list]
        kwargs = {"y_list_var":var_list, "y_list_sys":sys_list,"labels":labels,"colors":colors}
        return cls(*args,**kwargs)        
    @property
    def y_list_std(self):
        return self.y_list_var ** .5
    @property
    def bin_center(self):
        return [(self.bin_edges[i]+self.bin_edges[i+1])/2. for i in range(self.nBins)]
    @property
    def y_list_std_sum(self):
        return np.sum(self.y_list_var,axis=0) ** .5
    def histplot(self,kwargs,draw_sys=False):
        args = [
            self.y_list,
            self.bin_edges 
        ]
        kwargs_l ={
            "color":self.colors,
            "label":self.labels
        }
        hep.histplot(*args, **kwargs_l, **kwargs)
        if draw_sys:
            if 'stack' in kwargs:
                if kwargs['stack']:
                    plt.fill_between(self.bin_center,self.y_sum_list_sys[0]+self.y_sum,self.y_sum_list_sys[1]+self.y_sum, alpha=.5,color='grey') 
            else:
                for nom,sys,col in zip(self.y_list,self.y_list_sys,self.colors):
                    plt.fill_between(self.bin_center,sys[0]+nom,sys[1]+nom, alpha=.5,color=col)
        plt.legend()