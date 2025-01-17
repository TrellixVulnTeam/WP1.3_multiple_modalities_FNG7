# -*- coding: utf-8 -*-
"""
Created on Mon Jul  5 10:31:59 2021

@author: ctorti
"""

#from importlib import reload
#import xnat_tools.format_pathsDict

import os
from pathlib import Path
#import requests
from zipfile import ZipFile
from xnat_tools.sessions import create_session
from xnat_tools.format_pathsDict import create_pathsDict_for_scan


def download_scan(config, srcORtrg, xnatSession=None, pathsDict=None):
    """
    Download scan from XNAT.
    
    Returns a dictionary containing paths mimacking XNAT file hierarchy and the 
    XNAT requests session.
    
    Parameters
    ----------
    config : dict
        Dictionary of configuration settings.
    srcORtrg : str
            'src' or 'trg' for Source or Target.
    xnatSession : requests.models.Response, optional
        If provided a new session request will be avoided.
    pathsDict : dict, optional (None by default)
        Dictionary containing paths of data downloaded. 
    
    Returns
    -------
    pathsDict : dict
        Dictionary containing paths of data downloaded.
    
    Notes
    -----
    GET - /data/projects/{project-id}/subjects/{subject-id | subject-label}/
           experiments/{experiment-id | experiment-label}/scans/{scan-id}/files
           
    GET - /data/experiments/{experiment-id}/scans/{scan-id}/files
    
    https://wiki.xnat.org/display/XAPI/Image+Scan+Resource+API
    """
    
    
    """ Set to True if issue with zip file (e.g. duplication of files): """
    OVERWRITE_ZIP = False
    
    if xnatSession == None:
        xnatSession = create_session(xnatCfg=config)
    
    url = xnatSession.url
    
    #downloadDir = config['downloadDir']
    cwd = config['cwd']
    downloadDir = os.path.join(cwd, 'xnat_downloads')
    
    projID = config['projID']
    subjLab = config['subjLab']
    if srcORtrg == 'src':
        expLab = config['srcExpLab']
        scanID = config['srcScanID']
    else:
        expLab = config['trgExpLab']
        scanID = config['trgScanID']
    
    uri = f'{url}/data/projects/{projID}/subjects/{subjLab}/'\
          + f'experiments/{expLab}/scans/{scanID}/'\
          + 'resources/DICOM/files?format=zip'
    
    request = xnatSession.get(uri)
    
    # Raise status error if not None:
    if request.raise_for_status() != None:
        print(request.raise_for_status())
    
    exportDir = os.path.join(
        downloadDir, 'projects', projID, 'subjects', subjLab, 'experiments'
        )

    if not os.path.isdir(exportDir):
        Path(exportDir).mkdir(parents=True)
        print(f'Created directory:\n {exportDir}\n')
    
    filepath = os.path.join(
        exportDir, f'Experiment_{expLab}__Scan_{scanID}.zip'
        )
    
    if not os.path.exists(filepath) or OVERWRITE_ZIP:
        with open(filepath, 'wb') as file:
            file.write(request.content)
            
        print(f'Zipped file downloaded to: \n{filepath}\n')
        
        #zip_file = ZipFile(filepath, mode='r')
        #zip_file.extractall(exportDir)
        
        with ZipFile(filepath, 'r') as file:
            file.extractall(exportDir)
        
        print(f'Zipped file extracted to: \n{exportDir}\n')
    else:
        if not OVERWRITE_ZIP:
            print(f'Zipped file already downloaded to: \n{filepath}\n')
    
    
    """ Get the directory name of the exported DICOMs: """
    # Get the filepath of the first file in the zip file:
    with ZipFile(filepath, 'r') as file:
        filepath = file.infolist()[0].filename
    
    fullFpath = os.path.join(exportDir, filepath)
    
    #print(f'fullFpath = {fullFpath}\n')
    
    dicomDir = os.path.split(fullFpath)[0]
    
    print(f"DICOMs downloaded to:\n{dicomDir}\n")
    
    """ Store info in a dictionary: """
    pathsDict, keys\
        = create_pathsDict_for_scan(projID, subjLab, expLab, scanID, pathsDict)
    
    #print(f'pathsDict = {pathsDict}\n')
    
    if not 'dir' in keys:
        """ Get the experiment of interest: """
        uri = f'{url}/data/projects/{projID}/subjects/{subjLab}/'\
              + f'experiments/{expLab}?format=json'
        
        request = xnatSession.get(uri)
        
        # Raise status error if not None:
        if request.raise_for_status() != None:
            print(request.raise_for_status())
            
        experiment = request.json()
        
        #print(experiment['items'], '\n')
        #print(experiment['items'][0], '\n')
        #print(experiment['items'][0]['children'], '\n')
        #print(experiment['items'][0]['children'][1], '\n')
        #print(experiment['items'][0]['children'][1]['items'], '\n')
        #print(experiment['items'][0]['children'][1]['items'][0], '\n')
        #print(experiment['items'][0]['children'][1]['items'][0]['data_fields'], '\n')

        #studyUID = experiment['items'][0]['children'][1]['items'][0]['data_fields']['type']['UID']
        #studyUID = experiment['items'][0]['children'][1]['items'][0]['data_fields']['UID'] # 27/05/2021
        studyUID = experiment['items'][0]['data_fields']['UID'] # 27/05/2021
        
        """ There may be more than one item in the list 
        experiment['items'][0]['children'] (e.g. depending on whether there are 
        image assessors or not). Get the index that corresponds to scans: """
        scanInd = None # initial value
        
        for i in range(len(experiment['items'][0]['children'])):
            if 'scan' in experiment['items'][0]['children'][i]['field']:
                scanInd = i
        
        if scanInd == None:
            msg = f"There are no scans for:\n  projID = '{projID}'"\
              + f"\n  subjLab = '{subjLab}'\n  expLab = '{expLab}'"\
              + f"\n  scanID = '{scanID}'."
            raise Exception(msg)
            
        
        """ Get the list of series labels (scan IDs), seriesUIDs and series 
        descriptions for this series/scan: """
        scanIDs = []
        seriesUIDs = []
        seriesDescs = []
        
        #for exp in experiment['items'][0]['children'][1]['items']: # 27/05/21
        for exp in experiment['items'][0]['children'][scanInd]['items']: # 27/05/21
            scanIDs.append(exp['data_fields']['ID'])
            seriesUIDs.append(exp['data_fields']['UID'])
            seriesDescs.append(exp['data_fields']['type'])
            
        
        seriesUID = seriesUIDs[scanIDs.index(scanID)]
        seriesDesc = seriesDescs[scanIDs.index(scanID)]
        
        """ Replacing code below with something more reliable (i.e. rather than
        replacing spaces, dashes and full stops with underscores) (01/06/21).
        """
            
        #""" The folder name between the 'scans' folder and 'resources' folder
        #has the form 'scanID-seriesDesc', but it appears that spaces, dashes and 
        #full stops within seriesDesc become underscores in the folder structure 
        #of the extracted zip file. """
        ##print(f'seriesUID = {seriesUID}')
        ##print(f'seriesDesc = {seriesDesc}\n')
        #
        ##DirName = f'{scanID}-{seriesDesc}'.replace(' ', '_').replace('.', '_') # 01/06/21
        #DirName = f'{scanID}-{seriesDesc}'.replace(' ', '_').replace('.', '_').replace('-', '_') # 01/06/21
        #
        ##ResourceDir = os.path.join(downloadDir, expLab, 'scans', DirName,
        ##                           'resources')
        #
        #ResourceDir = os.path.join(downloadDir, 'projects', projID, 
        #                           'subjects', subjLab, 'experiments', 
        #                           expLab, 'scans', DirName, 'resources')
        #
        #dicomDir = os.path.join(ResourceDir, 'DICOM', 'files')
        #
        #print(f"DICOMs downloaded to:\n{dicomDir}\n")
        
        pathsDict['projects'][projID]['subjects'][subjLab]['experiments']\
            [expLab]['scans'][scanID]['resources']['DICOM']['files']\
                .update({'studyUID' : studyUID,
                         'seriesDesc' : seriesDesc,
                         'seriesUID' : seriesUID,
                         'dicomDir' : dicomDir})
                
    #print(f'pathsDict = {pathsDict}\n')
    
    return pathsDict