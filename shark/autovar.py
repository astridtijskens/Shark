# -*- coding: utf-8 -*-
"""
Created on Mon Nov 13 12:12:11 2017

@author: Astrid
"""

from shark import supp, climateFun, changeDPJ
import os
import sys
import multiprocessing

def calcClim(args):
    path, sample, j, years, intclimType, simulRain = args
    # Exterior climate
    if 'start year' in sample:
        climateFun.extractClimateYears(path_climate=os.path.join(path['climate data'],sample.loc['ext climate']), year_start=sample.loc['start year'], years=years, number=j+1, path_save=path['ext climate'], exclude=['CloudCover','GlobalRadiation','TerrainCounterRadiation','TotalPressure'])
    else:
        climateFun.extractClimateYears(path_climate=os.path.join(path['climate data'],sample.loc['ext climate']), year_start=1, years=years, number=j+1, path_save=path['ext climate'], exclude=['CloudCover','GlobalRadiation','TerrainCounterRadiation','TotalPressure'])
    # Interior climate
    if intclimType == 'EN15026':
        climateFun.calcIntClimateEN15026(path_climate=os.path.join(path['ext climate'], '%03i_' %(j+1)), load=sample.loc['int climate'], number=j+1, path_save=path['int climate'])
    elif intclimType == 'EN13788':
        climateFun.calcIntClimateEN13788(path_climate=os.path.join(path['ext climate'], '%03i_' %(j+1)), load=sample.loc['int climate'], number=j+1, path_save=path['int climate'])
    else:
        print('Error: climate type not supported, use EN15026 or EN13788 instead')
    # Rain
    if simulRain:
        climateFun.calcRainLoad(path_climate=os.path.join(path['ext climate'], '%03i_' %(j+1)), ori=sample.loc['wall orientation'], number=j+1, path_save=path['ext climate'])
    print('Created climates for sample ' + str(j+1))

def varParam(args):
    dpj_file_new, dpj_lines, assignments, sample, path, buildcomp, x_discr, y_discr, i, j = args
    # Exterior climate file, incl. path
    ext_climate_file = os.path.join(path['ext climate'], '%03i_' %(j+1))
    sample.set_value('ext climate',ext_climate_file)
    # Interio climate file, incl. path
    int_climate_file = os.path.join(path['int climate'], '%03i_' %(j+1))
    sample.set_value('int climate',int_climate_file)
    
    # Change parameters
    dpj_file_new = changeDPJ.cParameter(file=dpj_file_new, lines=dpj_lines, values=sample)
    # Change interior and exterior climate
    dpj_file_new = changeDPJ.cClimate(file=dpj_file_new, lines=dpj_lines, values=sample)
    # Change output files
    dpj_file_new = changeDPJ.cOutput(file=dpj_file_new, lines=dpj_lines, value='%03i-%03i' %(i, j+1), path=path['output'], assignments=assignments)
    # Change X-discretisation
    if buildcomp != None:
        bc = [buildcomp['component'][0], buildcomp['cell'], buildcomp['component'][1]]
        if buildcomp['dir'] == 'column':
            dpj_file_new = changeDPJ.cDiscretisation(file=dpj_file_new, lines=dpj_lines, values=sample, steps_change=x_discr, steps_keep=y_discr, col=bc, assignments=assignments)
        elif buildcomp['dir'] == 'row':
            dpj_file_new = changeDPJ.cDiscretisation(file=dpj_file_new, lines=dpj_lines, values=sample, steps_change=y_discr, steps_keep=x_discr, col=bc, assignments=assignments, Xdir=False)
    # Change materials
    dpj_file_new = changeDPJ.cMaterial(file=dpj_file_new, values=sample, assignments=assignments)
    
    # Save file
    file_save = os.path.join(path['variations'], 'Option_%03d-%03d.dpj' % (i,j+1))
    fileobj = open(file_save, 'w', encoding='utf8')
    fileobj.writelines(dpj_file_new)
    fileobj.close()
    del fileobj, dpj_file_new
    print('Created Option_%03d-%03d.dpj' % (i,j+1))

def main(path, samples, buildcomp=None, number_of_years=1, intclimType=None, simulRain=True):
    # Directories
    # Load climate directory
    with open(os.path.join(os.path.dirname(__file__), 'data', 'dir_ext_clim.txt'), 'r') as f: path['climate data'] = f.readline()
    #Create list of DELPHIN files that need to be read, auto variated and calculated
    path['delphin folder'] = os.path.join(path['project'], 'DELPHIN files') #Folder including subfolders with files needed for the the Delphin calculations
    path['design options'] = os.path.join(path['delphin folder'], 'Originals') #Folder with the original Delphin files = manually created design options
    design_options = {}
    design_options['list'], design_options['path list'] = supp.getFileList(path['design options'], '.dpj') #Create list of all original Delphin files
    # interior climate
    path['int climate'] = os.path.join(path['delphin folder'], 'Interior Climate')
    if not os.path.exists(path['int climate']):
        os.mkdir(path['int climate'])
    # exterior climate
    path['ext climate'] = os.path.join(path['delphin folder'], 'Exterior Climate')
    if not os.path.exists(path['ext climate']):
        os.mkdir(path['ext climate'])
    # variations folder
    path['variations'] = os.path.join(path['delphin folder'], 'Variations')
    if not os.path.exists(path['variations']):
        os.mkdir(path['variations'])
    # output folder
    path['output'] = os.path.join(path['delphin folder'], 'Output')
    if not os.path.exists(path['output']):
        os.mkdir(path['output'])
    
    # Parrallel pool setting
    num_cores = multiprocessing.cpu_count()-1
    pool = multiprocessing.Pool(num_cores)
    
    ###########################################################################
    # Warning climate
    if intclimType == 'constant':
        print('ERROR: Constant interior climate is not yet implemented, use EN15026 or EN13788 instead.')
        sys.exit()
    if not simulRain:
        print('WARNING: Wind driven rain is not calculated, are you sure?')
    
    # Calculate climate
    arg_pairs = [(path, samples.iloc[j], j, number_of_years, intclimType, simulRain) for j in range(samples.shape[0])]
#    for j in range(samples.shape[0]):
#        calcClim(arg_pairs[j])
    pool.map(calcClim, arg_pairs)
    
    ###########################################################################
    # Complete samples
    if 'exterior heat transfer coefficient slope' in samples.columns and 'exterior vapour diffusion transfer coefficient slope' not in samples.columns:
        samples['exterior vapour diffusion transfer coefficient slope'] = samples['exterior heat transfer coefficient slope']*7.7e-9
    if 'exterior vapour diffusion transfer coefficient slope' in samples.columns and 'exterior heat transfer coefficient slope' not in samples.columns :
        samples['exterior heat transfer coefficient slope'] = samples['exterior vapour diffusion transfer coefficient slope']/7.7e-9
    if 'start year' in samples.columns:
        samples = samples.drop('start year',1)
    ###########################################################################
    # Autovariate parameters
    # OUTER LOOP: Loop over design options
    # All design options are subjected to the same samples, which allows to reliably compare the results 
    for i in range(len(design_options['list'])):
        # Read DELPHIN file = design option i
        file_path = design_options['path list'][i]
        dpj_file_orig, x_discr_orig, y_discr_orig, assignments_orig, dpj_lines = supp.readDPJ(file_path)
        # INNER LOOP: Loop over samples
        # For each sample, change parameters in current .dpj file (option i) and save as new .dpj file (Option_i_j.dpj)
#        for j in range(samples.shape[0]):
#            varParam((dpj_file_orig[:], dpj_lines, assignments_orig, samples.iloc[j], path, buildcomp, x_discr_orig[:], y_discr_orig[:], i, j))
        arg_pairs = [(dpj_file_orig[:], dpj_lines, assignments_orig, samples.iloc[j], path, buildcomp, x_discr_orig[:], y_discr_orig[:], i, j) for j in range(samples.shape[0])]
        pool.map(varParam, arg_pairs)
        
    pool.close()
    pool.join()
