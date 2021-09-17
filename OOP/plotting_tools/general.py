# -*- coding: utf-8 -*-
"""
Created on Thu Jul  8 16:07:37 2021

@author: ctorti
"""

from importlib import reload
import general_tools.console_printing
reload(general_tools.console_printing)

import time
import os
from pathlib import Path
import SimpleITK as sitk
#import itk
import matplotlib.pyplot as plt
from pydicom import dcmread

import dicom_tools.seg_data
reload(dicom_tools.seg_data)
import general_tools.general
reload(general_tools.general)

from general_tools.general import get_unique_items
from dicom_tools.seg_data import (
    get_seg_data_from_list_of_segs, get_seg_data_from_list_of_labimByRoi
    )
from conversion_tools.pixarrs_ims import im_to_pixarr, imBySeg_to_pixarrBySeg
from general_tools.console_printing import (
    print_indsByRoi, print_ptsByCntByRoi, print_pixarrBySeg, print_labimBySeg
    )

    
def plot_two_ims(im0, ind0, plotLabel0, im1, ind1, plotLabel1):
    
    pixarr0 = sitk.GetArrayViewFromImage(im0)[ind0,:,:]
    pixarr1 = sitk.GetArrayViewFromImage(im1)[ind1,:,:]
    
    z0 = im0.TransformIndexToPhysicalPoint([0,0,ind0])[2]
    z1 = im1.TransformIndexToPhysicalPoint([0,0,ind1])[2]
    
    plotLabel0 = f'{plotLabel0}\nz = {round(z0, 2)} mm'
    plotLabel1 = f'{plotLabel1}\nz = {round(z1, 2)} mm'
    
    plt.subplots(1, 2, figsize=(15,8))
    
    plt.subplot(1, 2, 1)
    plt.imshow(pixarr0, cmap=plt.cm.Greys_r);
    plt.title(plotLabel0)
    plt.axis('off')
    
    plt.subplot(1, 2, 2)
    plt.imshow(pixarr1, cmap=plt.cm.Greys_r);
    plt.title(plotLabel1)
    plt.axis('off')
    
    plt.show()
    
    return

def plot_pixarrBySeg(pixarrBySeg, f2sIndsBySeg, plotTitle=''):
    """ 
    pixarrBySeg can either be a list of pixel arrays (as the variable name
    suggests), or a pixel array, and f2sIndsBySeg can either be a list (for 
    each segment) of a list (for each frame) of frame-to-slice indices, or it
    can be a list (for each frame) of frame-to-slice indices.
    
    The pixel array(s) must have shape (F, R, C) where F is the number of
    frames, which could be any integer number including 0. 
    """
    
    # Set the number of subplot rows and columns:
    if isinstance(pixarrBySeg, list):
        Ncols = len(pixarrBySeg)
        
        NframesBySeg = []
        
        for i in range(Ncols):
            pixarr = pixarrBySeg[i]
            
            NframesBySeg.append(pixarr.shape[0])
            
        Nrows = max(NframesBySeg)
    else:
        Nrows = pixarr.shape[0]
                
        """ Put the pixel array and f2sInds into a list. """
        pixarrBySeg = [pixarrBySeg]
        f2sIndsBySeg = [f2sIndsBySeg]
    
    fig, ax = plt.subplots(Nrows, Ncols, figsize=(5*Ncols, 8*Nrows))
    
    n = 1 # initialised sub-plot number
        
    # Loop through each pixel array:
    for i in range(Ncols):
        pixarr = pixarrBySeg[i]
        f2sInds = f2sIndsBySeg[i]
        
        print(f'\npixarr {i} has shape {pixarr.shape}')
        print(f'f2sInds = {f2sInds}')
        F = pixarr.shape[0]
        
        if F != len(f2sInds):
            print(f'The number of frames in pixarr, {F}, does not match the',
                  f'length of f2sInds, {len(f2sInds)}')
        
        # Loop through each frame:
        for f in range(F):
            #if f < F:
            ax = plt.subplot(Nrows, Ncols, n)
            ax.imshow(pixarr[f], cmap=plt.cm.Greys_r)
            ax.set_xlabel('pixels'); ax.set_ylabel('pixels')
            ax.set_title(plotTitle + f'\nframe {f2sInds[f]}')
            
            n += 1 # increment sub-plot number
    return

def plot_pixarrs_from_list_of_segs_and_dicomPixarrs(
        listOfSegs, listOfDicomPixarrs, listOfDicomDirs, listOfPlotTitles,
        exportPlot=False, exportDir='cwd', runID='', useCaseToApply='',
        forceReg=False, useDroForTx=False, regTxName='', initMethod='', 
        resInterp='', fname='', fontSize=12, p2c=False
        ):
    """
    02/06/2021
    
    Note:
        
    Modification of v1 that was previously called v3. Rather than plotting 
    allSliceNums = get_unique_items(listOfF2SindsBySeg)
    will just plot frames with segmentations since f2sInds for Src and Trg can 
    relate to very different depths, leading to a confusing plot.
    
    listOfSegs is a list (which could be of length 1) of SEG (Pydicom) objects.
    
    listOfDicomPixarrs is a list (which could be of length 1) of a list (for
    each DICOM) of pixel array representations of the DICOM.
    
    listOfDicomDirs is a list (which could be of length 1) of strings 
    containing the directory containing DICOMs.
    
    listOfPlotTitles is a list (which could be of length 1) of text for each
    plot title.
    
    Note
    ----
    listOfDicomPixarrs can either be obtained:
        
    1) By importing DICOMs given a list of directories containing DICOMs 
    (listOfDicomsDir)
    --> use plot_pixarrs_from_list_of_segs_and_dicomDirs()
    
    2) From a list of SimpleITK images (listOfImages) 
    --> use plot_pixarrs_from_list_of_segs_and_images
    
    both of which then calls this function. 
    
    
    Plot has different DATASETS ALONG COLUMNS and different SLICES ALONG ROWS. 
    """
    
    listOfPixarrBySeg, listOfF2SindsBySeg, listOfImSizes, listOfImSpacings,\
        listOfImIPPs, listOfImDirections, listOfDcmFpaths\
            = get_seg_data_from_list_of_segs(listOfSegs, listOfDicomDirs, p2c)
    
    # Get a list of pixel arrays for each dicom for each dataset:
    listOfDcmPixarrs = []
    
    # Loop through each dataset:
    for i in range(len(listOfDcmFpaths)):
        dcmFpaths = listOfDcmFpaths[i]
        pixarrs = []
        for fpath in dcmFpaths:
            pixarrs.append(dcmread(fpath).pixel_array)
        listOfDcmPixarrs.append(pixarrs)
    
    # Get the maximum number of slices containing segmentations in any ROI in 
    # any dataset:
    maxNumSlices = 0
    
    # The list (for each dataset) of the unique set of slice numbers that 
    # correspond to all segmentations in all ROIs:
    listOfUniqueSinds = []
    
    # Loop through each dataset:
    for i in range(len(listOfF2SindsBySeg)):
        f2sIndsBySeg = listOfF2SindsBySeg[i]
        
        uniqueSinds = get_unique_items(f2sIndsBySeg)
        
        listOfUniqueSinds.append(uniqueSinds)
        
        if len(uniqueSinds) > maxNumSlices:
            maxNumSlices = len(uniqueSinds)
    
    print(f'listOfF2SindsBySeg = {listOfF2SindsBySeg}')
    print(f'listOfUniqueSinds = {listOfUniqueSinds}')
    print(f'maxNumSlices = {maxNumSlices}')
    
    
    """ Prepare the figure. """
    
    # Set the number of subplot rows and columns:
    Ncols = len(listOfSegs)
    Nrows = maxNumSlices
    
    cMaps = ['Reds', 'Blues', 'Greens', 'Oranges', 'Purples']
    
    # Set the transparency of labelmaps to be overlaid over DICOMs:
    dcmAlpha = 0.2
    dcmAlpha = 0.5
    dcmAlpha = 0.7
    
    #segAlpha = 0.5
    segAlpha = 0.2
    
    if exportPlot:
        dpi = 120
    else:
        dpi = 80
        
    n = 1 # initialised sub-plot number
    
    if Ncols < 3:
        fig, ax = plt.subplots(
            Nrows, Ncols, figsize=(7*Ncols, 10*Nrows), dpi=dpi
            )
    else:
        fig, ax = plt.subplots(
            Nrows, Ncols, figsize=(4*Ncols, 7.5*Nrows), dpi=dpi
            )
    
    # Loop through each slice number (i.e. each row in the plot):
    for rowNum in range(maxNumSlices):
        # Loop through each data set:
        for i in range(len(listOfPixarrBySeg)):
            pixarrBySeg = listOfPixarrBySeg[i]
            f2sIndsBySeg = listOfF2SindsBySeg[i]
            uniqueSinds = listOfUniqueSinds[i]
            
            #dicomFpaths = listOfDcmFpaths[i]
            dicomPixarrs = listOfDcmPixarrs[i]
            IPPs = listOfImIPPs[i]
            #directions = listOfImDirections[i]
            #spacings = listOfImSpacings[i]
            plotTitle = listOfPlotTitles[i]
            #dicomDir = listOfDicomDirs[i]
            
            if p2c:
                print(f'\n   i = {i}')
                print(f'   plotTitle = {plotTitle}')
                print(f'   f2sIndsBySeg = {f2sIndsBySeg}')
                print(f'   uniqueSinds = {uniqueSinds}')
            
            # Continue if rowNum does not exceed the number of unique slice indeces:
            if rowNum < len(uniqueSinds):
                sInd = uniqueSinds[rowNum]
                
                ax = plt.subplot(Nrows, Ncols, n)
                
                #dicomPixarr = dcmread(dicomFpaths[sInd]).pixel_array
                dicomPixarr = dicomPixarrs[sInd]
                
                #im = ax.imshow(dicomPixarr, cmap=plt.cm.Greys_r)
                ax.imshow(dicomPixarr, cmap=plt.cm.Greys_r, alpha=dcmAlpha)
                
                IPP = IPPs[sInd]
                    
                # Loop through each segment:
                for s in range(len(f2sIndsBySeg)):
                    f2sInds = f2sIndsBySeg[s]
                    pixarr = pixarrBySeg[s]
                    
                    """ There are only len(cMaps) colormaps defined above. Wrap the 
                    segment index s if there are more segments than the number of 
                    defined colormaps. """
                    if s < len(cMaps):
                        cMap = cMaps[s]
                    else:
                        m = s//len(cMaps)
                        
                        cMap = cMaps[s - m*len(cMaps)]
                        
                    if sInd in f2sInds:
                        frameNums = [i for i, e in enumerate(f2sInds) if e==sInd]
                        
                        # Loop through all frame numbers:
                        for f in range(len(frameNums)):
                            frameNum = frameNums[f]
                        
                            frame = pixarr[frameNum]
                            
                            if p2c:
                                print(f'      SliceNum = {sInd} is in f2sInds')
                                print(f'      frameNum = {frameNum}')
                                #print(f'      Contour = {Contour}')
                                print(f'      frame.shape = {frame.shape}')
                        
                            #ax = plt.subplot(Nrows, Ncols, n)
                            #im = ax.imshow(frame, cmap=plt.cm.nipy_spectral, 
                            #               alpha=alpha)
                            ax.imshow(frame, cmap=cMap, alpha=segAlpha)
                            
                            #frameTxt = f'frame {frameNum}'
                        if len(frameNums) > 1:
                            frameTxt = f'frames {frameNums}'
                        else:
                            frameTxt = f'frame {frameNum}'
                            
                    else:
                        frameTxt = 'No frame'
                        
                        if p2c:
                            print(f'      sInd = {sInd} is NOT in f2sInds')
                        
                    sliceTxt = f'Slice {sInd}'
                    zPosTxt = f'z = {round(IPP[2], 2)} mm'
                    """ Title not displaying as expected using bold font with
                    Latex-style command:
                    plotTitle = plotTitle.replace(' ', '\:')
                    plotTitle = r"$\bf{{{x}}}$".format(x=plotTitle) \
                        + f'\n\n{sliceTxt}\n{frameTxt}\n{zPosTxt}'
                    #plotTitle = r"$\bf{plotTitle}$\," \
                    #            + f'\n\n{sliceTxt}\n{frameTxt}\n{zPosTxt}'
                    """
                    plotTitle = f'{plotTitle}\n\n {sliceTxt}\n{frameTxt}'\
                        + f'\n{zPosTxt}'
                        
                    ax.set_xlabel('Pixels', fontsize=fontSize)
                    ax.set_ylabel('Pixels', fontsize=fontSize)
                    ax.set_title(plotTitle, fontsize=fontSize)
                    
            n += 1 # increment sub-plot number
        
    
    if exportPlot:
        if exportDir == 'cwd':
            exportDir = os.getcwd()
        
        if not os.path.isdir(exportDir):
            #os.mkdir(exportDir)
            Path(exportDir).mkdir(parents=True)
        
        currentDateTime = time.strftime("%Y%m%d_%H%M%S", time.gmtime())
            
        #exportFname = currentDateTime + '_' + fname + '.jpg'
        
        if fname == '':
            exportFname = ''
            if runID:
                exportFname += runID + '_'
            if ('5' in useCaseToApply or forceReg):
                if useDroForTx:
                    exportFname += 'useDroForTx_'
                else:
                    exportFname += regTxName + '_'
                    exportFname += initMethod + '_'
            exportFname += resInterp + '_'
            
            #if fname:
            #    exportFname += fname + '_'
            
            exportFname += currentDateTime + '.jpg'
        else:
            exportFname = fname + '.jpg'
        
        exportFpath = os.path.join(exportDir, exportFname)
        
        plt.savefig(exportFpath, bbox_inches='tight')
        
        print(f'Plot exported to:\n {exportFpath}\n')
        
    return

def plot_pixarrs_from_list_of_segs_and_dicomDirs(
        listOfSegs, listOfDicomDirs, listOfPlotTitles,
        exportPlot=False, exportDir='cwd', runID='', useCaseToApply='',
        forceReg=False, useDroForTx=False, regTxName='', initMethod='', 
        resInterp='', fname='', p2c=False
        ):
    """ 
    02/06/2021
    
    Note:
        
    Modification of v1 that was previously called v3. Rather than plotting 
    allSliceNums = get_unique_items(listOfF2SindsBySeg)
    will just plot frames with segmentations since f2sInds for Src and Trg can 
    relate to very different depths, leading to a confusing plot.
    
    listOfSegs is a list (which could be of length 1) of SEG (Pydicom) objects.
    
    listOfDicomDirs is a list (which could be of length 1) of strings 
    containing the directory containing DICOMs that correspond to each SEG.
    
    listOfPlotTitles is a list (which could be of length 1) of text for each
    plot title.
    
    Note
    ----
    This function is useful when wanting to plot SEG overlays over DICOM pixel
    arrays that can be obtaind directly from DICOM files. If DICOM files are
    not available but SimpleITK Image representations are, use 
    plot_pixarrs_from_list_of_segs_and_images() instead.
    
    Plot has different DATASETS ALONG COLUMNS and different SLICES ALONG ROWS. 
    """
    
    listOfPixarrBySeg, listOfF2SindsBySeg, listOfImSizes, listOfImSpacings,\
        listOfImIPPs, listOfImDirections, listOfDicomFpaths\
            = get_seg_data_from_list_of_segs(listOfSegs, listOfDicomDirs, p2c)
    
    # Get a list of pixel arrays for each dicom for each dataset:
    listOfDicomPixarrs = []
    
    # Loop through each dataset:
    for i in range(len(listOfDicomFpaths)):
        fpaths = listOfDicomFpaths[i]
        pixarrs = []
        for fpath in fpaths:
            pixarrs.append(dcmread(fpath).pixel_array)
        listOfDicomPixarrs.append(pixarrs)
    
    plot_pixarrs_from_list_of_segs_and_dicomPixarrs(
        listOfSegs, listOfDicomPixarrs, listOfDicomDirs, listOfPlotTitles,
        exportPlot, exportDir, runID, useCaseToApply,
        forceReg, useDroForTx, regTxName, initMethod, 
        resInterp, fname, p2c
        )
        
    return

def plot_pixarrs_from_list_of_segs_and_images(
        listOfSegs, listOfImages, listOfDicomDirs, listOfPlotTitles,
        exportPlot=False, exportDir='cwd', runID='', useCaseToApply='',
        forceReg=False, useDroForTx=False, regTxName='', initMethod='', 
        resInterp='', fname='', fontSize=12, p2c=False
        ):
    """ 
    02/06/2021
    
    Note:
        
    Modification of v1 that was previously called v3. Rather than plotting 
    allSliceNums = get_unique_items(listOfF2SindsBySeg)
    will just plot frames with segmentations since f2sInds for Src and Trg can 
    relate to very different depths, leading to a confusing plot.
    
    listOfSegs is a list (which could be of length 1) of SEG (Pydicom) objects.
    
    listOfImages is a list (which could be of length 1) of 3D SimpleITK Image
    representations of the DICOMs.
    
    listOfDicomDirs is a list (which could be of length 1) of strings 
    containing the directory containing DICOMs that correspond to each SEG.
    
    listOfPlotTitles is a list (which could be of length 1) of text for each
    plot title.
    
    Note
    ----
    This function is needed (as opposed to 
    plot_pixarrs_from_list_of_segs_and_dicomDirs()) when wanting to plot SEG 
    overlays over DICOM pixel arrays that cannot be obtained from DICOM files
    (e.g. DICOMs are not exported following resampling/registering source to 
    target), but the SimpleITK Image is available.
    
    Plot has different DATASETS ALONG COLUMNS and different SLICES ALONG ROWS. 
    """
    
    listOfPixarrBySeg, listOfF2SindsBySeg, listOfImSizes, listOfImSpacings,\
        listOfImIPPs, listOfImDirections, listOfDicomFpaths\
            = get_seg_data_from_list_of_segs(listOfSegs, listOfDicomDirs, p2c)
    
    # Get a list of pixel arrays for each dicom for each dataset:
    listOfDicomPixarrs = []
    
    # Loop through each dataset:
    for i in range(len(listOfImages)):
        image = listOfImages[i]
        
        pixarr = im_to_pixarr(image)
        
        listOfDicomPixarrs.append(pixarr)
    
    plot_pixarrs_from_list_of_segs_and_dicomPixarrs(
        listOfSegs, listOfDicomPixarrs, listOfDicomDirs, listOfPlotTitles,
        exportPlot, exportDir, runID, useCaseToApply,
        forceReg, useDroForTx, regTxName, initMethod, 
        resInterp, fname, fontSize, p2c
        )
        
    return

def plot_list_of_labimByRoi_overlaid_on_dicom_ims_v1(
        listOfLabimByRoi, listOfDicomDir, listOfPlotTitles, listOfDicomIm=[],
        exportPlot=False, exportDir=None, fname='', p2c=False
        ):
    """ 
    listOfLabimByRoi is a list (for each dataset, which could be of length 1) 
    of a list (for each ROI/segment) of label images (SimpleITK Images).
    
    listOfDicomDir is a list (which could be of length 1) of a list of 
    strings containing the directories of DICOMs.
    
    listOfPlotTitles is a list (which could be of length 1) of text for each
    plot title.
    
    listOfDicomIm is a list (for each dataset, which could be of length 1) 
    of 3D SimpleITK Image representations of the DICOMs. This is optional, but
    if provided, the pixel data will be obtained from the 3D images rather than
    by importing DICOMs from the list of DICOM directories.
    
    Plot has different DATASETS ALONG COLUMNS and different SLICES ALONG ROWS. 
    """
    
    listOfPixarrByRoi, listOfF2SindsByRoi, listOfDicomFpaths,\
        listOfIPPs, listOfDirections, listOfSpacings\
        = get_seg_data_from_list_of_labimByRoi(
            listOfLabimByRoi, listOfDicomDir, p2c
            )
            
    """
    This is incomplete:
    if listOfDicomIm:
        
    else:
        listOfPixarrByRoi, listOfF2SindsByRoi, listOfDicomFpaths,\
            listOfIPPs, listOfDirections, listOfSpacings\
            = get_seg_data_from_list_of_labimByRoi(
                listOfLabimByRoi, listOfDicomDir, p2c
                )
    """
    
    """
    print(f'\nlen(listOfPixarrByRoi) = {len(listOfPixarrByRoi)}')
    print(f'len(listOfF2SindsByRoi) = {len(listOfF2SindsByRoi)}')
    print(f'len(listOfDicomFpaths) = {len(listOfDicomFpaths)}')
    print(f'listOfF2SindsByRoi = {listOfF2SindsByRoi}\n')
    
    print(f'listOfF2SindsByRoi[0]) = {listOfF2SindsByRoi[0]}\n')
    #print(f'listOfF2SindsByRoi[0][15]) = {listOfF2SindsByRoi[0][15]}\n')
    print(f'listOfF2SindsByRoi[1]) = {listOfF2SindsByRoi[1]}\n')
    #print(f'listOfF2SindsByRoi[1][8]) = {listOfF2SindsByRoi[1][8]}\n')
    print(f'listOfF2SindsByRoi[2]) = {listOfF2SindsByRoi[2]}\n')
    #print(f'listOfF2SindsByRoi[2][7]) = {listOfF2SindsByRoi[2][7]}\n')
    """
    
    # Get the maximum number of slices containing segmentations in any ROI in 
    # any dataset:
    maxNumSlices = 0
    
    # The list (for each dataset) of the unique set of slice numbers that 
    # correspond to all segmentations in all ROIs:
    listOfUniqueSinds = []
    
    # Loop through each dataset:
    for i in range(len(listOfF2SindsByRoi)):
        f2sIndsByRoi = listOfF2SindsByRoi[i]
        
        uniqueSinds = get_unique_items(f2sIndsByRoi)
        
        listOfUniqueSinds.append(uniqueSinds)
        
        if len(uniqueSinds) > maxNumSlices:
            maxNumSlices = len(uniqueSinds)
    
    """
    print(f'listOfF2SindsByRoi = {listOfF2SindsByRoi}')
    print(f'listOfUniqueSinds = {listOfUniqueSinds}')
    print(f'maxNumSlices = {maxNumSlices}')
    """
    
    """ Prepare the figure. """
    
    # Set the number of subplot rows and columns:
    Ncols = len(listOfLabimByRoi)
    Nrows = maxNumSlices
    
    cMaps = ['Reds', 'Blues', 'Greens', 'Oranges', 'Purples']
    
    # Set the transparency of labelmaps to be overlaid over DICOMs:
    dcmAlpha = 0.2
    dcmAlpha = 0.5
    #dcmAlpha = 1
    
    segAlpha = 0.5
    #segAlpha = 0.2
    
    if exportPlot:
        dpi = 120
    else:
        dpi = 80
        
    n = 1 # initialised sub-plot number
    
    if Ncols < 3:
        fig, ax = plt.subplots(
            Nrows, Ncols, figsize=(7*Ncols, 9*Nrows), dpi=dpi
            )
    else:
        fig, ax = plt.subplots(
            Nrows, Ncols, figsize=(4*Ncols, 7.5*Nrows), dpi=dpi
            )
    
    # Loop through each slice/frame number (i.e. each row in the plot):
    for rowNum in range(maxNumSlices):
        # Loop through each data set:
        for i in range(len(listOfPixarrByRoi)):
            pixarrByRoi = listOfPixarrByRoi[i]
            f2sIndsByRoi = listOfF2SindsByRoi[i]
            uniqueSinds = listOfUniqueSinds[i]
            
            dicomFpaths = listOfDicomFpaths[i]
            IPPs = listOfIPPs[i]
            #origin = listOfOrigins[i]
            #directions = listOfDirections[i]
            #spacings = listOfSpacings[i]
            plotTitle = listOfPlotTitles[i]
            #dicomDir = listOfDicomDir[i]
            
            if p2c:
                print(f'\n   i = {i}')
                print(f'   plotTitle = {plotTitle}')
                print(f'   f2sIndsByRoi = {f2sIndsByRoi}')
                print(f'   uniqueSinds = {uniqueSinds}')
            
            # Continue if rowNum does not exceed the number of unique slice indeces:
            if rowNum < len(uniqueSinds):
                Sind = uniqueSinds[rowNum]
                
                ax = plt.subplot(Nrows, Ncols, n)
                
                dicomPixarr = dcmread(dicomFpaths[Sind]).pixel_array
                """
                This is incomplete:
                if listOfDicomIm:
                    dicomPixarr = 
                else:
                    dicomPixarr = dcmread(dicomFpaths[Sind]).pixel_array
                """
                
                #im = ax.imshow(dicomPixarr, cmap=plt.cm.Greys_r)
                ax.imshow(dicomPixarr, cmap=plt.cm.Greys_r, alpha=dcmAlpha)
                
                IPP = IPPs[Sind]
                
                if p2c:
                    print(f'   Sind = {Sind}')
                    print(f'   IPP = {IPP}')
                    
                # Loop through each ROI/segment:
                for s in range(len(f2sIndsByRoi)):
                    f2sInds = f2sIndsByRoi[s]
                    pixarr = pixarrByRoi[s]
                    
                    """ There are only len(cMaps) colormaps defined above. Wrap the 
                    segment index s if there are more segments than the number of 
                    defined colormaps. """
                    if s < len(cMaps):
                        cMap = cMaps[s]
                    else:
                        m = s//len(cMaps)
                        
                        cMap = cMaps[s - m*len(cMaps)]
                        
                    if Sind in f2sInds:
                        frameNums = [i for i, e in enumerate(f2sInds) if e==Sind]
                        
                        # Loop through all frame numbers:
                        for f in range(len(frameNums)):
                            frameNum = frameNums[f]
                        
                            frame = pixarr[frameNum]
                            
                            if p2c:
                                print(f'      SliceNum = {Sind} is in f2sInds')
                                print(f'      frameNum = {frameNum}')
                                #print(f'      Contour = {Contour}')
                                print(f'      frame.shape = {frame.shape}')
                        
                            #ax = plt.subplot(Nrows, Ncols, n)
                            #im = ax.imshow(frame, cmap=plt.cm.nipy_spectral, 
                            #               alpha=alpha)
                            ax.imshow(frame, cmap=cMap, alpha=segAlpha)
                            
                            #frameTxt = f'Frame {frameNum}'
                        if len(frameNums) > 1:
                            frameTxt = f'Frames {frameNums}'
                        else:
                            frameTxt = f'Frame {frameNum}'
                            
                    else:
                        frameTxt = 'No frame'
                        
                        if p2c:
                            print(f'      Sind = {Sind} is NOT in f2sInds')
                        
                    sliceTxt = f'Slice {Sind}'
                    zPosTxt = f'z = {round(IPP[2], 2)} mm'
                    plotTitle = plotTitle.replace(' ', '\:')
                    plotTitle = r"$\bf{{{x}}}$".format(x=plotTitle) \
                                + f'\n\n{sliceTxt}\n{frameTxt}\n{zPosTxt}'
                    #plotTitle = r"$\bf{plotTitle}$\," \
                    #            + f'\n\n{sliceTxt}\n{frameTxt}\n{zPosTxt}'
                    
                    ax.set_xlabel('Pixels'); ax.set_ylabel('Pixels')
                    ax.set_title(plotTitle)
                    
            n += 1 # increment sub-plot number
        
    
    if exportPlot:
        if exportDir == 'cwd':
            exportDir = os.getcwd()
        
        if not os.path.isdir(exportDir):
            #os.mkdir(exportDir)
            Path(exportDir).mkdir(parents=True)
        
        if fname == '':
            currentDateTime = time.strftime("%Y%m%d_%H%M%S", time.gmtime())
        
            exportFname = currentDateTime + '_' + fname + '.jpg'
        else:
            exportFname = fname + '.jpg'
        
        exportFpath = os.path.join(exportDir, exportFname)
        
        plt.savefig(exportFpath, bbox_inches='tight')
        
        print(f'Plot exported to:\n {exportFpath}\n')
        
    return

def plot_list_of_pixarrBySeg_overlaid_on_dicom_ims(
        listOfPixarrBySeg, listOfF2SindsBySeg, listOfDicomIm, listOfIPPs,
        listOfPlotTitles, exportPlot=False, exportDir=None, fname='', p2c=False
        ):
    """ 
    listOfPixarrBySeg is a list (for each dataset, which could be of length 1) 
    of a list (for each ROI/segment) of Numpy pixel arrays.
    
    listOfF2SindsBySeg is a list (for each dataset, which could be of length 1)
    of a list (for each SEG) of a list (for each segmentation) of the 
    corresponding slice index in the DICOM series.
    
    listOfDicomIm is a list (for each dataset, which could be of length 1) 
    of 3D SimpleITK Image representations of the DICOMs. This is optional, but
    if provided, the pixel data will be obtained from the 3D images rather than
    by importing DICOMs from the list of DICOM directories.
    
    listOfIPPs is a list (for each dataset, which could be of length 1) of a
    list (for each DICOM) of the ImagePositionPatient.
    
    listOfPlotTitles is a list (which could be of length 1) of text for each
    plot title.
    
    Plot has different DATASETS ALONG COLUMNS and different SLICES ALONG ROWS. 
    """
    
    
    """
    print(f'\nlen(listOfPixarrBySeg) = {len(listOfPixarrBySeg)}')
    print(f'len(listOfF2SindsBySeg) = {len(listOfF2SindsBySeg)}')
    print(f'len(listOfDicomFpaths) = {len(listOfDicomFpaths)}')
    print(f'listOfF2SindsBySeg = {listOfF2SindsBySeg}\n')
    
    print(f'listOfF2SindsBySeg[0]) = {listOfF2SindsBySeg[0]}\n')
    #print(f'listOfF2SindsBySeg[0][15]) = {listOfF2SindsBySeg[0][15]}\n')
    print(f'listOfF2SindsBySeg[1]) = {listOfF2SindsBySeg[1]}\n')
    #print(f'listOfF2SindsBySeg[1][8]) = {listOfF2SindsBySeg[1][8]}\n')
    print(f'listOfF2SindsBySeg[2]) = {listOfF2SindsBySeg[2]}\n')
    #print(f'listOfF2SindsBySeg[2][7]) = {listOfF2SindsBySeg[2][7]}\n')
    """
    
    # Get the maximum number of slices containing segmentations in any ROI in 
    # any dataset:
    maxNumSlices = 0
    
    # The list (for each dataset) of the unique set of slice numbers that 
    # correspond to all segmentations in all ROIs:
    listOfUniqueSinds = []
    
    # Loop through each dataset:
    for i in range(len(listOfF2SindsBySeg)):
        f2sIndsByRoi = listOfF2SindsBySeg[i]
        
        uniqueSinds = get_unique_items(f2sIndsByRoi)
        
        listOfUniqueSinds.append(uniqueSinds)
        
        if len(uniqueSinds) > maxNumSlices:
            maxNumSlices = len(uniqueSinds)
    
    """
    print(f'listOfF2SindsBySeg = {listOfF2SindsBySeg}')
    print(f'listOfUniqueSinds = {listOfUniqueSinds}')
    print(f'maxNumSlices = {maxNumSlices}')
    """
    
    """ Prepare the figure. """
    
    # Set the number of subplot rows and columns:
    Ncols = len(listOfPixarrBySeg)
    Nrows = maxNumSlices
    
    cMaps = ['Reds', 'Blues', 'Greens', 'Oranges', 'Purples']
    
    # Set the transparency of labelmaps to be overlaid over DICOMs:
    dcmAlpha = 0.2
    dcmAlpha = 0.5
    #dcmAlpha = 1
    
    segAlpha = 0.5
    #segAlpha = 0.2
    
    if exportPlot:
        dpi = 120
    else:
        dpi = 80
        
    n = 1 # initialised sub-plot number
    
    if Ncols < 3:
        fig, ax = plt.subplots(
            Nrows, Ncols, figsize=(7*Ncols, 9*Nrows), dpi=dpi
            )
    else:
        fig, ax = plt.subplots(
            Nrows, Ncols, figsize=(4*Ncols, 7.5*Nrows), dpi=dpi
            )
    
    # Loop through each slice/frame number (i.e. each row in the plot):
    for rowNum in range(maxNumSlices):
        # Loop through each data set:
        for i in range(len(listOfPixarrBySeg)):
            pixarrBySeg = listOfPixarrBySeg[i]
            f2sIndsBySeg = listOfF2SindsBySeg[i]
            uniqueSinds = listOfUniqueSinds[i]
            dicomIm = listOfDicomIm[i]
            dicom3dPixarr = sitk.GetArrayViewFromImage(dicomIm)
            
            #dicomFpaths = listOfDicomFpaths[i]
            IPPs = listOfIPPs[i]
            #origin = listOfOrigins[i]
            #directions = listOfDirections[i]
            #spacings = listOfSpacings[i]
            plotTitle = listOfPlotTitles[i]
            #dicomDir = listOfDicomDir[i]
            
            if p2c:
                print(f'\n   i = {i}')
                print(f'   plotTitle = {plotTitle}')
                print(f'   f2sIndsBySeg = {f2sIndsBySeg}')
                print(f'   uniqueSinds = {uniqueSinds}')
            
            # Continue if rowNum does not exceed the number of unique slice indeces:
            if rowNum < len(uniqueSinds):
                Sind = uniqueSinds[rowNum]
                
                ax = plt.subplot(Nrows, Ncols, n)
                
                #dicomPixarr = dcmread(dicomFpaths[Sind]).pixel_array
                dicom2dPixarr = dicom3dPixarr[Sind]
                
                #im = ax.imshow(dicomPixarr, cmap=plt.cm.Greys_r)
                ax.imshow(dicom2dPixarr, cmap=plt.cm.Greys_r, alpha=dcmAlpha)
                
                IPP = IPPs[Sind]
                
                if p2c:
                    print(f'   Sind = {Sind}')
                    print(f'   IPP = {IPP}')
                    
                # Loop through each ROI/segment:
                for s in range(len(f2sIndsBySeg)):
                    f2sInds = f2sIndsBySeg[s]
                    segPixarr = pixarrBySeg[s]
                    
                    """ 
                    There are only len(cMaps) colormaps defined above. Wrap the 
                    segment index s if there are more segments than the number 
                    of defined colormaps.
                    """
                    if s < len(cMaps):
                        cMap = cMaps[s]
                    else:
                        m = s//len(cMaps)
                        
                        cMap = cMaps[s - m*len(cMaps)]
                        
                    if Sind in f2sInds:
                        frameNums = [
                            i for i, e in enumerate(f2sInds) if e==Sind
                            ]
                        
                        # Loop through all frame numbers:
                        for f in range(len(frameNums)):
                            frameNum = frameNums[f]
                        
                            frame = segPixarr[frameNum]
                            
                            if p2c:
                                print(f'      SliceNum = {Sind} is in f2sInds')
                                print(f'      frameNum = {frameNum}')
                                #print(f'      Contour = {Contour}')
                                print(f'      frame.shape = {frame.shape}')
                        
                            #ax = plt.subplot(Nrows, Ncols, n)
                            #im = ax.imshow(frame, cmap=plt.cm.nipy_spectral, 
                            #               alpha=alpha)
                            ax.imshow(frame, cmap=cMap, alpha=segAlpha)
                            
                            #frameTxt = f'Frame {frameNum}'
                        if len(frameNums) > 1:
                            frameTxt = f'Frames {frameNums}'
                        else:
                            frameTxt = f'Frame {frameNum}'
                            
                    else:
                        frameTxt = 'No frame'
                        
                        if p2c:
                            print(f'      Sind = {Sind} is NOT in f2sInds')
                        
                    sliceTxt = f'Slice {Sind}'
                    zPosTxt = f'z = {round(IPP[2], 2)} mm'
                    plotTitle = plotTitle.replace(' ', '\:')
                    plotTitle = r"$\bf{{{x}}}$".format(x=plotTitle) \
                                + f'\n\n{sliceTxt}\n{frameTxt}\n{zPosTxt}'
                    #plotTitle = r"$\bf{plotTitle}$\," \
                    #            + f'\n\n{sliceTxt}\n{frameTxt}\n{zPosTxt}'
                    
                    ax.set_xlabel('Pixels'); ax.set_ylabel('Pixels')
                    ax.set_title(plotTitle)
                    
            n += 1 # increment sub-plot number
        
    
    if exportPlot:
        if exportDir == 'cwd':
            exportDir = os.getcwd()
        
        if not os.path.isdir(exportDir):
            #os.mkdir(exportDir)
            Path(exportDir).mkdir(parents=True)
        
        if fname == '':
            currentDateTime = time.strftime("%Y%m%d_%H%M%S", time.gmtime())
        
            exportFname = currentDateTime + '_' + fname + '.jpg'
        else:
            exportFname = fname + '.jpg'
        
        exportFpath = os.path.join(exportDir, exportFname)
        
        plt.savefig(exportFpath, bbox_inches='tight')
        
        print(f'Plot exported to:\n {exportFpath}\n')
        
    return

def plot_list_of_labimBySeg_overlaid_on_dicom_ims(
        listOfLabimBySeg, listOfF2SindsBySeg, listOfDicomIm, listOfIPPs,
        listOfPlotTitles, exportPlot=False, exportDir=None, fname='', p2c=False
        ):
    """ 
    listOfLabimByRoi is a list (for each dataset, which could be of length 1) 
    of a list (for each ROI/segment) of label images (SimpleITK Images).
    
    listOfF2SindsBySeg is a list (for each dataset, which could be of length 1)
    of a list (for each SEG) of a list (for each segmentation) of the 
    corresponding slice index in the DICOM series.
    
    listOfDicomIm is a list (for each dataset, which could be of length 1) 
    of 3D SimpleITK Image representations of the DICOMs. This is optional, but
    if provided, the pixel data will be obtained from the 3D images rather than
    by importing DICOMs from the list of DICOM directories.
    
    listOfIPPs is a list (for each dataset, which could be of length 1) of a
    list (for each DICOM) of the ImagePositionPatient.
    
    listOfPlotTitles is a list (which could be of length 1) of text for each
    plot title.
    
    Plot has different DATASETS ALONG COLUMNS and different SLICES ALONG ROWS. 
    """
    
    listOfPixarrBySeg = []
    listOfF2SindsBySeg_conversion = []
    
    for im in listOfLabimBySeg:
        pixarrBySeg, f2sIndsBySeg = imBySeg_to_pixarrBySeg(im)
            
        listOfPixarrBySeg.append(pixarrBySeg)
        listOfF2SindsBySeg_conversion.append(f2sIndsBySeg)
    
    """
    Note that the list of f2sIndsBySeg from the conversion from labim to 
    pixarr will not necessarily be the same as the original list of f2sIndsBySeg
    (or c2sIndsByRoi if the pixarr used to create the labim came from converting
    ptsByCntByRoi to pixarrBySeg), because in the process of converting from
    pixarr to labim, any existence of multiple frames in pixarr that related to
    the same slice index were combined to a single frame in the labim - hence
    knowledge of multiple segmentations on any slice is "lost" during the 
    conversion to labim. Hence f2sIndsBySeg returned from imBySeg_to_pixarrBySeg
    may have fewer items than the original list of f2sIndsBySeg (or c2sIndsByRoi).
    """
    print_labimBySeg(listOfLabimBySeg[0])
    print_pixarrBySeg(listOfPixarrBySeg[0])
    
    print('\nOriginal list of f2sIndsBySeg (from input parameter):')
    print_indsByRoi(listOfF2SindsBySeg[0])
    
    print('\nList of f2sIndsBySeg from conversion from labim to pixarr:')
    print_indsByRoi(listOfF2SindsBySeg_conversion[0])
    
    plot_list_of_pixarrBySeg_overlaid_on_dicom_ims(
        listOfPixarrBySeg, listOfF2SindsBySeg, listOfDicomIm, listOfIPPs,
        listOfPlotTitles, exportPlot=False, exportDir=exportDir, fname=fname, p2c=p2c
        )

def plot_labim_over_dicom_im(dicomIm, labim, dpi=80, p2c=False):
    """ 
     
    """
    
    dicomPixarr, dicomF2Sinds = im_to_pixarr(dicomIm)
    dicomF, dicomR, dicomC = dicomPixarr.shape
    
    labPixarr, labF2Sinds = im_to_pixarr(labim)
    labF, labR, labC = labPixarr.shape
    
    if p2c:
        print(f'\ndicomPixarr.shape = {dicomPixarr.shape}')
        print(f'dicomF2Sinds = {dicomF2Sinds}')
        
        print(f'\nlabPixarr.shape = {labPixarr.shape}')
        print(f'labF2Sinds = {labF2Sinds}')
    
    #if colormap == 'color':
    #    cmap = plt.cm.nipy_spectral
    #else:
    #    cmap = plt.cm.Greys_r
    
    # Colormap for labelmaps:
    cMap = plt.cm.nipy_spectral
    #cMap = plt.cm.hsv
    #cMap = plt.cm.gist_rainbow
    
    # Set the transparency of labelmaps to be overlaid over DICOMs:
    #alpha = 0.2
    alpha = 0.5
    
    # Set the number of subplot rows and columns:
    Ncols = 1
    Nrows = labF
    
    fig, ax = plt.subplots(Nrows, Ncols, figsize=(5*Ncols, 8*Nrows), dpi=dpi)
        
    n = 1 # initialised sub-plot number
    
    for f in range(labF):
        ax = plt.subplot(Nrows, Ncols, n)
        
        # The DICOM slice number:
        s = labF2Sinds[f]
        
        #ax.imshow(dicomPixarr[s], cmap=plt.cm.Greys_r)
        ax.imshow(dicomPixarr[s], cmap=plt.cm.Greys_r, alpha=alpha)
        
        ax.imshow(labPixarr[f], cmap=cMap, alpha=alpha)
                
        ax.set_xlabel('Pixels'); ax.set_ylabel('Pixels')
        ax.set_title(f'Frame = {f}, Slice {s}')
                
        n += 1 # increment sub-plot number
        
    return
