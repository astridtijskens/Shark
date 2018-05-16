# -*- coding: utf-8 -*-
"""
Created on Tue Nov 28 11:35:34 2017

@author: Astrid
"""
import os
import subprocess
import re
import multiprocessing

def main(delphin_executable, files, feedback=True):
    args = [(delphin_executable, f, feedback) for f in files]
#    for a in args:
#        delphin_solver(a)
    num_cores = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(num_cores, maxtasksperchild=16)
    pool.map(delphin_solver, args)
    pool.close()
    pool.join()

def checkFinSim(files):
    # Create list of .output files
    outputfiles = [x + '.output' for x in files]
    # Check if file was simulated succesfully
    status = list()
    for f in outputfiles:
        if os.path.exists(f):
            # If the file exists, read it and look for the sentence 'Simulation finished'
            with open(f, 'r') as fo: output = fo.read()
            if 'Simulation finished' in output:
                status.append(True)
            else:
                status.append(False)
        else:
            #If the file does not exist, is has not been simulated yet
            status.append(False)
    return status

def adjustRelTol(filename, feedback):
    #Read .dpj file line by line
    file_obj = open(filename, 'r', encoding='utf8')
    file = file_obj.readlines()
    file_obj.close()
    del file_obj
    
    # Get current relative tolerance and define new
    l = 0
    while l < len(file):
        if 'REL_TOL' in file[l]: break
        l = l+1
    string = file[l]
    rel_tol_old = re.sub('[^0-9e.-]', '', string)
    rel_tol_new = float(rel_tol_old)/10
    # Replace old relative tolerance by new
    string = re.sub(rel_tol_old, '%.4e' % rel_tol_new, string)
    file[l] = string
    # write new Delphin file
    file_obj = open(filename, 'w', encoding='utf8')
    file_obj.writelines(file)
    file_obj.close()
    del file_obj, file
    if feedback:
        print('Adjusted relative tolerance of ' + filename.split('\\')[-1])

def adjustMaxOrder(filename, feedback):
    #Read .dpj file line by line
    file_obj = open(filename, 'r', encoding='utf8')
    file = file_obj.readlines()
    file_obj.close()
    del file_obj
    
    # Get current relative tolerance and define new
    l = 0
    while l < len(file):
        if 'MAX_ORDER' in file[l]: break
        l = l+1
    string = file[l]
    max_order_old = re.sub('[^0-9e.-]', '', string)
    # Replace old max order by new
    string = re.sub(max_order_old, '2', string)
    file[l] = string
    # write new Delphin file
    file_obj = open(filename, 'w', encoding='utf8')
    file_obj.writelines(file)
    file_obj.close()
    del file_obj, file
    if feedback:
        print('Adjusted max order method of ' + filename.split('\\')[-1])

def delphin_solver(args):
    delphin_executable, filename, feedback = args
    t = 1
    while True:
        if feedback:
            print ('Running: ' + filename.split('\\')[-1])
        status = subprocess.run([delphin_executable , "-x", "-v0", filename], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        # if the simulation was succesfull, print
        if not status.returncode:
            if feedback:
                print('Finished: ' + filename.split('\\')[-1])
            break
        # if the simulation was unsuccesfull:
        else:
            if t <= 3:
                # Adjust relative tolerance and re-add file to queue
                adjustRelTol(filename, feedback)
                t += 1
            elif t == 4:
                # If files didn't successfully simulate after 3 tries of adjustRelTol, adjust the max. order method
                adjustMaxOrder(filename, feedback)
                t += 1
            elif feedback:
                # If files didn't successfully simulate after of adjustMaxOrder, there is a problem with the file itself
                print('Error: cannot simulate ' + filename.split('\\')[-1])
                break
            