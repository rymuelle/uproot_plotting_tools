import numpy as np
import uproot
from uproot_plotting_tools.utils import get_hist_uproot, hist_integral_and_error

class basic_hist_stack:
    def __init__(self,name,td_dict={},sys_list=[],blinded=True):
        self.SR = 'SR' in name
        self.name = name
        self.hcat = {}
        self.blinded = blinded
        if td_dict: self.add_from_dict(td_dict,sys_list=sys_list)
    def zero_array(self):
        return np.full(self.nBins,0.)
    def add_from_dict(self, td_dict, sys_list=[]):
        for i, td_string in enumerate(td_dict):
            td = td_dict[td_string]['td']
            type_string = td_dict[td_string]['type']
            label  = td_dict[td_string]['label']
            kwargs  = td_dict[td_string]['kwargs']
            # get nominal hist and set bins
            hist = get_hist_uproot(td, self.name)
            if i == 0: self.set_bins(hist['bins'])
            # don't fill data in SR if blinded, don't look for weights for data
            if self.SR and self.blinded and 'data' in type_string:
                        continue
            if "nominal" not in type_string and 'data' in type_string:
                        continue
            if '_W_' in type_string and 'data' in type_string:
                        continue
            #sys placeholder arrays
            sys_up = self.zero_array()
            sys_down = self.zero_array()
            if sys_list and not 'data' in type_string:
                for sys in sys_list:
                    sys_temp = get_hist_uproot(td, sys)
                    sys_delta = np.subtract(sys_temp['values'], hist['values'])
                    sys_delta_sum = np.sum(sys_delta)
                    if sys_delta_sum>0: sys_up += sys_delta
                    if sys_delta_sum<0: sys_down += sys_delta
            sys_array_list = [sys_down,sys_up]
            self.add(type_string,label,hist,sys_array_list=sys_array_list,kwargs=kwargs)
    def set_bins(self,bins):
        self.bins = bins
        self.bin_centers = np.asarray([(low+high)/2 for low,high in self.bins])
        self.nBins = len(self.bins)
    def add(self,type_string,hlabel,hist,sys_array_list=[],kwargs={}):
        bins,values,var = hist['bins'],hist['values'],hist['var']
        nBins = len(bins)
        if nBins != self.nBins: 
            print("wrong lenght")
            return 0
        if type_string not in self.hcat:  self.hcat[type_string] = {}
        if hlabel not in self.hcat[type_string]:
            self.hcat[type_string][hlabel] = {}
            self.hcat[type_string][hlabel]['kwargs'] = kwargs
            self.hcat[type_string][hlabel]['values'] = self.zero_array()
            self.hcat[type_string][hlabel]['var'] = self.zero_array()
            self.hcat[type_string][hlabel]['sys'] = {}
            self.hcat[type_string][hlabel]['sys']['down'] = self.zero_array()
            self.hcat[type_string][hlabel]['sys']['up'] = self.zero_array()
        self.hcat[type_string][hlabel]['values'] += values
        self.hcat[type_string][hlabel]['var'] += var   
        if len(sys_array_list)==2: 
            self.hcat[type_string][hlabel]['sys']['down'] += sys_array_list[0]
            self.hcat[type_string][hlabel]['sys']['up'] += sys_array_list[1]
    def print_summary(self):
        for hcat in self.hcat:
            print(hcat)
            for hlabel in self.hcat[hcat]:
                print("\t",hlabel)
                total_events = np.sum(self.hcat[hcat][hlabel]['values'])
                variance = np.sum(self.hcat[hcat][hlabel]['var'])
                std = variance ** .5
                print("\t\t nEvents: {:.2f}, std: {:.2f}".format(total_events,std) )
    def return_type(self,type_string):
        if not type_string in self.hcat: return 0
        value_list = []
        var_list = []
        sys_list = []
        kwarg_list = []
        for hlabel in self.hcat[type_string]:
            values = np.asarray(self.hcat[type_string][hlabel]['values'])
            var = np.asarray(self.hcat[type_string][hlabel]['var'])
            value_list.append(values)
            var_list.append(var)
            kwarg_list.append(self.hcat[type_string][hlabel]['kwargs'])
            if 'sys' in self.hcat[type_string][hlabel]:
                temp_sys_down = np.asarray(self.hcat[type_string][hlabel]['sys']['down'])
                temp_sys_up = np.asarray(self.hcat[type_string][hlabel]['sys']['up'])
                sys_list.append([temp_sys_down,temp_sys_up])
        return value_list, var_list, sys_list, kwarg_list
    def return_sum_type(self,type_string):
        value_list, var_list, sys_list, kwarg_list = self.return_type(type_string)
        value_list = np.sum(value_list,axis=0)
        var_list = np.sum(var_list,axis=0)
        sys_list = np.sum(sys_list,axis=0)
        std_list = var_list ** .5
        return value_list, std_list,[sys_list[0]+value_list,sys_list[1]+value_list]
     
    