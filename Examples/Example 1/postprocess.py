# -*- coding: utf-8 -*-
"""
Example of how to use shark to for probabilistic Monte-Carlo simulations with DELPHIN 5.8.
===============================================================================
2017-12-05

This script is an example of how to use the dpm module of shark for postprocessing 
the Delphin output with damage prediction models (dpm).
First the output of the Delphin simulations is read into Python.
Next, the output is processed by the desired damage prediction model.

Postprocessing of the output is very project specific. Hence, this script only 
serves as an example, and does not show all postprocessing possibilities.
"""

from shark import supp, dpm
import os
import pandas as pd

def main():
    path = {}
    
    # Load samples
    path['samples'] = os.path.join(os.path.dirname(__file__), 'Sampling scheme')
    samples = pd.read_pickle(os.path.join(path['samples'], 'samples'))
    
    # Read all output files
    path['output'] = os.path.join(os.path.dirname(__file__), 'Delphin files', 'Output')
    output, geometry, elements = supp.readOutput(path['output'])
    
    # Perform postprocessing - damage prediction
    damage = pd.DataFrame()
    damage['index'] = output.index.values
    damage = damage.set_index('index')
    
    # Frost damage - moist freeze-thaw cycles DTU equatiuon
    frost = list()
    col = 0 # column of output to use
    wperc = 0.25 #☺ critical degree of saturation
    for ind,row in output.iterrows():
    #    i,j = int(ind.split('_')[0]), int(ind.split('_')[1])
        T = list(row['temperature'][:,col])[1:]
        RH = list(row['relhum'][:,col])[1:]
        W = list(row['freeze_sat_degree'])[1:]
        ft = dpm.freezeThawCyclesDTU(T, RH, W, wperc)[0] # freeze-thaw cycles
        mft = dpm.freezeThawCyclesDTU(T, RH, W, wperc)[1] # moist freeze-thaw cycles
        frost.append(mft)
    damage['frost'] = frost
    
    # Mould growth - VTT mould model
    # Interior surface
    MI_surf = list()
    col = 3 # column of output to use
    sens_class='vs' # sensitivity class
    for ind,row in output.iterrows():
        T = list(row['temperature'][:,col])[1:]
        RH = list(row['relhum'][:,col])[1:]
        mi = dpm.mouldVTTupdate(T, RH, sens_class, C_eff=1)
        MI_surf.append(mi)
    damage['mould index surface'] = MI_surf
    # Interface masonry - insulation
    MI_interf = list()
    col = 2 # column of output to use
    sens_class='mr' # sensitivity class
    for ind,row in output.iterrows():
        T = list(row['temperature'][:,col])[1:]
        RH = list(row['relhum'][:,col])[1:]
        mi = dpm.mouldVTTupdate(T, RH, sens_class, C_eff=1)
        MI_interf.append(mi)
    damage['mould index interface'] = MI_interf
    # Wooden beam ends
    MI_beam = list()
    col = 1 # column of output to use
    sens_class='vs' # sensitivity class
    for ind,row in output.iterrows():
        T = list(row['temperature'][:,col])[1:]
        RH = list(row['relhum'][:,col])[1:]
        mi = dpm.mouldVTTupdate(T, RH, sens_class, C_eff=1)
        MI_beam.append(mi)
    damage['mould index beam'] = MI_beam
    
    # Wood decay - VTT wood decay model - mass loss
    # Wooden beam ends
    ML_beam = list()
    col = 1 # column of output to use
    for ind,row in output.iterrows():
        T = list(row['temperature'][:,col])[1:]
        RH = list(row['relhum'][:,col])[1:]
        ml = dpm.woodDecayVTT(T, RH)
        ML_beam.append(ml)
    damage['wood mass loss beam'] = ML_beam

"""Protect main code when using multiprocessing (supp.readOuptut())"""
if __name__ == '__main__':
    __spec__ = None
    main()