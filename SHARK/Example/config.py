# -*- coding: utf-8 -*-
"""
Example of how to use shark to for probabilistic Monte-Carlo simulations with DELPHIN 5.8.
===============================================================================
2017-12-05

In this script, you first have to define the parameter distributions, as are all the 
other variables needed for the probabilistic assessment. 

Next, the script automatically samples the given parameter distributions according 
to the specified sampling strategy. The parameter values of the original Delphin 
files are edited using these samples. Finally, the edited Delphin files are then 
saved as new variation Delphin files for simulation.
Simulation is done by the script run.py.
"""

import pandas as pd

# Scenario layer - scenario's
interior_climate_type = 'EN15026' # Use 'EN15026' or 'EN13788'
scenario = {'parameter':'int climate', 'value':['a','b']} # currently, only one scenario is supported

# Uncertainty layer - Parameter distributions
distributions = pd.DataFrame([{'parameter':'solar absorption',                          'type':'uniform',       'value':[0.4,0.8]},
                              {'parameter':'ext climate',                               'type':'discrete',      'value':['Oostende','Gent','StHubert','Gaasbeek']},
                              {'parameter':'exterior heat transfer coefficient slope',  'type':'uniform',       'value':[1,8]},
                              {'parameter':'brick material',                            'type':'discrete',      'value':['Brick1','Brick2','Brick3']},
                              {'parameter':'scale factor catch ratio',                  'type':'uniform',       'value':[0,1.5]},
                              {'parameter':'wall orientation',                          'type':'uniform',       'value':[0,360]},
                              {'parameter':'start year',                                'type':'discrete',      'value':24},
                              {'parameter':'brick dimension',                           'type':'uniform',       'value':[0.15,0.5]},
                              ])
# Scenario layer - scenario's
scenario = {'parameter':'int climate', 'value':['a','b']} # currently, only one scenario is supported

# Sampling details
sampling_strategy = 'sobol' # If load, load raw sampling scheme from .mat file; number of samples is not used
samples_per_set = 18
sets = 3

# Climate info
number_of_years = 7 # Number of years that need to be extracted from the climate files to perform silumation for full duration
simulate_wdrain = True # If wind driven rain is incluced in the simulations, use True. If wind driven rain is excluced in the simulations, use False (not recommended).

# Change dimensions of building component
buildcomp = [1,17] # [first column/row of building component, last column/row of building component]
buildcomp_elem = 5 # building component column/row which dimensions needs to be changed and discretised
dir_cr = 'column' # 'column' if building componentis column, 'row' if building component is row

"""
###############################################################################
# Run - no changes below this line
###############################################################################
"""

import os
from shark import autovar, sampling

def main():
    path = {}
    # read project file path
    path['project'] = os.path.dirname(__file__)
    # read samples path
    path['samples'] = os.path.join(path['project'], 'Sampling scheme')
    
    #Generate samples
    
    print('Sampling parameter distributions')
    
    samples = sampling.main(scenario=scenario, dist=distributions, runs=samples_per_set, sets=sets, strat=sampling_strategy, path=path['samples'])
    
    #Run
    print('Running Automated Parameter Variation Delphin script')
    
    # Compact information about building component
    bc = {'component':buildcomp, 'cell':buildcomp_elem, 'dir': dir_cr}
    autovar.main(path, samples, buildcomp=bc, number_of_years=number_of_years, intclimType=interior_climate_type, simulRain=True)
    
    print('Done!')

if __name__ == '__main__':
    __spec__ = None
    main()