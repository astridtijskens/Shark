# -*- coding: utf-8 -*-
"""
Created on Mon Dec  4 16:09:36 2017

@author: Astrid
"""

from distutils.core import setup

setup(
    # Application name:
    name="SHARK",

    # Version number (initial):
    version="0.3.1",

    # Application author details:
    author="Astrid Tijskens",
    author_email="astrid.tijskens@kuleuven.be",

    # Packages
    packages = ['shark'],
    package_dir={'shark': 'shark'},
    
    # Include additional files needed by the module distribution
    package_data={'shark': ['data/*']},

    # Details
    url="https://github.com/astridtijskens/Shark",

    # License
    license="LICENSE.txt",
    
    description="This package allows Monte Carlo simulations with the hygrothermal simulation environment DELPHIN 5.8.",

    # Dependent packages (distributions)
    requires=[
        "pandas", 
        "os",
        "scipy",
        "numpy",
        "sys",
        "multiprocessing",
        "math",
        "subprocess",
        "re",
        "collections"]
)