# -*- coding: utf-8 -*-
"""
Created on Thu Nov  4 11:15:31 2021

@author: ctorti
"""


"""
This is a tool to create a global variables config file for use with 
app_ohif.py, and hence is not a core module that will need to be used to 
run the app_ohif.py.
"""


import os
#from pathlib import Path
#import time
#import argparse
from io_tools.exports import export_dict_to_json
#from io_tools.imports import import_dict_from_json


def create_global_var_file():
    """
    Generate a JSON file containing global variables that will the user will
    not need to modify (assumed).
    
    Parameters
    ----------
    None.
    
    Returns
    -------
    None.
    
    Notes
    -----
    Resampling / Registration / Transformation settings:
        If the values for the keys "srcFidsFpath" and "trgFidsFpath" are not
        empty, the files containing the fiducials will be used to initialise
        image registration.  If no fiducials are available leave empty.
        
        By default image registration will only be performed if the source and 
        target images have different FrameOfReferenceUIDs.  However it is possible
        for differing ImagePositionPatient and/or ImageOrientationPatient to exist be
        between two images with the same FoR (perhaps down to human error). 
        
        If results of an ROI copy between two datasets with the same FoR arise
        try setting the parameter 'forceReg' to True (it is False by default) to
        force registration to be performed despite equal FoRs.
        
        Image registration can be initialised using one of three methods:
            1. 'landmarks'
            2. 'moments' (or 'centerofgravity')
            3. 'geometry' (or 'geometricalcenter')
            
        If 'landmarks' is chosen but srcFidsFpath and trgFidsFpath are empty or
        not formatted properly, a 'moments'-based initialisation will be performed.
        
        Suitable limits for the maximum iterations ("maxIters") are 512 for 
        rigid/affine, and 100 for bspline registrations.
        
        The following three possible values are allowed for the key "resInterp"
        (resampling interpolator):
            1. 'NearestNeighbor'
            2. 'LabelGaussian'
            3. 'BlurThenLinear'
    """
    
    # Get the current working directory:
    """ 
    Note this is used for exporting the dictionary to a JSON. The cwd 
    variable will be updated later to reflect any environment variable for
    workdir.
    """
    cwd = os.getcwd()
    
    # Root input and output directories (within to the current working
    # directory):
    inputsDir = r'inputs' # 03/11/21
    outputsDir = r'outputs' # 03/11/21
    
    # Directories containing sample DROs and fiducials:
    sampleDroDir = os.path.join(inputsDir, r'sample_DROs')
    fidsDir = os.path.join(inputsDir, r'fiducials')
    
    # Directories for the (new) target ROI Collections, DRO, plots, transforms,
    # binary label maps, logs and configuration files:
    rtsExportDir = os.path.join(outputsDir, r'new_RTS')
    segExportDir = os.path.join(outputsDir, r'new_SEG')
    droExportDir = os.path.join(outputsDir, r'new_DRO')
    rtsPlotsExportDir = os.path.join(outputsDir, 'plots_RTS')
    segPlotsExportDir = os.path.join(outputsDir, 'plots_SEG')
    # resampled/transformed/registered plots
    resPlotsExportDir = os.path.join(outputsDir, r'plots_res')
    txExportDir = os.path.join(outputsDir, r'transforms')
    imExportDir = os.path.join(outputsDir, r'images')
    labimExportDir = os.path.join(outputsDir, r'label_images')
    logsExportDir = os.path.join(outputsDir, r'logs')
    
    """
    Chose whether or not to export the new ROI Collection (i.e. RTS or SEG),
    DRO, transforms, label images, plots and logs:
    """
    exportRoicol = True
    exportDro = True
    exportIm = False # 3D DICOM images
    exportLabim = False # 3D binary label images
    exportTx = False
    exportPlots = False
    exportLogs = True
    
    """
    Chose whether or not to upload the (new) target DRO to XNAT:
    """
    #uploadDro = False
    uploadDro = True # see Notes
    
    """
    Chose whether or not to overwrite an existing DRO to XNAT:
    """
    overwriteDro = False
    #overwriteDro = True # see Notes
    
    """
    Chose whether or not to print results to console (e.g. for debugging):
    """
    p2c = False
    #p2c = True
    
    # Initialise dictionary to store the variables:
    cfg = {
        'regTxName' : 'affine',
        #'initMethod' : 'moments',
        'initMethod' : 'geometry',
        'maxIters' : 512,
        'applyPreResBlur' : False,
        'preResVar' : (1,1,1),
        'resInterp' : 'BlurThenLinear',
        'applyPostResBlur' : True,
        'postResVar' : (1,1,1),
        'exportRoicol' : exportRoicol,
        'exportDro' : exportDro,
        'exportTx' : exportTx,
        'exportIm' : exportIm,
        'exportLabim' : exportLabim,
        'exportPlots' : exportPlots,
        'exportLogs' : exportLogs,
        'uploadDro' : uploadDro,
        'overwriteDro' : overwriteDro,
        'p2c' : p2c,
        'cwd' : cwd, # this will be updated later
        'inputsDir' : inputsDir,
        'outputsDir' : outputsDir,
        'sampleDroDir' : sampleDroDir,
        'fidsDir' : fidsDir,
        'rtsExportDir' : rtsExportDir,
        'segExportDir' : segExportDir,
        'droExportDir' : droExportDir,
        'txExportDir' : txExportDir,
        'imExportDir' : imExportDir,
        'labimExportDir' : labimExportDir,
        'logsExportDir' : logsExportDir,
        'rtsPlotsExportDir' : rtsPlotsExportDir,
        'segPlotsExportDir' : segPlotsExportDir,
        'resPlotsExportDir' : resPlotsExportDir
        }
    
    # Export the dictionary to a JSON file:
    export_dict_to_json(
        dictionary=cfg, filename='global_variables.json', exportDir=cwd
        )
        
    print(f"\nGlobal variables file has been exported to {cwd}")



if __name__ == '__main__':
    """
    Run config_ohif.py as a script.
    
    Example usage in a console:
    
    cd C:\Code\WP1.3_multiple_modalities\src
    python config_ohif.py
    """
    
    # Run create_global_var_file():
    create_global_var_file()