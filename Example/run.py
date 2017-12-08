# -*- coding: utf-8 -*-
"""
Example of how to use shark to for probabilistic Monte-Carlo simulations with DELPHIN 5.8.
===============================================================================
2017-12-05

This script simulates all the variation Delphin files created by config.py.
Simulations are done in parallel, to speed up the simulation time.
"""

# Chech first which simulations were already run successfully? and skip these
check_finished_simulations = True

# How many CP's schould NOT be used?
cpu_unused = 0

# Specify the path to the Delphin executable
delphin_executable = 'C:\Program Files (x86)\IBK\Delphin 5.8\delphin_solver.exe'

"""
###############################################################################
# Run - no changes below this line
###############################################################################
"""

from shark import supp, solver
import os
import threading, queue
import multiprocessing

def main():
    # read variations path
    path = os.path.join(os.path.dirname(__file__), 'Delphin files', 'Variations')
    # get list of all Delphin files to stimulate
    files = supp.getFileList(path, '.dpj')[1]
    
    # Check finished simulations
    if check_finished_simulations:
        simstatus = solver.checkFinSim(files)
        print('%i files were already simulated succesfully, now simulating %i files' % (sum(simstatus),len(simstatus)-sum(simstatus)))
    else:
        simstatus = [False]*len(files)
        print('Simulating all %i files' % len(simstatus))
    simfiles = [x for i,x in enumerate(files) if not simstatus[i]]
    
    # Run simulations
    num_cores = multiprocessing.cpu_count()
    q = queue.Queue()
    # create threads
    for i in range (num_cores):
        t = threading.Thread(target = solver.delphin_solver, args = (delphin_executable,q))
        t.daemon = True
        t.start()
    # add project files to the queue
    for f in simfiles:
        q.put(f)
    # wait untill all tasks are done
    q.join()
    
    print('Done!')

if __name__ == '__main__':
    __spec__ = None
    main()