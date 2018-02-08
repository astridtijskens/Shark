# -*- coding: utf-8 -*-
"""
Created on Wed Nov 22 16:14:23 2017

@author: Astrid
"""
import os
import scipy.io as sio
import numpy as np
import pandas as pd
import sys
from scipy.stats import norm
from scipy.stats import randint
from scipy.stats import uniform
from shark import sobol_lib

def sobol(m, dim, sets=1):
    design = np.empty([0,dim])
    for i in range(sets):
        d = sobol_lib.scrambled_sobol_generate(k=dim, N=m, skip=2, leap=0)
        design = np.vstack((design,d))
    return design

def main(scenario, dist, runs, sets, strat, path):
    if strat == 'load':
        # load file
        file = os.path.join(path,'samples_raw.mat')
        samples_mat = sio.loadmat(file)['design']
        samples_raw = np.empty((0,dist.shape[0]))
        for i in range(samples_mat.shape[1]):
            samples_raw = np.vstack((samples_raw,samples_mat[:,i].tolist()[0]))
    else:
        # create raw sampling scheme
        if strat == 'sobol':
            samples_raw = sobol(m=runs, dim=dist.shape[0],sets=sets)
        else:
            print('''Error: This sampling strategy is not supperted. Currently only 'sobol' and 'load' are implemented.''')
    # Add keys to dictionary
    samples = pd.DataFrame({})
    samples[scenario['parameter']] = []
    for p in dist['parameter']:
        samples[p] = []
    # Add samples to dictionary
    for s in scenario['value']:
        sdf = pd.DataFrame({})
        sdf[scenario['parameter']] = [s]*samples_raw.shape[0]
        for i in range(dist.shape[0]):
            dist_type = dist.get_value(i, 'type')
            x = samples_raw[:,i]
            if dist_type == 'discrete':
                p1 = dist.get_value(i, 'value')
                if isinstance(p1, int): 
                    high = p1+1
                    values = randint.ppf(x, low=1, high=high).tolist()
                else: 
                    high = len(p1)-1
                    values = randint.ppf(x, low=0, high=high).tolist()
                    values = [p1[int(x)] for x in values]
                sdf[dist.get_value(i, 'parameter')] = values
            elif dist_type == 'uniform':
                p1 = dist.get_value(i, 'value')[0]
                p2 = dist.get_value(i, 'value')[1]
                values = uniform.ppf(x, loc=p1, scale=p2-p1).tolist()
                sdf[dist.get_value(i, 'parameter')] = values
            elif dist_type == 'normal':
                p1 = dist.get_value(i, 'value')[0]
                p2 = dist.get_value(i, 'value')[1]
                values = norm.ppf(x, loc=p1, scale=p2).tolist()
                sdf[dist.get_value(i, 'parameter')] = values
            else:
                print('ERROR: distribution type not supported')
                sys.exit()
        samples = samples.append(sdf, ignore_index=True)
    # Save samples
    samples.to_excel(os.path.join(path,'samples.xlsx'))
    samples.to_pickle(os.path.join(path,'samples'))
    return samples
