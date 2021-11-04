# -*- coding: utf-8 -*-
"""
Created on Thu Sep 30 11:24:09 2021

@author: ctorti
"""



""" 
Batch script for running the ROI Collection propagation.

Note:
This is intended as a backend script working alongside frontend work in the
OHIF-Viewer.

As opposed to the stand-alone version (app.py) this will not fetch data from
XNAT but instead will work on the basis that the data has been stored in a
temporary folder on the localhost.

Hence for development the ROI Collections and scans have been stored in the
inputs directory.

This implementation will only need to perform ROI propagations (i.e. those
involving relationship-preserving that require resampling or image registrtion
to account for different voxel resolutions and/or frames of reference), since
simple ("direct") copying of ROIs will be handled exclusively in the frontend.

That said, none of the code that handles the simple cases (use cases 1-2) will
be removed.
""" 


import sys

code_root = r'C:\Code\WP1.3_multiple_modalities\src'

# Add code_root to the system path so packages can be imported from it:
sys.path.append(code_root)


from importlib import reload
import io_tools.import_data
reload(io_tools.import_data)
import io_tools.import_dro
reload(io_tools.import_dro)
import io_tools.propagate
reload(io_tools.propagate)
import dicom_tools.create_roicol
reload(dicom_tools.create_roicol)
import dro_tools.create_dro
reload(dro_tools.create_dro)


import time
import argparse
from io_tools.import_data import DataImporter
from io_tools.import_dro import DroImporter
from io_tools.propagate import Propagator
from dicom_tools.create_roicol import RoicolCreator
from dro_tools.create_dro import DroCreator


def main(
        cfgDir, runID, printSummary=False, plotResults=False):
    """
    Main script for fetching the config settings, downloading data from XNAT,
    importing of source ROI Collection and source and target DICOM series, 
    copy/propagation of source ROI Collection to the target dataset, creation
    of new ROI Collection, creation of a DRO and uploading to XNAT (if 
    applicable).
    
    Parameters
    ----------
    cfgDir : str
        The path to the directory containing config files.
    runID : str
        The ID that determines the main configuration parameters to use for the
        run (i.e. the key in the base level dictionary contained in 
        main_params.json).
    printSummary : bool, optional
        If True, summarising results will be printed. The default is False.
    plotResults : bool, optional
        If True, results will be printed. The default is False.
    
    Returns
    -------
    None.
    """
    
    cfgDir = r'' + cfgDir # convert to an r path
    #print(f'\ncfgDir = {cfgDir}\n')
    
    # Store time stamps for various steps:
    times = [time.time()]
    
    # Instanstantiate a ConfigFetcher object, get the config settings, and 
    # get the alias token (which may or may not exist):
    cfgObj = ConfigFetcher(cfgDir, runID)
    cfgObj.get_config()
    cfgObj.update_cfgDict()
    #cfgObj.get_alias_token()
    
    # Instantiate a DataDownloader object, download the data and create
    # pathsDict:
    params = DataDownloader(cfgObj)
    params.download_and_get_pathsDict()
    
    # Instantiate a DataImporter object for source and import the data:
    srcDataset = DataImporter(params, 'src')
    srcDataset.import_data(params)
    
    # Instantiate a DataImporter object for target and import the data:
    trgDataset = DataImporter(params, 'trg')
    trgDataset.import_data(params)
    
    # Instantiate a DROImporter object and fetch the DRO (if applicable):
    droObj = DroImporter()
    droObj.fetch_dro(params)
    
    times.append(time.time())
    dTime = times[-1] - times[-2]
    
    # Instantiate a Propagator object and copy/propagate the source ROI
    # Collection to the target dataset:
    newDataset = Propagator(srcDataset, trgDataset, params)
    newDataset.execute(srcDataset, trgDataset, params, droObj.dro)
    
    times.append(time.time())
    dTime = times[-1] - times[-2]
    
    print('\n\n\n*** TIMINGS ***')
    [print(msg) for msg in params.timingMsgs if 'Took' in msg]
    print(f'Total time {dTime:.1f} s ({dTime/60:.1f} min) to',
          f'execute runID {runID}.\n\n\n')
    
    if printSummary:
        newDataset.print_summary_of_results(srcDataset, trgDataset)
    
    if plotResults:
        newDataset.plot_metric_v_iters(params)
        newDataset.plot_res_results(srcDataset, trgDataset, params)
        newDataset.plot_roi_over_dicom_im(
            srcDataset, trgDataset, params
            )
    
    # Instantiate RoicolCreator, create the new ROI Collection, check
    # for errors, export, upload to XNAT, and plot results 
    # (conditional):
    roicolObj = RoicolCreator()
    roicolObj.create_roicol(srcDataset, trgDataset, newDataset, params)
    roicolObj.error_check_roicol(srcDataset, trgDataset, newDataset, params)
    roicolObj.export_roicol(params)
    roicolObj.upload_roicol(params)
    if plotResults:
        roicolObj.plot_roi_over_dicoms(srcDataset, trgDataset, newDataset, params)
    
    # Instantiate a DroCreator object, create a new DRO, export it to
    # disk, and upload to XNAT:
    newDroObj = DroCreator(newDataset, params)
    newDroObj.create_dro(srcDataset, trgDataset, newDataset, params)
    newDroObj.export_dro(params)
    newDroObj.upload_dro(params)

if __name__ == '__main__':
    """
    Run app.py as a script.
    
    Example usage in a console:
    
    python app.py C:\Code\WP1.3_multiple_modalities\src\configs NCITA_TEST_RR2
    """
    
    parser = argparse.ArgumentParser(description='Arguments for main()')
    
    parser.add_argument(
        "cfgDir", 
        help="The directory containing config files"
        )
    
    parser.add_argument(
        "runID", 
        help="The run ID to execute"
        )
    
    parser.add_argument(
        "--printSummary", 
        action="store_true",
        #type=bool,
        help="Print summary if True"
        )
    
    parser.add_argument(
        "--plotResults", 
        action="store_true",
        #type=bool,
        help="Plot results if True"
        )
    
    args = parser.parse_args()
    
    # Run main():
    main(args.cfgDir, args.runID, args.printSummary, args.plotResults)