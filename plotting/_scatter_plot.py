from __future__ import print_function

# Copyright (c) 2011, Roger Lew [see LICENSE.txt]

# Python 2 to 3 workarounds
import sys
if sys.version_info[0] == 2:
    _strobj = basestring
    _xrange = xrange
elif sys.version_info[0] == 3:
    _strobj = str
    _xrange = range

import os

from matplotlib import pyplot as plt
import numpy as np

from pyvter.plotting.support import \
     _bivariate_trend_fit, _tick_formatter, _subplots

def scatter_plot(df, aname, bname, where=None, trend=None,
                 fname=None, output_dir='',
                 quality='medium', alpha=0.6):
    """
    Creates a scatter plot with the specified parameters

       args:
          aname: variable on x-axis
          
          bname: variable on y-axis
             
       kwds:
          alpha:
             amount of transparency applied
    
          trend :
             None:          no model fitting
        
             'linear':      f(x) = a + b*x
        
             'exponential': f(x) = a * x**b
        
             'logarithmic': f(x) = a * log(x) + b
        
             'polynomial':  f(x) = a * x**2 + b*x + c
        
             'power':       f(x) = a * x**b
    """
    
    if where == None:
        where = []

    # check fname
    if not isinstance(fname, _strobj) and fname != None:
        raise TypeError('fname must be None or string')

    if isinstance(fname, _strobj):
        if not (fname.lower().endswith('.png') or \
                fname.lower().endswith('.svg')):
            raise Exception('fname must end with .png or .svg')                

    # select_col does checking of aname, bnames, and where        
    adata = df.select_col(aname, where)
    bdata = df.select_col(bname, where)

    # figure out the limits for the plot
    # I want 5 ticks for both the x and y axis
    amin,amax = min(adata),max(adata)
    arange = amax-amin
    xticks = np.linspace(amin, amax, 5)
    xlim = [amin - .1*arange, amax + .1*arange]
    
    bmin,bmax = min(bdata),max(bdata)
    brange = bmax-bmin
    yticks = np.linspace(bmin, bmax, 5)
    ylim = [bmin - .1*brange, bmax + .1*brange]

    # initialize the figure
    fig=plt.figure(figsize=(4,4))
    plt.subplots_adjust(left=.2, bottom=.2, top=.95, right=.95)

    # make the scatter plot
    plt.scatter(adata, bdata, alpha=alpha)

    # format stuff
    plt.xticks(xticks, _tick_formatter(xticks),rotation=30)
    plt.yticks(yticks, _tick_formatter(yticks))
    plt.xlim(xlim)
    plt.ylim(ylim)
    plt.xlabel(aname)
    plt.ylabel(bname)

    # perform trend fit if requested
    if trend in ['exponential','linear','logarithmic',
                 'log','polynomial','power']:

        trend_dict = _bivariate_trend_fit(adata,bdata,trend)
        model = trend_dict['model']
        model_str = model.__doc__
        tex_str = model_str + '\n' + r'$R^{2}=%.04f$'%trend_dict['r2']

        # plot fit
        ind = np.linspace(xlim[0], xlim[1], 1000)  
        plt.plot(ind, model(ind), alpha=.8)                        
        plt.text(xticks[0], yticks[-1],
                   tex_str,
                   horizontalalignment='left',
                   verticalalignment='top',
                   fontsize=11)

    if fname == None:
        fname = 'scatter(%s_X_%s'%(aname,bname)
        if trend != None:
            fname += ',trend=' + trend
        fname += ').png'

    fname = os.path.join(output_dir, fname)

    # save figure
    if quality == 'low' or fname.endswith('.svg'):
        plt.savefig(fname)
        
    elif quality == 'medium':
        plt.savefig(fname, dpi=200)
        
    elif quality == 'high':
        plt.savefig(fname, dpi=300)
        
    else:
        plt.savefig(fname)

    plt.close()

    if df.TESTMODE:
        # build and return test dictionary
        return {'aname':aname, 'bname':bname, 'fname':fname, 'trend':trend}
