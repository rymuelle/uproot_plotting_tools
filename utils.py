import numpy as np
import uproot

def get_hist_uproot(uproot_dir, hname, overflow=False):
    hist = uproot_dir[hname] 
    if overflow:
        bins = hist.allbins
        values = hist.allvalues
        var = hist.allvariances
    else:
        bins = hist.bins
        values = hist.values
        var = hist.variances
    return {"bins":bins, "values":values, "var":var}

def hist_integral_and_error(x): return (np.sum(x['values']), np.sum(x['var']) ** .5)

def safe_divide(a,b):
    return np.divide(a, b, out=np.zeros_like(a), where=b!=0)