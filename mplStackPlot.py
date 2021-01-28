class mplStackPlot:
    def __init__(self,name, bh1d_list=[],blinded=True):
        self.name = name
        self.n_hists = len(bh1d_list)
        self.bin_edges = bh1d_list[0].bin_edges
        self.n_bins = bh1d_list[0].n_bins
        self.bh1d_list = bh1d_list
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
        print(mask)
        print( [bh1d.label for bh1d in self.bh1d_list])
        return self.return_hist_stack("",mask)
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