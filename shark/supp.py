# -*- coding: utf-8 -*-
"""
Created on Mon Nov 13 12:31:33 2017

@author: Astrid
"""
import os
import pandas as pd
import numpy as np
from collections import Counter

def getFileList(dir_name, ext=''):
    file_dir_list = list()
    file_list = list()
    for file in os.listdir(dir_name):
        # If no extension is specified, create list with all files
        if not ext:
            file_dir_list.append(os.path.join(dir_name, file))
            file_list.append(file)
        # If extension is specified, create list with only ext files
        elif file.endswith(ext):
            file_dir_list.append(os.path.join(dir_name, file))
            file_list.append(file)
    return file_list, file_dir_list

def string2vec(string):
    vec = []
    for t in string.split():
        try:
            vec.append(float(t))
        except ValueError:
           pass
    return vec

def readDPJ(filename):
    #Read .dpj file line by line
    file_obj = open(filename, 'r')
    file = file_obj.readlines()
    file_obj.close()
    del file_obj
    
    # Search in file for lines that need to be changes, save those lines in a dataframe
    # Create an array with the x-discretisation grid, an array with the y-discretisation grid and an array with the assignments
    x_discretisation = list()
    y_discretisation = list()
    assignments = pd.DataFrame(columns=['line','type','range','name'])
    parameters = pd.DataFrame(columns = ['line','parameter'])
    l=23 #start looking on 24th line
    
    # INITIALISATION SETTINGS
    # Find start year and start time
    while l < len(file):
        if 'START_YEAR' in file[l]:
            parameters = parameters.append({'line': l,'parameter':'start year'},ignore_index=True)
            parameters = parameters.append({'line': l+1,'parameter':'start time'},ignore_index=True)
            l=l+4;
            break
        # If the parameter is not found at the end of the file, there is a problem in the code
        elif l == len(file)-1:
            print('Error: start year and start time not found')
        l=l+1
        
    # MATERIAL PARAMETERS
    k=l
    # Find air layer properties - included only when using an air layer to implement an interior climate dependent on V, n, HIR and exterior climate
    while l < len(file):
        if 'air room' in file[l].lower():
            while  file[l].strip() != '[MATERIAL]' and '; **' not in file[l]:
                if 'CE' in file[l]:
                    parameters = parameters.append({'line': l,'parameter':'room air thermal capacity'},ignore_index=True)
                    l=l+1
                    continue
                elif 'THETA_POR' in file[l]:
                    parameters = parameters.append({'line': l,'parameter':'room air theta_por'},ignore_index=True)
                    l=l+1
                    continue
                elif 'THETA_EFF' in file[l]:
                    parameters = parameters.append({'line': l,'parameter':'room air theta_eff'},ignore_index=True)
                    l=l+1
                    continue
                elif 'THETA_80' in file[l]:
                    parameters = parameters.append({'line': l,'parameter':'room air theta_80'},ignore_index=True)
                    l=l+1
                    continue
                elif 'Theta_l(RH)' in file[l]:
                    parameters = parameters.append({'line': l,'parameter':'room air sorption curve'},ignore_index=True)
                    l=l+1
                    continue
                l=l+1
            l=l+5
            break
        # If the parameter is not found at the end of the file, there is no air layer. We must start looking for the next parameter from the same begin line, so we don't skip part of the file.
        elif l == len(file)-2:
            l=k
            break
        l=l+1
    
    # WALLS
    # Find wall conditions
    while l < len(file):
        if '[WALL_DATA]' in file[l]:
            parameters = parameters.append({'line': l+2,'parameter':'wall orientation'},ignore_index=True)
            parameters = parameters.append({'line': l+3,'parameter':'wall inclination'},ignore_index=True)
            parameters = parameters.append({'line': l+4,'parameter':'latitude'},ignore_index=True)
            l=l+9
            break
        # If the parameter is not found at the end of the file, there is a problem in the code
        elif l == len(file)-1:
            print('Error: wall orientation and inclination not found')
        l=l+1
    
    # CLIMATE CONDITIONS
    while l < len(file):
        if '[CLIMATE_CONDITIONS]' in file[l]:
            k=l
            break
        elif l == len(file)-1:
            print('Error: climate conditions section not found')
        l=l+1
    
    # Find climatic conditions
    # Interior temperature
    l=k # start at beginning of climate conditions
    while l < len(file):
        if 'TEMPER' in file[l] and 'inside' in file[l+1].lower():
            parameters = parameters.append({'line': l+3,'parameter':'interior temperature'},ignore_index=True)
            break
        # If the parameter is not found at the end of the file, there is a problem in the code
        elif l == len(file)-1:
            print('Error: interior temperature not found')
        l=l+1
    
    # Exterior temperature
    l=k # start at beginning of climate conditions
    while l < len(file):
        if 'TEMPER' in file[l] and 'outside' in file[l+1].lower():
            parameters = parameters.append({'line': l+3,'parameter':'exterior temperature'},ignore_index=True)
            break
        # If the parameter is not found at the end of the file, there is a problem in the code
        elif l == len(file)-1:
            print('Error: interior temperature not found')
        l=l+1
    
    # Interior relative humidity
    l=k # start at beginning of climate conditions
    while l < len(file):
        if 'RELHUM' in file[l] and 'inside' in file[l+1].lower():
            parameters = parameters.append({'line': l+3,'parameter':'interior relative humidity'},ignore_index=True)
            break
        l=l+1
    
    # Exterior relative humidity
    l=k # start at beginning of climate conditions
    while l < len(file):
        if 'RELHUM' in file[l] and 'outside' in file[l+1].lower():
            parameters = parameters.append({'line': l+3,'parameter':'exterior relative humidity'},ignore_index=True)
            break
        l=l+1
    
    # Interior vapour pressure
    l=k # start at beginning of climate conditions
    while l < len(file):
        if 'VAPPRES' in file[l] and 'inside' in file[l+1].lower():
            parameters = parameters.append({'line': l+3,'parameter':'interior vapour pressure'},ignore_index=True)
            break
        l=l+1
    
    # Rain load - imposed flux on vertical surface
    l=k # start at beginning of climate conditions
    while l < len(file):
        if 'NORRAIN' in file[l]:
            parameters = parameters.append({'line': l+3,'parameter':'rain vertical surface'},ignore_index=True)
            break
        l=l+1
    
    # Rain load - flux on horizontal surface
    l=k # start at beginning of climate conditions
    while l < len(file):
        if 'HORRAIN' in file[l]:
            parameters = parameters.append({'line': l+3,'parameter':'rain horizontal surface'},ignore_index=True)
            break
        l=l+1
    
    # Wind direction
    l=k # start at beginning of climate conditions
    while l < len(file):
        if 'WINDDIR' in file[l]:
            parameters = parameters.append({'line': l+3,'parameter':'wind direction'},ignore_index=True)
            break
        l=l+1
    
    # Wind velocity
    l=k # start at beginning of climate conditions
    while l < len(file):
        if 'WINDVEL' in file[l]:
            parameters = parameters.append({'line': l+3,'parameter':'wind velocity'},ignore_index=True)
            break
        l=l+1
    
    # Direct sun radiation
    l=k # start at beginning of climate conditions
    while l < len(file):
        if 'DIRRAD' in file[l]:
            parameters = parameters.append({'line': l+3,'parameter':'direct radiation'},ignore_index=True)
            break
        l=l+1
    
    # Diffuse sun radiation
    l=k # start at beginning of climate conditions
    while l < len(file):
        if 'DIFRAD' in file[l]:
            parameters = parameters.append({'line': l+3,'parameter':'diffuse radiation'},ignore_index=True)
            break
        l=l+1
    
    # Cloud covering
    l=k # start at beginning of climate conditions
    while l < len(file):
        if 'CLOUDCOV' in file[l]:
            parameters = parameters.append({'line': l+3,'parameter':'cloud cover'},ignore_index=True)
            break
        l=l+1
    
    # Sky radiation
    l=k # start at beginning of climate conditions
    while l < len(file):
        if 'SKYEMISS' in file[l]:
            parameters = parameters.append({'line': l+3,'parameter':'sky radiation'},ignore_index=True)
            break
        l=l+1
    
    # Sky temperature
    l=k # start at beginning of climate conditions
    while l < len(file):
        if 'SKYTEMP' in file[l]:
            parameters = parameters.append({'line': l+3,'parameter':'sky temperature'},ignore_index=True)
            break
        l=l+1
    
    # BOUNDARY CONDITIONS
    while l < len(file):
        if '[BOUNDARY_CONDITIONS]' in file[l]:
            k=l
            break
        elif l == len(file)-1:
            print('Error: boundary conditions section not found')
        l=l+1
    
    # Find exterior heat transfer coefficient
    l=k; # start at beginning of boundary conditions
    while l < len(file):
        if 'HEATCOND' in file[l] and 'outside' in file[l+1].lower():
            while file[l].strip() != '[BOUND_COND]':
                if 'EXCOEFF' in file[l]:
                    parameters = parameters.append({'line': l,'parameter':'exterior heat transfer coefficient'},ignore_index=True)
                    if 'EXCH_SLOPE' in file[l+1].strip():
                        l=l+1
                        parameters = parameters.append({'line': l,'parameter':'exterior heat transfer coefficient slope'},ignore_index=True)
                    break
                l=l+1
            break
        l=l+1
    
    # Find interior vapour surface resistance coefficient
    l=k # start at beginning of boundary conditions
    while l < len(file):
        if 'VAPDIFF' in file[l] and 'inside' in file[l+1].lower():
            while file[l].strip() != '[BOUND_COND]':
                if 'EXCOEFF' in file[l]:
                    parameters = parameters.append({'line': l,'parameter':'interior vapour diffusion transfer coefficient'},ignore_index=True)
                    break
                l=l+1
            break
        l=l+1
    
    # Find exterior vapour surface resistance coefficient
    l=k # start at beginning of boundary conditions
    while l < len(file):
        if 'VAPDIFF' in file[l] and 'outside' in file[l+1].lower():
            while file[l].strip() != '[BOUND_COND]':
                if 'EXCOEFF' in file[l]:
                    parameters = parameters.append({'line': l,'parameter':'exterior vapour diffusion transfer coefficient'},ignore_index=True)
                    if 'EXCH_SLOPE' in file[l+1].strip():
                        l=l+1
                        parameters = parameters.append({'line': l,'parameter':'exterior vapour diffusion transfer coefficient slope'},ignore_index=True)
                    break
                l=l+1
            break
        l=l+1
    
    # Find solar absorption
    l=k #start at beginning of boundary conditions
    while l < len(file):
        if 'SURABSOR' in file[l]:
            parameters = parameters.append({'line': l,'parameter':'solar absorption'},ignore_index=True)
            break
        l=l+1
    
    # Find scale factor catch ratio
    l=k #start at beginning of boundary conditions
    while l < len(file):
        if 'EXPCOEFF' in file[l]:
            parameters = parameters.append({'line': l,'parameter':'scale factor catch ratio'},ignore_index=True)
            break
        l=l+1
    
    # DISCRETISATION
    while l < len(file):
        if '[DISCRETISATION]' in file[l]:
            k=l
            break
        elif l == len(file)-1:
            print('Error: discretisation section not found')
        l=l+1
    
    # Find discretisation
    l=k #start at beginning of discretisation
    while l < len(file):
        if '[DISCRETISATION]' in file[l]:
            x_discr_str = file[l+3]
            parameters = parameters.append({'line': l+3,'parameter':'x-discretisation'},ignore_index=True)
            y_discr_str = file[l+4]
            parameters = parameters.append({'line': l+4,'parameter':'y-discretisation'},ignore_index=True)
            # remove characters and convert to vector
            x_discretisation = string2vec(x_discr_str)
            y_discretisation = string2vec(y_discr_str)
            break
        # If the discretisation is not found at the end of the file, there is a problem in the code
        elif l == len(file)-1:
            print('Error: discretisation not found')
        l=l+1
    
   # %OUTPUTS
    while l < len(file):
        if '[OUTPUTS]' in file[l]:
            k=l
            break
        elif l == len(file)-1:
            print('Error: outputs section not found')
        l=l+1
    
    # Find output folder
    l=k # start at beginning of outputs
    while l < len(file):
        if 'OUTPUT_FOLDER' in file[l]:
            parameters = parameters.append({'line': l,'parameter':'output folder'},ignore_index=True)
            break
        #If the output folder is not found at the end of the file, there is a problem in the code
        elif l == len(file)-1:
            print('Error: output folder not found')
        l=l+1
    
    # Find output files
    while l < len(file):
        if '[FILES]' in file[l]:
            l=l+3
            while '; **' not in file[l]:
                if 'NAME' in file[l]:
                    output_file = file[l]
                    parameters = parameters.append({'line': l,'parameter':output_file[33:]},ignore_index=True)
                    l=l+5
                    continue
                l=l+1
            break
        # If the output files are not found at the end of the file, there is a problem in the code
        elif l == len(file)-1:
            print('Error: output files not found')
        l=l+1
    
    # ASSIGNMENTS
    while l < len(file):
        if '[ASSIGNMENTS]' in file[l]:
            k=l
            break
        elif l == len(file):
            print('Error: assignments section not found')
        l=l+1
    
    # Find assignments
    l=k # start at beginning of assignments
    while l < len(file):
        if 'RANGE' in file[l]:
            assignments = assignments.append({'line': l, 'type': file[l-1][30:-1].strip(),'range': [int(i) for i in string2vec(file[l])],'name': file[l+1][30:-1].strip()},ignore_index=True)
            l=l+4
            continue
        l=l+1
    #If the discretisation is not found at the end of the file, there is a problem in the code
    if assignments.empty:
        print('Error: assignments not found')
    
    return file, x_discretisation, y_discretisation, assignments, parameters

def readccd(ccdfile, date=False):
    # Find header
    with open(ccdfile, 'r') as f:
        l = 0
        for line in f:
            if '0:00:00' in line:
                header = l
                break
            l = l+1
    # Read ccd
    value = np.loadtxt(ccdfile,skiprows=header,usecols=2,dtype='f').tolist()
    if date:
        day = np.loadtxt(ccdfile,skiprows=header,usecols=0,dtype='i').tolist()
        hour = np.loadtxt(ccdfile,skiprows=header,usecols=1,dtype='U').tolist()
        return value, day, hour
    else:
        return value

def saveccd(path, value):
    days = int(len(value)/24)
    df = pd.DataFrame()
    df['day'] = np.repeat(list(range(days)),24).tolist()
    df['hour'] = ['%02d:00:00' % x for x in range(24)]*days
    df['value'] = value
    climateparam = os.path.basename(path)[4:-4]
    df.to_csv(path, header=[headerccd(climateparam),'',''], sep=' ', index=False, quotechar=' ')

def headerccd(climateparam):
    param_header = pd.DataFrame([{'parameter':'CloudCover', 'header': 'CLOUDCOV   ---'},
                                 {'parameter':'DiffuseRadiation', 'header': 'DIFRAD   W/m2'},
                                 {'parameter':'DirectRadiation', 'header': 'DIRRAD  W/m2'},
                                 {'parameter':'GlobalRadiation', 'header': 'SKYEMISS  W/m2'},
                                 {'parameter':'RelativeHumidity', 'header': 'RELHUM   %'},
                                 {'parameter':'VapourPressure', 'header': 'VAPPRES   Pa'},
                                 {'parameter':'SkyRadiation', 'header': 'SKYEMISS  W/m2'},
                                 {'parameter':'Temperature', 'header': 'TEMPER   C'},
                                 {'parameter':'VerticalRain', 'header': 'NORRAIN   l/m2h'},
                                 {'parameter':'HorizontalRain', 'header': 'HORRAIN   l/m2h'},
                                 {'parameter':'WindDirection', 'header': 'WINDDIR   Deg'},
                                 {'parameter':'WindVelocity', 'header': 'WINDVEL   m/s'},
                                 ])
    header = param_header.loc[param_header['parameter'] == climateparam,'header'].tolist()[0]
    if len(header) == 0:
        print('Error: coud not find climate parameter header')
    return header

def marker(param):
    param_mark = pd.DataFrame([{'parameter': 'wall orientation','marker': 'Deg'},
                              {'parameter': 'wall inclination', 'marker': 'Deg'},
                              {'parameter': 'interior temperature', 'marker': 'C'},
                              {'parameter': 'exterior temperature', 'marker': 'C'},
                              {'parameter': 'exterior heat transfer coefficient', 'marker': 'W/m2K'},
                              {'parameter': 'exterior heat transfer coefficient slope', 'marker': 'J/m3K'},
                              {'parameter': 'interior relative humidity', 'marker': '%'},
                              {'parameter': 'exterior relative humidity', 'marker': '%'},
                              {'parameter': 'interior vapour pressure', 'marker': 'Pa'},
                              {'parameter': 'exterior vapour pressure', 'marker': 'Pa'},
                              {'parameter': 'interior vapour diffusion transfer coefficient', 'marker': 's/m'},
                              {'parameter': 'exterior vapour diffusion transfer coefficient', 'marker': 's/m'},
                              {'parameter': 'exterior vapour diffusion transfer coefficient slope', 'marker': 's2/m2'},
                              {'parameter': 'solar absorption', 'marker': '-'},
                              {'parameter': 'scale factor catch ratio', 'marker': '-'},
                              {'parameter': 'output folder', 'marker': ''},
                              {'parameter': 'x-discretisation', 'marker': 'm'},
                              {'parameter': 'y-discretisation', 'marker': 'm'},
                              {'parameter': 'start year', 'marker': ''},
                              {'parameter': 'start time', 'marker': ''}
                              ])
    mark = param_mark.loc[param_mark['parameter'] == param,'marker'].tolist()[0]
    if len(mark) == 0:
        print('Error: coud not find parameter marker')
    return mark

def nameccd(climateparam):
    param_name = pd.DataFrame([{'parameter': 'cloud cover','name':'CloudCover'},
                               {'parameter': 'diffuse radiation','name':'DiffuseRadiation'},
                               {'parameter': 'direct radiation','name':'DirectRadiation'},
                               {'parameter': 'sky radiation','name':'SkyRadiation'},
                               {'parameter': 'interior relative humidity','name':'RelativeHumidity'},
                               {'parameter': 'exterior relative humidity','name':'RelativeHumidity'},
                               {'parameter': 'interior vapour pressure','name':'VapourPressure'},
                               {'parameter': 'sky radiation','name':'SkyRadiation'},
                               {'parameter': 'interior temperature','name':'Temperature'},
                               {'parameter': 'exterior temperature','name':'Temperature'},
                               {'parameter': 'rain vertical surface','name':'VerticalRain'},
                               {'parameter': 'rain horizontal surface','name':'HorizontalRain'},
                               {'parameter': 'wind direction','name':'WindDirection'},
                               {'parameter': 'wind velocity','name':'WindVelocity'},
                               ])
    name = param_name.loc[param_name['parameter'] == climateparam,'name'].tolist()[0]
    if len(name) == 0:
        print('Error: coud not find climate parameter name')
    return name

def readOutput(path):
    # Get list of all files that need to be read
    files = getFileList(path, ext='.out')[1]
    # Extract output parameters from list
    param = list(Counter([x.split('\\')[-1][:-12] for x in files]).keys())
    # Extract numbers from list
    num = list(Counter([x[-11:-4] for x in files]).keys())
    # Read files
    output, geometry, elements = pd.DataFrame(columns=param), pd.DataFrame(columns=['geom_x','geom_y']), pd.DataFrame(columns=param)
    for n in num:
        files_num = [x for x in files if x[-11:-4] == n]
        output_fn, geometry_fn, elements_fn = dict(), dict(), dict()
        geom_x, geom_y = None, None
        for file in files_num:
            with open(file, 'r') as f:
                l = 0
                for line in f:
                    # Find geometry line
                    if 'TABLE  GRID' in line: 
                        geom_x = string2vec(f.readline())
                        geom_y = string2vec(f.readline())
                        l += 2
                    # Find output start line
                    if 'ELEMENTS' in line:
                        elem_f = string2vec(line)
                        output_f = np.loadtxt(file,skiprows=l+1,usecols=tuple(range(1,len(elem_f)+1)),dtype='f')
                        break
                    l +=1
                # Combine in dictionary
                geometry_fn['geom_x'], geometry_fn['geom_y'],  = geom_x, geom_y
                elements_fn[file.split('\\')[-1][:-12]] = elem_f
                output_fn[file.split('\\')[-1][:-12]] = output_f
        # Combine in dataframe
        geometry.loc[n] = pd.Series(geometry_fn)
        elements.loc[n] = pd.Series(elements_fn)
        output.loc[n] = pd.Series(output_fn)
    return output, geometry, elements