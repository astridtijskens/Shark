# -*- coding: utf-8 -*-
"""
Created on Fri Nov 17 13:14:54 2017

@author: Astrid
"""
from shark import discr, supp

def cParameter(file, lines, values):
    for param in values.keys():
        line = lines.loc[lines['parameter'] == param,'line'].tolist()
        if len(line) == 0:
            continue
        else: 
            line = line[0]
            value = values[param]
#            if value < 1e-4: value_str = '%.4e' % value
#            else: value_str = '%.4f' % value
            string = file[line]
            string = string[:string.rfind("=")+2] + '%.4e' % value +' '+str(supp.marker(param))+'\n'
            file[line] = string
    return file

def cClimate(file, lines, values):
    for param in values.keys():
        if 'ext climate' in param:
            clim_params = ['exterior temperature', 'exterior relative humidity', 'exterior vapour pressure' , 'rain vertical surface', 'rain horizontal surface', 'wind direction', 'wind velocity', 'direct radiation', 'diffuse radiation', 'sky radiation', 'sky temperature']
        elif'int climate' in param:
            clim_params = ['interior temperature', 'interior relative humidity','interior vapour pressure']
        else:
            continue
        for p in clim_params:
            line = lines.loc[lines['parameter'] == p,'line'].tolist()
            if len(line) != 0:
                line = line[0]
                value = values[param]
                string = file[line]
                # data poits
                if isinstance(value, str):
                    string = string[:string.rfind("=")+2] + value + supp.nameccd(p) + '.ccd\n'
                # Constant value
                else:
                    string = string[:string.rfind("=")+2] + str(value) +' '+str(supp.marker(param))+'\n'
                file[line] = string
    return file

def cOutput(file, lines, value, path, assignments):
    for param in lines['parameter']:
        if param == 'output folder':
            line = lines.loc[lines['parameter'] == param,'line'].tolist()[0]
            string = file[line]
            string = string[:string.rfind("=")+2] + path +'\n'
            file[line] = string
        elif '.out' in param:
            line = lines.loc[lines['parameter'] == param,'line'].tolist()[0]
            string = file[line]
            string = string[:string.rfind(".out")] + '_'+str(value) + string[string.rfind('.out'):]
            file[line] = string
    for a in assignments.index.values:
        if '.out' in assignments.get_value(a,'name'):
            line = assignments.get_value(a,'line')+1
            string = file[line]
            string = string[:string.rfind(".out")] + '_'+str(value) + string[string.rfind('.out'):]
            file[line] = string
    return file

def cDiscretisation(file, lines, values, steps_change, steps_keep, col, assignments, Xdir=True, param_discr={'stretch factor':1.6,'detail':13.44,'min_grid':0.001,'max_grid':0}):
    # Change discretisation
    for param in values.keys():
        if 'dimension' in param:
            d = values[param]
            steps_change[col[1]-1] = d - sum(steps_change[col[0]-1:col[1]-1]) - sum(steps_change[col[1]:col[2]])
            if Xdir:
                # Discretise
                steps_change, assignments = discr.discr_X(xsteps=steps_change, ysteps=steps_keep, column=col[1], assignments=assignments, param_discr=param_discr)
                # Change line
                line = lines.loc[lines['parameter'] == 'x-discretisation','line'].tolist()[0]
                string = file[line]
                string = string[:string.rfind("=")+2] + str([round(x,5) for x in steps_change]).strip('[]').replace(',','') +' '+str(supp.marker('x-discretisation'))+'\n'
            else:
                # Discretise
                steps_change, assignments = discr.discr_Y(xsteps=steps_keep, ysteps=steps_change, row=col[1], assignments=assignments, param_discr=param_discr)
                # Change line
                line = lines.loc[lines['parameter'] == 'y-discretisation','line'].tolist()[0]
                string = file[line]
                string = string[:string.rfind("=")+2] + str([round(x,5) for x in steps_change]).strip('[]').replace(',','') +' '+str(supp.marker('y-discretisation'))+'\n'
            file[line] = string
            continue
    # Change assignment ranges
    for a in assignments.index.values:
        line = assignments.get_value(a,'line')
        string = file[line]
        string = string[:string.rfind("=")+2] + str(assignments.get_value(a,'range')).strip('[]').replace(',','') +'\n'
        file[line] = string
    return file

def cMaterial(file, values, assignments):
    for param in values.keys():
        if 'material' in param:
            mat = param.replace('material', '').strip().lower()
            for a in assignments.index.values:
                 if mat in assignments.get_value(a,'name').lower() and assignments.get_value(a,'type') =='MATERIAL':
                     line = assignments.get_value(a,'line')+1
                     string = file[line]
                     string = string[:string.rfind("=")+2] + values[param] +'\n'
                     file[line] = string
    return file