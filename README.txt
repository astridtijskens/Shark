==============================================================
SHARK - A package for Monte Carlo simulations with DELPHIN 5.8
==============================================================

MIT License

Copyright (c) 2017 Astrid Tijskens

astrid.tijskens@kuleuven.be
KU Leuven, Civil Engineering, Building Physics


==============================================================
Introduction
==============================================================

This package contains utilities to perform probabilistic Monte-Carlo simulations with DELPHIN 5.8.

The probabilistic simulation process is split into five parts:

1.	Create design options in Delphin
	Create one (or more) Delphin file(s) with the desired geometry and assign the boundary conditions and the desired outputs. 
	These files form the basis of the probabilistic assessment.
	This is very project specific and thus not automated.

2.	Generate sampling scheme based on given parameters and parameter distributions
	Reference: L. Van Gelder, H. Janssen, and S. Roels, “Probabilistic design and analysis of building performances: Methodology and application example,” Energy and Buildings, vol. 79, pp. 202–211, 2014.
	
3.	Generate Delphin simulation files based on given design options and sampling scheme
		- Automatically calculate and assign interior and exterior climate files
		- Automatically change parameter values in Delphin files
		- Save newly created Delphin files to disc

4.	Runs simulations
	Send all newly created in parallel to the Delphin Solver.
	All available CPU's are used to speed up the simulation time.

5.	Postprocess
	Read the output files into Python and process with a desired damage prediction model.
	This is very project specific and thus not automated.

	
==============================================================
Installation 
==============================================================

In order to use the climate functions (calculate interior and exterior climate), you need to specify the directory of the folder containing the exterior climate data.
This folder should contain subfolders for each climate location (e.g. Bremerhaven, Essen, Munich, ...)
To specify the exterior climate directory, open de file 'dir_exct_clim' in a text editor and change the directory to the directory on your machine.