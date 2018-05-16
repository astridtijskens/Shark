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

# Interior climate model
interior_climate_type = 'EN15026' # Use 'EN15026' or 'EN13788'
# Scenario layer - scenario's
scenario = {'parameter':'int climate', 'value':['a','b']} # currently, only one scenario parameter is supported

# Uncertainty layer - Parameter distributions
distributions = pd.DataFrame([{'parameter':'solar absorption',                          'type':'uniform',       'value':[0.4,0.8]},
                              {'parameter':'ext climate',                               'type':'discrete',      'value':['Oostende','Gent','StHubert','Gaasbeek']},
                              {'parameter':'exterior heat transfer coefficient slope',  'type':'uniform',       'value':[1,4]},
                              {'parameter':'brick material',                            'type':'discrete',      'value':['Brick1','Brick2','Brick3']},
                              {'parameter':'scale factor catch ratio',                  'type':'uniform',       'value':[0,2]},
                              {'parameter':'wall orientation',                          'type':'uniform',       'value':[0,360]},
                              {'parameter':'start year',                                'type':'discrete',      'value':24},
                              {'parameter':'brick dimension',                           'type':'uniform',       'value':[0.2,0.5]},
                              ])

# Change dimensions of building component
buildcomp = [1,17] # [first column/row of building component, last column/row of building component] - assign 'buildcomp = None' if no building components need to be changed
buildcomp_elem = 5 # building component column/row which dimensions needs to be changed and discretised - assign 'buildcomp_elem = None' if no building components need to be changed
dir_cr = 'column' # 'column' if building componentis column, 'row' if building component is row - assign 'dir_cr = None' if no building components need to be changed

# Climate info
number_of_years = 7 # Number of years that need to be extracted from the climate files to perform silumation for full duration
simulate_wdrain = True # If wind driven rain is incluced in the simulations, use True. If wind driven rain is excluced in the simulations, use False (not recommended).

# Sampling details
sampling_strategy = 'sobol' # If load, load raw sampling scheme from .mat file; number of samples is not used
samples_per_set = 24
sets = 3

"""
###############################################################################
# Run - no changes below this line
###############################################################################
"""

import os
from shark import autovar, sampling
import sys

def main():
    if len(buildcomp) !=2 or buildcomp != None:
        print('ERROR: buildcomp has the wrong formatting, this should be [first column/row of building component, last column/row of building component]')
        sys.exit()
    if buildcomp != None and buildcomp_elem == None:
        print('ERROR: buildcomp is defined to change building component dimensions but the corresponding row/column was not defined by buildcomp_elem!')
        sys.exit()
    if buildcomp != None and dir_cr == None:
        print('ERROR: buildcomp is defined to change building component dimensions but the discretisation direction was not defined by dir_cr!')
        sys.exit()
            
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
    if buildcomp != None:
        autovar.main(path, samples, buildcomp={'component':buildcomp, 'cell':buildcomp_elem, 'dir': dir_cr}, number_of_years=number_of_years, intclimType=interior_climate_type, simulRain=simulate_wdrain)
    else:
        autovar.main(path, samples, number_of_years=number_of_years, intclimType=interior_climate_type, simulRain=simulate_wdrain)
    
    print('Done!')

if __name__ == '__main__':
    __spec__ = None
    main()