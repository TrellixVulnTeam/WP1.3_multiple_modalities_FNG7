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
from io_tools.exports import export_dict_to_json


def create_global_vars():
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
    
    With the exception of cwd (current working directory), all directory paths
    are deliberately defined relative to the root directory (i.e. src/) so that 
    the local filesystem used to generate the paths is not present. Instead, at 
    the point at which global_variables.json is imported, the paths will be 
    modified by adding the relative paths to the current working directory to 
    make the paths absolute and relevant to the local filesystem that is 
    importing it.
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
    
    # Directories containing configuration files (for various runIDs), sample 
    # DROs and fiducials relative to src/:
    xnatCfgDir = os.path.join(r'xnat_configs')
    sampleDroDir = os.path.join(inputsDir, r'sample_dros')
    fidsDir = os.path.join(inputsDir, r'fiducials')
    
    # Directories for the (new) target ROI Collections, DRO, plots, transforms,
    # binary label maps, logs and configuration files:
    rtsExportDir = os.path.join(outputsDir, r'roicols')
    segExportDir = os.path.join(outputsDir, r'roicols')
    droExportDir = os.path.join(outputsDir, r'dros')
    rtsPlotsExportDir = os.path.join(outputsDir, 'plots_rts')
    segPlotsExportDir = os.path.join(outputsDir, 'plots_seg')
    # resampled/transformed/registered plots
    resPlotsExportDir = os.path.join(outputsDir, r'plots_res')
    txExportDir = os.path.join(outputsDir, r'transforms')
    imExportDir = os.path.join(outputsDir, r'images')
    labimExportDir = os.path.join(outputsDir, r'label_images')
    logsExportDir = os.path.join(outputsDir, r'logs')
    
    """
    Define registration settings.
    
    Chose whether or not to force registration (even if the frames of 
    reference of the two datasets are the same), whether to use a DRO (if 
    applicable and available), the registration type ('rigid', 'affine',
    'bspline'), the initialisation method ('landmarks', 'moments', 'geometry'),
    and the maximum number of interations:
    """
    forceReg = False
    useDroForTx = True
    regTxName = 'affine'
    initMethod = 'geometry'
    maxIters = 512
    
    """ 
    Define resampling settings.
    
    Chose whether or not to apply a pre-resampling Gaussian blur to the source 
    label image, the variance of the pre-sampling blur, what type of 
    interpolation strategy to use ('NearestNeighbor', 'LabelGaussian',
    'BlurThenLinear'), apply a post-resampling blur, and the variance of the
    post-resampling Gaussian blur:
    """
    applyPreResBlur = False
    preResVar = (1,1,1)
    resInterp = 'BlurThenLinear'
    applyPostResBlur = True
    postResVar = (1,1,1)
    
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
    The parameter addToRoicolLabel allows for adding text to the 
    StructureSetLab (SSL) of the new DICOM-RTSTRUCT or SeriesDescription (SD)
    of the new DICOM-SEG file, 
    e.g. New SSL/SD = SSD/SD copied from the Source RTS/SEG + addToRoicolLabel
    The default value of addToRoicolLab will the empty string, which will
    result in the addition of the timestamp of the file creation,
    e.g. "{copied SSL/SD} 20210323 101748".
    """
    addToRoicolLab = '' # the current timestamp will be added
    
    """ 
    When searching XNAT for the source ROI Collection that matches the required
    metadata multiple hits may arise. Chose how to proceed from the following
    3 options:
        1. Select the oldest ROI Collection (whichSrcRoicol = 'oldest')
        2. Select the newest ROI Collection (whichSrcRoicol = 'newest')
        3. Allow the user to decide (whichSrcRoicol = 'user')
    """
    whichSrcRoicol = 'oldest'
    #whichSrcRoicol = 'newest'
    #whichSrcRoicol = 'user'
    
    """
    Chose whether or not to print results to console (e.g. for debugging):
    """
    p2c = False
    #p2c = True
    
    # Initialise dictionary to store the variables:
    globalVars = {
        'forceReg' : forceReg,
        'useDroForTx' : useDroForTx,
        'regTxName' : regTxName,
        'initMethod' : initMethod,
        'maxIters' : maxIters,
        'applyPreResBlur' : applyPreResBlur,
        'preResVar' : preResVar,
        'resInterp' : resInterp,
        'applyPostResBlur' : applyPostResBlur,
        'postResVar' : postResVar,
        'exportRoicol' : exportRoicol,
        'exportDro' : exportDro,
        'exportTx' : exportTx,
        'exportIm' : exportIm,
        'exportLabim' : exportLabim,
        'exportPlots' : exportPlots,
        'exportLogs' : exportLogs,
        'uploadDro' : uploadDro,
        'overwriteDro' : overwriteDro,
        'whichSrcRoicol' : whichSrcRoicol,
        'addToRoicolLab': addToRoicolLab,
        'p2c' : p2c,
        'cwd' : cwd, # this will be updated later
        'xnatCfgDir' : xnatCfgDir,
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
    filename = 'global_variables.json'
    export_dict_to_json(
        dictionary=globalVars, filename=filename, exportDir=cwd
        )
    
    filepath = os.path.join(cwd, filename)
    print(f"\nGlobal variables file has been exported to {filepath}")


if __name__ == '__main__':
    """
    Run create_global_file.py as a script.
    
    Example usage in a console:
    
    python create_global_file.py
    """
    
    create_global_vars()