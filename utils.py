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

def average_list_pairs(l_list): return [(l_list[i] + l_list[i+1])/2 for i in range(len(l_list)-1)]


def abcd_template(titles, yscale="linear",bottom=1):
    import matplotlib
    import matplotlib.pyplot as plt
    import mplhep as hep
    hep.set_style(hep.style.ROOT)

    fig = plt.figure(constrained_layout=True, figsize=(10,16))
    gs = fig.add_gridspec(10, 2)
    ax = []
    ax.append([fig.add_subplot(gs[0:3,0]), fig.add_subplot(gs[3,0])])
    ax[0][0].set_title(titles[0])
    ax[0][1].set_ylim(0,2)

    ax.append([fig.add_subplot(gs[0:3,1],sharey=ax[0][0]), fig.add_subplot(gs[3,1])])
    ax[1][0].set_title(titles[1])
    ax[1][1].set_ylim(0,2)

    ax.append([fig.add_subplot(gs[4:7,0],sharey=ax[0][0]), fig.add_subplot(gs[7,0])])
    ax[2][0].set_title(titles[2])
    ax[2][1].set_ylim(0,2)

    ax.append([fig.add_subplot(gs[4:7,1],sharey=ax[0][0]), fig.add_subplot(gs[7,1])])
    ax[3][0].set_title(titles[3])
    ax[3][1].set_ylim(0,2)

    for axis in ax:
        axis[0].set_yscale(yscale)

    return fig, ax

def log_norm(x, norm, sigma, theta, mean,slope):
    theta  = min(theta,140)
    return norm/((x-theta)*sigma*2*3.14159)*np.exp(-(np.log((x-theta)/mean))**2/(2*sigma**2))*(slope*x)

def log_norm_unc(x, norm, sigma, theta, mean,slope):
    from uncertainties import unumpy
    from uncertainties import ufloat
    import uncertainties
    theta  = min(theta,140)
    return norm/((x-theta)*sigma*2*3.14159)*unumpy.exp(-(unumpy.log((x-theta)/mean))**2/(2*sigma**2))*(slope*x)


    
def make_band_plot(unc_array): 
    from uncertainties import unumpy
    from uncertainties import ufloat
    import uncertainties
    y = unumpy.nominal_values(unc_array)
    y_err = unumpy.std_devs(unc_array)
    return (y - y_err, y + y_err), y, y_err