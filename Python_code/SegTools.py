# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 11:54:12 2020

@author: ctorti
"""




# Import packages and functions:
#import os
#import time
#from copy import deepcopy
#import pydicom
#from pydicom.pixel_data_handlers.numpy_handler import pack_bits
#from pydicom.uid import generate_uid
#import numpy as np
#import SimpleITK as sitk




"""
******************************************************************************
******************************************************************************
SEGMENT FUNCTIONS
******************************************************************************
******************************************************************************
"""      


def ProportionOfPixArrInExtent(PixArr, FrameToSliceInds, SrcDicomDir, 
                               TrgDicomDir, LogToConsole=False):
    """
    COMMENT 29/01/2021:
        I was using the same image (i.e. same DICOM directory) to generate the
        pixel array (i.e. PixArr2PtsByContour()) and to generate the vertices
        (i.e. GetImageVertices()).  The former had to be the source DICOMs and
        the latter the target DICOMs.
        
    
    Determine what proportion of voxels that make up a 3D pixel array intersect
    with the 3D volume of a 3D image.
    
    Inputs:
    ******
    
    PixArr : Numpy array with dimensions Z x Y x X where Z may be 1
        The pixel array that may represent a mask or labelmap.
    
    FrameToSliceInds : List of list of integers
        A list (for each frame) of the slice numbers that correspond to each 
        frame in PixArr.  This is equivalent to a list of Per-Frame Functional 
        Groups Sequence-to-slice inds (PFFGStoSliceInds). 
        
    SrcDicomDir : string
        Directory containing the DICOMs that relate to PixArr.
    
    TrgDicomDir : string
        Directory containing the DICOMs that relate to the image grid/extent
        within which the test is for.
    
    LogToConsole : boolean (optional; False by default)
        Denotes whether intermediate results will be logged to the console.
        
        
    Outputs:
    *******
    
    FracProp : float
        The fractional proportion (normalised to 1) of voxels in PixArr that 
        intersect the extent of RefImage.
    """
    
    from ConversionTools import PixArr2PtsByContour
    from ImageTools import ImportImage, GetImageVertices
    from GeneralTools import IsPointInPolygon
    
    F, R, C = PixArr.shape
    
    # Convert the pixel array to a list (for each frame in PixArr) of a list 
    # (for each point) of a list (for each dimension) of physical coordinates:
    PtsByObjByFrame,\
    CntDataByObjByFrame = PixArr2PtsByContour(PixArr, 
                                              FrameToSliceInds, 
                                              SrcDicomDir)
    
    Image = ImportImage(TrgDicomDir)
    
    Vertices = GetImageVertices(Image)
    
    IsInside = []
    
    for f in range(len(PtsByObjByFrame)):
        for o in range(len(PtsByObjByFrame[f])):
            for pt in PtsByObjByFrame[f][o]:
                IsInside.append(IsPointInPolygon(pt, Vertices))
    
    FracProp = sum(IsInside)/len(IsInside)
    
    if LogToConsole:
        print('\n\n\nFunction ProportionOfPixArrInExtent():')
        print(f'   PixArr has {F}x{R}x{C} (FxRxC)')
        print(f'   FrameToSliceInds = {FrameToSliceInds}')
        print(f'   len(PtsByObjByFrame) = {len(PtsByObjByFrame)}')
        print(f'   len(CntDataByObjByFrame) = {len(CntDataByObjByFrame)}')
        for f in range(len(PtsByObjByFrame)):
            print(f'   Frame {f} has {len(PtsByObjByFrame[f])} objects')
            for o in range(len(PtsByObjByFrame[f])):
                print(f'      Object {o} has {len(PtsByObjByFrame[f][o])} points')
                ##print(f'   len(CntDataByFrame[{i}]) = {len(CntDataByFrame[i])}')
        #print(f'   \nPtsByFrame = {PtsByFrame}')
        #print(f'   \nCntDataByFrame = {CntDataByFrame}')
        
        if False:
            print(f'\n   The vertices of the image grid:')
            for i in range(len(Vertices)):
                print(f'   {Vertices[i]}')
            
            print(f'\n   The points from the input indices:')
            for i in range(len(PtsByObjByFrame[f][o])):
                print(f'   {PtsByObjByFrame[f][o][i]}')
                
            print(f'\n   len(IsInside) = {len(IsInside)}')
            print(f'   sum(IsInside) = {sum(IsInside)}')
            
        if FracProp < 1:
            print(f'\n   The vertices of the image grid:')
            for i in range(len(Vertices)):
                print(f'   {Vertices[i]}')
            N = len(IsInside)
            limit = 10
            if N > limit:
                print(f'\n   The first {limit} points that lie outside of extent:')
                #print([f'\n   {PtsByObjByFrame[0][0][i]}' for i in range(5)])
                for i in range(limit):
                    print(f'   {PtsByObjByFrame[0][0][i]}')
            else:
                print(f'\n   The first {N} points that lie outside of extent:')
                #print([f'\n   {PtsByObjByFrame[0][0][i]}' for i in range(N)])
                for i in range(N):
                    print(f'   {PtsByObjByFrame[0][0][i]}')
    
    return FracProp






def ProportionOfSegsInExtent(PixArrByRoi, F2SindsByRoi, SrcDicomDir, 
                             TrgDicomDir, LogToConsole=False):
    """
    COMMENT 29/01/2021:
        I was using the same image (i.e. same DICOM directory) to generate the
        pixel array (i.e. PixArr2PtsByContour()) and to generate the vertices
        (i.e. GetImageVertices()).  The former had to be the source DICOMs and
        the latter the target DICOMs.
        
    
    Determine what proportion of voxels that make up a list of 3D pixel arrays 
    intersect with the 3D volume of a 3D image.
    
    Inputs:
    ******
    
    PixArrByRoi : list of Numpy arrays
        A list (for each ROI) of a FxRxC (frames x rows x cols) Numpy array 
        containing F RxC masks in each pixel array.
    
    F2SindsByRoi : List of list of integers
        A list (for each ROI) of a list (for each frame) of the slice numbers 
        that correspond to each frame in each pixel array in PixArrByRoi.  This
        is equivalent to a list of Per-FrameFunctionalGroupsSequence-to-slice 
        indices (PFFGStoSliceInds). 
        
    SrcDicomDir : string
        Directory containing the DICOMs that relate to PixArr.
    
    TrgDicomDir : string
        Directory containing the DICOMs that relate to the image grid/extent
        within which the test is for.
    
    LogToConsole : boolean (optional; False by default)
        Denotes whether intermediate results will be logged to the console.
        
        
    Outputs:
    *******
    
    FracProp : float
        The fractional proportion (normalised to 1) of voxels in PixArr that 
        intersect the extent of RefImage.
    """
    
    from ConversionTools import PixArrByRoi2PtsByCntByRoi
    from RtsTools import ProportionOfRoisInExtent
    
    # Convert the list of pixel arrays-by-ROI to a list of 
    # points-by-contour-by-ROI:
    PtsByCntByRoi, CntDataByCntByRoi,\
    C2SindsByRoi = PixArrByRoi2PtsByCntByRoi(PixArrByRoi, F2SindsByRoi, 
                                             SrcDicomDir, Thresh=0.5)
    
    FracProp = ProportionOfRoisInExtent(PtsByCntByRoi, TrgDicomDir, 
                                        LogToConsole)
    
    return FracProp








def GetFrameNums(Seg, SearchString, DicomDir):
    """
    Get the frame number(s) in a SEG's pixel array that matches the segment 
    label provided.
    
    Inputs:
    ******
    
    Seg : Pydicom object
        SEG object.
        
    SearchString : string
        All or part of the Segment Label containing the segmentation of
        interest.
    
    DicomDir : string
        Directory containing the corresponding DICOMs.
    
                            
    Outputs:
    *******
    
    FrameNums : list of integer
        List of the frame numbers that correspond to all frames in the SEG's 
        pixel array that belongs to the segment of interest.  If only one frame 
        corresponds to the segment, the returned list will be of length one 
        (e.g. [3]).
        
    PFFGStoSliceInds : list of integers
        List of the slice numbers that correspond to each Per-frame Functional 
        Groups Sequence in the segment of interest. 
    """
    
    from DicomTools import GetDicomSOPuids
    from DicomTools import GetRoiNum
    
    # Get the DimensionIndexValues (DIVs) and group the DIVs by segment.
    """ Note:  The DIVs are integers that start from 1. """
    DIVs = GetDIVs(Seg)
    
    # Get the DICOM SOP UIDs:
    SOPuids = GetDicomSOPuids(DicomDir)
    
    # Get the PerFrameFunctionalGroupsSequence-to-slice indices
    # (PFFGStoSliceInds) and PFFGStoSliceInds grouped by segment
    # (PFFGStoSliceIndsBySeg):
    """ Note:  The PFFGStoSliceInds are integers that start from 0. """
    PFFGStoSliceInds = GetPFFGStoSliceInds(Seg, SOPuids)
    
    PFFGStoSliceIndsBySeg = GroupListBySegment(ListToGroup=PFFGStoSliceInds, 
                                               DIVs=DIVs)
    
    SegNum = GetRoiNum(Seg, SearchString)
    
    # The PFFGStoSliceInds for the segment of interest:
    PFFGStoSliceInds = PFFGStoSliceIndsBySeg[SegNum]
    
    # The number of segments:
    S = len(PFFGStoSliceIndsBySeg)
    
    # The number of frames in the segment of interest:
    F = len(PFFGStoSliceInds)
    
    n = 0 # initialise frame number counter
    
    FrameNums = []
    
    for s in range(S):
        if s == SegNum:
            """ 
            This segment contains the frame(s) of interest, which are given by
            the index of PFFGStoSliceInds[f] in PFFGStoSliceIndsBySeg[s] plus 
            any frames that preceeded it (i.e. the frame counter n).
            """
            
            for f in range(F):
                FrameNum = n + PFFGStoSliceIndsBySeg[s].index(PFFGStoSliceInds[f])
                
                FrameNums.append(FrameNum)
            
        else:
            # Add to the frame counter the number of frames in this segment:
            n += len(PFFGStoSliceIndsBySeg[s])
    
    return FrameNums, PFFGStoSliceInds








def GetRSOPuidsInRIS(Seg):
    """
    Get the list of ReferencedSOPInstanceUIDs in the ReferencedInstanceSequence
    of a SEG.
    
    Inputs:
    ******
        
    Seg : Pydicom object
        ROI object from a SEG file.
    
        
    Outputs:
    *******
        
    RSOPuids : list of strings
        List of ReferencedSOPInstanceUIDs.
    """
    
    RSOPuids = [] 
    
    sequences = Seg.ReferencedSeriesSequence[0]\
                   .ReferencedInstanceSequence
    
    for sequence in sequences:
        uid = sequence.ReferencedSOPInstanceUID
        
        RSOPuids.append(uid)
        
    return RSOPuids





def GetRIStoSliceInds(Seg, SOPuids):
    """
    Get the slice numbers that correspond to each ReferencedInstanceSequence
    in a SEG.
    
    Inputs:
    ******
    
    Seg : Pydicom object
        ROI object from a SEG file.
        
    SOPuids : list of strings
        List of SOPInstanceUIDs of the DICOMs.
        
    
    Outputs:
    *******
    
    RIStoSliceInds : list of integers
        Slice numbers that correspond to each ReferencedInstanceSequence in 
        Seg.
    """
    
    # Get the list of Referenced SOP Instance UIDs:
    RSOPuids = GetRSOPuidsInRIS(Seg)
    
    RIStoSliceInds = [] 
    
    for Ruid in RSOPuids:
        # Find the matching index of Ruid in SOPuids:
        RIStoSliceInds.append(SOPuids.index(Ruid))
        
    return RIStoSliceInds





def GetRSOPuidsInPFFGS(Seg):
    """
    Get the list of ReferencedSOPInstanceUIDs in the 
    Per-FrameFunctionalGroupsSequence of a SEG.
    
    Inputs:
    ******
        
    Seg : Pydicom object
        ROI object from a SEG file.
    
        
    Outputs:
    *******
    
    RSOPuids : list of strings
        List of ReferencedSOPUIDs.
    """
    
    RSOPuids = [] 
    
    sequences = Seg.PerFrameFunctionalGroupsSequence
    
    for sequence in sequences:
        uid = sequence.DerivationImageSequence[0]\
                      .SourceImageSequence[0]\
                      .ReferencedSOPInstanceUID
        
        RSOPuids.append(uid)
        
    return RSOPuids





def GetPFFGStoSliceInds(Seg, SOPuids):
    """
    Get a list of the slice numbers that correspond to each  
    Per-FrameFunctionalGroupsSequence in a SEG.
    
    Inputs:
    ******
        
    Seg : Pydcom object
        ROI object from a SEG file.
        
    SOPuids : list of strings
        SOPInstanceUIDs of the DICOMs.
        
    
    Outputs:
    *******
        
    PFFGStoSliceInds : list of integers
        List (for each frame) of the slice numbers that correspond to each 
        Per-FrameFunctionalGroupsSequence in Seg.
    """
    
    # Get the list of Referenced SOP Instance UIDs:
    RSOPuids = GetRSOPuidsInPFFGS(Seg)
    
    PFFGStoSliceInds = [] 
    
    for Ruid in RSOPuids:
        # Find the matching index of Ruid in SOPuids:
        PFFGStoSliceInds.append(SOPuids.index(Ruid))
        
    return PFFGStoSliceInds







def GetPFFGStoSliceIndsBySeg(Seg, SOPuids):
    """
    Get a list (per segment) of the slice numbers that correspond to each 
    Per-FrameFunctionalGroupsSequence in a SEG.
    
    Inputs:
    ******
        
    Seg : Pydcom object
        ROI object from a SEG file.
        
    SOPuids : list of strings
        SOPInstanceUIDs of the DICOMs.
        
    
    Outputs:
    *******
        
    PFFGStoSliceIndsBySeg : list of a list of integers
        List (for each segment) of a list (for each frame) of the slice numbers 
        that correspond to each Per-FrameFunctionalGroupsSequence in Seg.
    """
    
    PFFGStoSliceInds = GetPFFGStoSliceInds(Seg, SOPuids)
    
    DIVs = GetDIVs(Seg)
    
    PFFGStoSliceIndsBySeg = GroupListBySegment(ListToGroup=PFFGStoSliceInds, 
                                               DIVs=DIVs)
    
    return PFFGStoSliceIndsBySeg






    
    
def GetDIVs(Seg):
    """
    Get the DimensionIndexValues in a SEG.
    
    Inputs:
    ******
    
    Seg : Pydicom object
        ROI object from a SEG file.
        
        
    Outputs:
    *******
    
    DIVs : list of lists of integers
        List of DimensionIndexValues in Seg.
        
    """
    
    # Initialise the list of DIVs:
    DIVs = [] 
    
    sequences = Seg.PerFrameFunctionalGroupsSequence
    
    for sequence in sequences:
        DIV = sequence.FrameContentSequence[0]\
                      .DimensionIndexValues
        
        DIVs.append(DIV)
        
    return DIVs






def GroupListBySegment(ListToGroup, DIVs):
    """
    Group a list of items by common segment/ROI using the DimensionIndexValues.
    
    Inputs:
    ******
    
    ListToGroup : list
        The list to be grouped.
        
    DIVs : list of lists of integers
        List of DimensionIndexValues.
        
        
    Outputs:
    *******
    
    GroupedList : list of lists
        ListToGroup grouped by ROI.
        
        
    Note:
    ----
    
    DIVs is a list of lists of the form:
            
    [ [1, 10], [1, 11], [1, 12], ... [2, 6], [2, 7], [2, 8], ... ]
    
    where each list of index values that belong to a common ROI are separated
    into separate lists.
    
    The goal is to group a list (of anything) by ROI.  In the case of the DIVs,
    that is:
        
    [ [ [1, 10], [1, 11], [1, 12], ... ],
      [ [2, 6], [2, 7], [2, 8], ... ],
      ... 
     ]
      
     
    If there's only one ROI, ListToGroup will still be nested in a list to 
    maintain continuity.  In the case of the DIVs with only one ROI:
        
    [ [ [1, 10], [1, 11], [1, 12], ... ]
     ]
    """
    
    # Get the list of ROI numbers:
    RoiNums = []
    
    for DIV in DIVs:
        RoiNums.append(DIV[0])
        
    UniqueRoiNums = list(set(RoiNums))
    
    if len(UniqueRoiNums) == 1:
        GroupedList = [ListToGroup]
        
    else:
        GroupedList = []
        
        for RoiNum in UniqueRoiNums:
            ListThisRoi = [] # initialise
            
            for i in range(len(ListToGroup)):
                if DIVs[i][0] == RoiNum:
                    ListThisRoi.append(ListToGroup[i])
        
            GroupedList.append(ListThisRoi)
             
    return GroupedList











def AddToPFFGS(Seg):
    """
    Append the last item in the Per-FrameFunctionalGroupsSequence of the
    SEG to itself (i.e. increase the length of the sequence by one). 
    
    Inputs:
    ******
    
    Seg : Pydicom object
        ROI object from a SEG file.
        
    
    Outputs:
    *******
    
    NewSeg : Pydicom object
        Modified ROI object with Per-FrameFunctionalGroupsSequence lengthened
        by one.
    """
    
    from copy import deepcopy
    
    # Use Seg as a template for NewSeg: 
    NewSeg = deepcopy(Seg)
             
    # The last item in Per-frame Functional Groups Sequence:
    last = deepcopy(Seg.PerFrameFunctionalGroupsSequence[-1])
    
    # Append to the Per-frame Functional Groups Sequence:
    NewSeg.PerFrameFunctionalGroupsSequence.append(last)
             
    return NewSeg






def AddToSS(Seg):
    """
    Append the last item in the SegmentSequence of the SEG Object to itself 
    (i.e. increase the length of the sequence by one). 
    
    Inputs:
    ******
    
    Seg : Pydicom object
        ROI object from a SEG file.
        
    
    Outputs:
    *******
    
    NewSeg : Pydicom object
        Modified Seg with SegmentSequence lengthened by one.
    """
    
    from copy import deepcopy
    
    # Use Seg as a template for NewSeg: 
    NewSeg = deepcopy(Seg)
             
    # The last item in Segment Sequence:
    last = deepcopy(Seg.SegmentSequence[-1])
    
    # Append to the Segment Sequence:
    NewSeg.SegmentSequence.append(last)
             
    return NewSeg







def ChangeNumOfSegSequences(Seg, Dicoms, NumOfFrames, LogToConsole=False):
    """
    Adjust the number of sequences in a SEG object based so that they are 
    consistent with the number of DICOMs in the series and the number of
    frames in the pixel array.
         
    
    Inputs:
    ******
                              
    Seg : Pydicom object
        SEG object.
        
    Dicoms : List of Pydicom objects
        List of DICOM objects that relate to the SEG object to be created.
    
    NumOfFrames : integer
        The number of frames in the SEG object's pixel array.
                         
    LogToConsole : boolean (optional; False by default)
        Denotes whether intermediate results will be logged to the console.
        
        
    Outputs:
    *******
        
    Seg : Pydicom object
        SEG object with modified number of sequences.
    """
    
    
    """ 
    Modify the number of sequences in ReferencedSeriesSequence. 
    The number of sequences must be equal to the number of DICOMs.
    """
    
    from copy import deepcopy
    
    # The number of DICOMs:
    D = len(Dicoms)
    
    # The number of sequences in the ReferencedSeriesSequence:
    R = len(Seg.ReferencedSeriesSequence[0].ReferencedInstanceSequence)
    
    
    # Add/remove sequences by appending/popping the last sequence N times, 
    # where N is the difference between D and R:
    if D > R:
        for i in range(D - R):
            Seg.ReferencedSeriesSequence[0]\
               .ReferencedInstanceSequence\
               .append(deepcopy(Seg.ReferencedSeriesSequence[0]\
                                   .ReferencedInstanceSequence[-1]))          
    else:
        for i in range(R - D):
            Seg.ReferencedSeriesSequence[0]\
               .ReferencedInstanceSequence.pop()

    
    """ 
    Modify the number of sequences in SegmentSequence. 
    There must be only one sequence - for the (one) new segment.
    """
    
    S = len(Seg.SegmentSequence)
    
    if S > 1:
        for i in range(S - 1):
            Seg.SegmentSequence.pop()
    
    
    """ 
    Modify the number of sequences in Per-FrameFunctionGroupsSequence. 
    The number of sequences must be equal to NumOfFrames.
    """
    
    # The number of sequences in the Per-FrameFunctionGroupsSequence:
    P = len(Seg.PerFrameFunctionalGroupsSequence)
    
    if NumOfFrames > P:
        for i in range(NumOfFrames - P):
            Seg.PerFrameFunctionalGroupsSequence\
               .append(deepcopy(Seg.PerFrameFunctionalGroupsSequence[-1]))          
    else:
        for i in range(P - NumOfFrames):
            Seg.PerFrameFunctionalGroupsSequence.pop()

    
    
    
    if True:#LogToConsole:       
        R2 = len(Seg.ReferencedSeriesSequence[0].ReferencedInstanceSequence)
        
        S2 = len(Seg.SegmentSequence)
        
        P2 = len(Seg.PerFrameFunctionalGroupsSequence)
        
        print(f'\nThere are {D} DICOMs and there were {R} sequences in',
              f'ReferencedSeriesSequence. Now there are {R2} sequences.')
        
        print(f'\nThere were {S} sequences in SegmentSequence. Now there are',
              f'{S2} sequences.')
        
        print(f'\nThere are {NumOfFrames} frames in the pixel array and there',
              f'were {P} sequences in PerFrameFunctionalGroupsSequence. Now',
              f'there are {P2} sequences.')
        
    
    return Seg








def GetFrameFromPixArr(Seg, DicomDir, SearchString, SliceNum, LogToConsole):
    """
    Extract a single (2D) frame from a 3D pixel array that matches a given
    segment label.  
    
    Inputs:
    ******
    
    Seg : Pydicom object
        SEG object.
    
    DicomDir : string
        Directory containing the corresponding DICOMs.
    
    SearchString : string
        All or part of the Segment label containing the segmentation to be
        copied.
    
    SliceNum : integer
        Slice index of the Source DICOM stack corresponding to the segmentation
        to be copied (counting from 0).
        
    LogToConsole : boolean (optional; False by default)
        Denotes whether some results will be logged to the console.
        
    
    Outputs:
    *******
    
    Frame : Numpy array
        Frame from PixArr.
    """
    
    import numpy as np
    from DicomTools import GetDicomSOPuids
    from DicomTools import GetRoiLabels
    from DicomTools import GetRoiNum
    
    SegLabels = GetRoiLabels(Seg)
    
    # Determine which segment contains the segmentation to be copied, and
    # the corresponding frame number in the pixel array:
    """ Note:  SegNum is equivalent to SegmentNumber in SegmentSequence. """
    SegNum = GetRoiNum(Seg, SearchString)
    
    SOPuids = GetDicomSOPuids(DicomDir)
    
    PFFGStoSliceIndsBySeg = GetPFFGStoSliceIndsBySeg(Seg, SOPuids)
    
    PFFGStoSliceIndsInSeg = PFFGStoSliceIndsBySeg[SegNum]
    
    if not SliceNum in PFFGStoSliceIndsInSeg:
        msg = f'There is no segmentation in the segment matching the term '\
              + f'"{SearchString}" for slice {SliceNum} in the SEG.'
              
        raise Exception(msg)
    
    # Get the corresponding FrameNum:
    
    n = 0 # initialise frame number counter
    
    for i in range(len(SegLabels)):
        if i == SegNum:
            """ 
            This segment contains the frame to be copied, whose position is
            given by the index of FromSliceNum in 
            SrcPFFGStoSliceIndsBySeg[i] plus any frames that preceeded it 
            (i.e. the frame counter n).
            """
            FrameNum = n + PFFGStoSliceIndsBySeg[i].index(SliceNum)
            
        else:
            # Add to the frame counter the number of frames in this segment:
            n += len(PFFGStoSliceIndsBySeg[i]) 
    
    
    if LogToConsole:
        print('\n\nResults of GetFrameFromPixArr:')
        print(f'   SliceNum = {SliceNum} relates to FrameNum = {FrameNum} in',
              'PixelArray')
    
    PixArr = Seg.pixel_array
    
    if len(PixArr.shape) < 3:
        # This is a single-frame PixArr, i.e. shape (R, C). Reshape it to 
        # shape (1, R, C):
        R, C = PixArr.shape
        
        PixArr = np.reshape(PixArr, (1, R, C))
    else:
        # This is a multi-frame PixArr, i.e. shape (AllF, R, C).
        AllF, R, C = PixArr.shape
    
    # Initialise Frame:
    Frame = np.zeros((1, R, C), dtype='uint')
    
    Frame[0] = PixArr[FrameNum]
            
    return Frame








def GetFramesFromPixArr(Seg, DicomDir, SearchString, LogToConsole):
    """
    Extract all frames from a 3D pixel array that match a given segment label.  
    
    Inputs:
    ******
    
    Seg : Pydicom object
        SEG object.
    
    DicomDir : string
        Directory containing the corresponding DICOMs.
    
    SearchString : string
        All or part of the Segment Label of the segment containing the 
        segmentation to be copied.
    
    SliceNum : integer
        Slice index of the Source DICOM stack corresponding to the segmentation
        to be copied (counting from 0).
        
    LogToConsole : boolean (optional; False by default)
        Denotes whether some results will be logged to the console.
        
    
    Outputs:
    *******
    
    Frame : Numpy array
        Frame from PixArr.
    """
    
    import numpy as np
    from DicomTools import GetDicomSOPuids
    from DicomTools import GetRoiNum
    
    # Determine which segment contains the segmentation to be copied, and
    # the corresponding frame number in the pixel array:
    """ Note:  SegNum is equivalent to SegmentNumber in SegmentSequence. """
    SegNum = GetRoiNum(Seg, SearchString)
    
    SOPuids = GetDicomSOPuids(DicomDir)
    
    PFFGStoSliceIndsBySeg = GetPFFGStoSliceIndsBySeg(Seg, SOPuids)
    
    PFFGStoSliceIndsInSeg = PFFGStoSliceIndsBySeg[SegNum]
    
    # The number of frames in the segment of interest:
    F = len(PFFGStoSliceIndsInSeg)
    
    # Get the number of rows and columns required for Frames:
    PixArr = Seg.pixel_array
    
    if len(PixArr.shape) < 3:
        """ This is a single-frame PixArr, i.e. shape (1, R, C). """
        R, C = PixArr.shape
    else:
        """ This is a multi-frame PixArr, i.e. shape (AllF, R, C). """
        AllF, R, C = PixArr.shape
    
    Frames = np.zeros((F, R, C), dtype='uint')
    
    for f in range(F):
        SliceNum = PFFGStoSliceIndsInSeg[f]
        
        Frame = GetFrameFromPixArr(Seg, DicomDir, SearchString, SliceNum, 
                                   LogToConsole)
        
        Frames[f] = Frame
    
    if LogToConsole:
        print('\n\n***Result from GetFramesFromPixArr:')
        print(f'   There are {F} frames in the segment matching',
              f'"{SearchString}".')
        print(f'   PFFGStoSliceIndsInSeg = {PFFGStoSliceIndsInSeg}')
        print(f'   PixArr.shape = {PixArr.shape}')
        if len(PixArr.shape) > 2:
            [print(f'   np.amax(PixArr[{i}]) = {np.amax(PixArr[i])}') for i in range(PixArr.shape[0])]
        else:
            print(f'   np.amax(PixArr) = {np.amax(PixArr)}')
        print(f'   Frames.shape = {Frames.shape}')
        if len(Frames.shape) > 2:
            [print(f'   np.amax(Frames[{i}]) = {np.amax(Frames[i])}') for i in range(Frames.shape[0])]
        else:
            print(f'   np.amax(Frames) = {np.amax(Frames)}')
            
    return Frames








def GetPixArrInSeg(Seg, DicomDir, SearchString):
    """
    Get the frames in a SEG's pixel array that belong to a segment with
    specified label.
    
    Inputs:
    ******
    
    Seg : Pydicom object
        SEG object.
        
    DicomDir : string 
        Directory containing the corresponding DICOMs.
        
    SearchString : string
        All or part of the Segment Label containing the segment of interest.
                       
                            
    Outputs:
    *******
    
    PixArrInSeg : Numpy array
        Sub-array of the SEG's pixel array that contains the frames that belong
        to the segment of interest. 
        
    PFFGStoSliceIndsInSeg : List of integers
        List (for each segmentation) of the slice numbers that correspond to 
        each frame in PixArr.
    """
    
    import numpy as np
    
    AllPixArr = Seg.pixel_array
    
    AllF, R, C = AllPixArr.shape
    
    # Get the frame numbers of the SEG's pixel array that correspond to the 
    # segment of interest, and the corresponding Per-frame Functional Groups
    # Sequence-to-slice indices:
    FrameNumsInSeg, PFFGStoSliceIndsInSeg = GetFrameNums(Seg, SearchString, 
                                                         DicomDir)
    
    F = len(FrameNumsInSeg)
    
    PixArrInSeg = np.zeros((F, R, C), dtype='uint')
    
    for i in range(F):  
        PixArrInSeg[i] = AllPixArr[FrameNumsInSeg[i]]
    
        
    return PixArrInSeg, PFFGStoSliceIndsInSeg








def AddCopiedPixArr(OrigPixArr, OrigPFFGStoSliceInds, 
                    PixArrToAdd, PFFGStoSliceIndsToAdd):
    """
    Add frame(s) from a pixel array to an existing pixel array.
       
    
    Inputs:
    ******
    
    OrigPixArr : Numpy array
        A FxRxC (Frames x Rows x Columns) array of all frames that belong to
        the segment of interest. 
        
    OrigPFFGStoSliceInds : list of integers
        List (for each segmentation) of slice numbers that correspond to each 
        frame in OrigPixArr.
        
    PixArrToAdd : Numpy array
        A FxRxC (Frames x Rows x Columns) array of all frames that originated
        from a single segmentation.  F will be one if a single segmentation is
        to be copied, but may be greater than one, if, for example, the 
        segmentation to be copied was resampled to a number of segmentations.
        
    PFFGStoSliceIndsToAdd : list of integers
        List (for each segmentation) of slice numbers that correspond to each 
        frame in PixArrToAdd.
        
        
    Outputs:
    *******
    
    NewPixArr : Numpy array
        A FxRxC (Frames x Rows x Columns) array of all frames in 
        OrigPixArrInSeg and PixArrToAddToSeg. Note that F will not necessarily
        be the sum of the number of frames in OrigPixArrInSeg and 
        PixArrToAddToSeg.  Some frames in both pixel arrays may correspond
        to the same slice number, in which case, any duplicate frame(s) in
        OrigPixArrInSeg will be over-written with the frame(s) in
        PixArrToAddToSeg that correspond to the same slice number.
        
    NewPFFGStoSliceInds : list of integers
        Modified list (for each segmentation) of slice numbers that correspond   
        to each frame in NewPixArr.
    """
    
    import numpy as np
    from GeneralTools import UniqueItems
    
    # Combine OrigPFFGStoSliceInds and PFFGStoSliceIndsToAdd:
    NewPFFGStoSliceInds = OrigPFFGStoSliceInds + PFFGStoSliceIndsToAdd
    
    # Remove any duplicate slice numbers:
    NewPFFGStoSliceInds = UniqueItems(NewPFFGStoSliceInds)
    
    F = len(NewPFFGStoSliceInds)
    
    OrigF, R, C = OrigPixArr.shape
    
    NewPixArr = np.zeros((F, R, C), dtype='uint')
    
    for FrameNum in range(F):
        # The corresponding slice number for this frame:
        SliceNum = NewPFFGStoSliceInds[FrameNum]
        
        if SliceNum in PFFGStoSliceIndsToAdd:
            """
            This frame is to be over-written by the corresponding frame in
            PixArrToAdd.
            """
            
            ind = PFFGStoSliceIndsToAdd.index(SliceNum)
            
            NewPixArr[FrameNum] = PixArrToAdd[ind]
            
        else:
            """
            This existing frame (in OrigPixArr) is to be preserved.
            """
            
            ind = OrigPFFGStoSliceInds.index(SliceNum)
            
            NewPixArr[FrameNum] = OrigPixArr[ind]
    
    
    return NewPixArr, NewPFFGStoSliceInds










def InitialiseSeg(SegTemplate, SearchString, PFFGStoSliceInds, DicomDir, 
                  NamePrefix='', LogToConsole=False):
    """
    Initialise a SEG object based on an existing SEG object (SegTemplate).
         
    
    Inputs:
    ******
    
    SegTemplate : Pydicom object
        SEG object that will be used as a template to create the new object.

    SearchString : string
        All or part of the SegmentLabel of the segment of interest. 
        
    PFFGStoSliceInds : List of integers
        List (for each segmentation) of the slice numbers that correspond to 
        each frame in the SEG's pixel array.
                    
    DicomDir : string
        Directory containing the corresponding DICOMs.
    
    NamePrefix : string (optional; '' by default)
        Prefix to be added to the assigned filename (after the DateTime stamp), 
        e.g. 'Case3b-i'.
        
    LogToConsole : boolean (optional; False by default)
        Denotes whether intermediate results will be logged to the console.
        
        
    Output:
    ******
        
    Seg : Pydicom object
        New SEG object.
    """
    
    from pydicom.uid import generate_uid
    import time
    from copy import deepcopy
    from DicomTools import GetRoiNum
    from DicomTools import GetDicomFpaths
    from DicomTools import ImportDicom
    from ImageTools import GetImageAttributes
    
    Dicom = ImportDicom(DicomDir)
    
    NumOfDicoms = len(GetDicomFpaths(DicomDir))
    
    Size, Spacings, ST,\
    IPPs, Dirs = GetImageAttributes(DicomDir=DicomDir, Package='sitk')
    
    SegNum = GetRoiNum(SegTemplate, SearchString)
    
    #print(f'\n\n***SegNum = {SegNum}')
    
    # The Segment Label of the segment containing the segmentation to be 
    # copied:
    SegLabel = SegTemplate.SegmentSequence[SegNum].SegmentLabel
    
    #print(f'\n\n***SegLabel = {SegLabel}')
    
    # Use SegTemplate as a template for Seg:
    Seg = deepcopy(SegTemplate)
    
    # Generate a new SOPInstance UID:
    Seg.SOPInstanceUID = generate_uid()
    
    # Generate a new SeriesInstance UID:
    Seg.SeriesInstanceUID = generate_uid()
    
    Seg.file_meta.MediaStorageSOPInstanceUID = deepcopy(Seg.SOPInstanceUID) # 18/12
    
    
    """Added on 16/12 to see if it solves the issues for UseCases 2b and 3b-i.
    It didn't resolve the issue.
    
    # Generate a new DimensionOrganizationUID:
    Seg.DimensionOrganizationSequence[0].DimensionOrganizationUID = generate_uid()
    
    # Set the DimensionOrganizationUIDs in DimensionIndexSequence to the new
    # uid:
    DOuid = deepcopy(Seg.DimensionOrganizationSequence[0].DimensionOrganizationUID)
    
    DIS = deepcopy(Seg.DimensionIndexSequence)
    
    for i in range(len(DIS)):
        Seg.DimensionIndexSequence[i].DimensionOrganizationUID = DOuid
    
    end of code added on 16/12."""
    
    # Modify the Series Description:
    #if 'SEG' in NamePrefix:
    #    SD = NamePrefix + '_from_' + Seg.SeriesDescription
    #else:
    #    SD = NamePrefix + '_SEG_from_' + Seg.SeriesDescription
    
    #print(f'\n\n***NamePrefix = {NamePrefix}')
        
    #Seg.SeriesDescription = SD
    Seg.SeriesDescription = NamePrefix
    
    #print(f'\n\n***Seg.SeriesDescription = {Seg.SeriesDescription}')
    
    # Modify the Content Date and Time to the present:
    NewDate = time.strftime("%Y%m%d", time.gmtime())
    NewTime = time.strftime("%H%M%S", time.gmtime())
    
    Seg.ContentDate = NewDate
    Seg.ContentTime = NewTime
    
    
    
    # Modify various tags to match the values in Dicoms:
    Seg.StudyDate = Dicom.StudyDate
    Seg.SeriesDate = Dicom.SeriesDate
    #Seg.ContentDate = Dicom.ContentDate
    Seg.StudyTime = Dicom.StudyTime
    Seg.SeriesTime = Dicom.SeriesTime
    #Seg.ContentTime = Dicom.ContentTime
    
    Seg.ReferencedSeriesSequence[0]\
       .SeriesInstanceUID = Dicom.SeriesInstanceUID # 15/12/20
    
    Seg.PatientName = Dicom.PatientName
    Seg.PatientID = Dicom.PatientID
    Seg.PatientBirthDate = Dicom.PatientBirthDate
    Seg.PatientSex = Dicom.PatientSex
    Seg.PatientAge = Dicom.PatientAge
    Seg.StudyInstanceUID = Dicom.StudyInstanceUID
    
    #Seg.StudyID = Dicom.StudyID # Leave StudyID unchanged (22/12/20)
    
    Seg.FrameOfReferenceUID = Dicom.FrameOfReferenceUID
    Seg.NumberOfFrames = f"{len(PFFGStoSliceInds)}"
    Seg.Rows = Dicom.Rows
    Seg.Columns = Dicom.Columns
    
    Seg.SharedFunctionalGroupsSequence[0]\
       .PlaneOrientationSequence[0]\
       .ImageOrientationPatient = Dicom.ImageOrientationPatient
       
    """ 
    Notes:
        
    1. The SliceThickness appears to be the z-Spacing rather than the
    SliceThickness from the DICOM metadata. 
    
    2. The character limit of VR DS is 16 characters.
    """
    Zspacing = f"{Spacings[2]}"
    
    if len(Zspacing) > 16:
        Zspacing = Zspacing[:16]
    
    Seg.SharedFunctionalGroupsSequence[0]\
       .PixelMeasuresSequence[0]\
       .SliceThickness = Zspacing
    
    Seg.SharedFunctionalGroupsSequence[0]\
       .PixelMeasuresSequence[0]\
       .SpacingBetweenSlices = Zspacing

    Seg.SharedFunctionalGroupsSequence[0]\
       .PixelMeasuresSequence[0]\
       .PixelSpacing = Dicom.PixelSpacing
       
       
    """ 
    Modify the number of sequences in ReferencedInstanceSequence (RIS). 
    The number of sequences RIS should be equal to the number of DICOMs.
    """
    # The original and required number of sequences in 
    # ReferencedInstanceSequence:
    OrigRIS = len(Seg.ReferencedSeriesSequence[0].ReferencedInstanceSequence)

    ReqRIS = NumOfDicoms
    
    # Add/remove sequences by appending/popping the last sequence N times, 
    # where N is the difference between ReqRIS and OrigRIS:
    if ReqRIS > OrigRIS:
        for i in range(ReqRIS - OrigRIS):
            Seg.ReferencedSeriesSequence[0]\
               .ReferencedInstanceSequence\
               .append(deepcopy(Seg.ReferencedSeriesSequence[0]\
                                   .ReferencedInstanceSequence[-1]))          
    else:
        for i in range(OrigRIS - ReqRIS):
            Seg.ReferencedSeriesSequence[0]\
               .ReferencedInstanceSequence.pop()
    
    
    """ 
    Modify the number of sequences in SegmentSequence. 
    There must be only one. Preserve the sequence that relates to the segment
    of interest and remove any others.
    """
    
    # Over-write the first SegmentSequence with the sequence to be preserved:
    Seg.SegmentSequence[0] = deepcopy(Seg.SegmentSequence[SegNum])
    
    OrigSS = len(Seg.SegmentSequence)
    
    ReqSS = 1
    
    if OrigSS > ReqSS:
        for i in range(OrigSS - ReqSS):
            Seg.SegmentSequence.pop()
    
    
    """ 
    Modify the number of sequences in Per-FrameFunctionGroupsSequence. 
    The number of sequences must be equal to the length of PFFGStoSliceInds.
    """

    OrigPFFGS = len(Seg.PerFrameFunctionalGroupsSequence)
    
    ReqPFFGS = len(PFFGStoSliceInds)
    
    if ReqPFFGS > OrigPFFGS:
        for i in range(ReqPFFGS - OrigPFFGS):
            Seg.PerFrameFunctionalGroupsSequence\
               .append(deepcopy(Seg.PerFrameFunctionalGroupsSequence[-1]))          
    else:
        for i in range(OrigPFFGS - ReqPFFGS):
            Seg.PerFrameFunctionalGroupsSequence.pop()

    
    
    #print(f'\n\n***Seg.SegmentSequence[0].SegmentLabel before change = {Seg.SegmentSequence[0].SegmentLabel}')
    
    """ 
    Modify the Segment Label to SegLabel.
    """
    Seg.SegmentSequence[0].SegmentLabel = SegLabel # 09/12/2020
    
    #print(f'\n\n***Seg.SegmentSequence[0].SegmentLabel after change = {Seg.SegmentSequence[0].SegmentLabel}')
    
    
    
    """
    Output some results to the console.
    """
    if LogToConsole:       
        NewRIS = len(Seg.ReferencedSeriesSequence[0].ReferencedInstanceSequence)
        
        NewSS = len(Seg.SegmentSequence)
        
        NewPFFGS = len(Seg.PerFrameFunctionalGroupsSequence)
        
        print(f'\nThere are {ReqRIS} DICOMs and there were {OrigRIS}',
              f'sequences in ReferencedSeriesSequence. Now there are {NewRIS}',
              'sequences.')
        
        print(f'\nThere were {OrigSS} sequences in SegmentSequence.',
              f'Now there are {NewSS} sequences.')
        
        print(f'\nThere are {ReqPFFGS} segmentations and there were',
              f'{OrigPFFGS} sequences in PerFrameFunctionalGroupsSequence.',
              f'Now there are {NewPFFGS} sequences.')
        
    return Seg

    
    
    







def ModifySeg(Seg, PixArr, PFFGStoSliceInds, DicomDir, LogToConsole=False):
    """
    Modify various tag values of a SEG so that they are consistent with the
    corresponding tag values of the DICOMs.
         
    
    Inputs:
    ******
                              
    Seg : Pydicom object
        The SEG ROI object to modify.
     
    PixArr : Numpy array
        The SEG's pixel array.
    
    PFFGStoSliceInds : List of integers
        List of slice numbers that correspond to each frame in PixArr.
    
    DicomDir : string
        Directory containing the corresponding DICOMs.
                         
    LogToConsole : boolean (optional; False by default)
        Denotes whether intermediate results will be logged to the console.
        
        
    Output:
    ******
        
    Seg : Pydicom object
        Modified SEG ROI object.
    """
    
    from DicomTools import ImportDicoms
    from pydicom.pixel_data_handlers.numpy_handler import pack_bits
    import numpy as np
    
    F, R, C = PixArr.shape
    
    #if F == 0:
    #    PixArr = np.reshape(PixArr, (1, R, C))
    #    
    #    F, R, C = PixArr.shape
    
    if LogToConsole:
        print(f'\n*****PixArr.shape = {PixArr.shape}')
    
    P = len(PFFGStoSliceInds)
    
    if not F == P:
        raise Exception(f"There are {F} frames in PixArr and {P} indices in "\
                        + "PFFGStoSliceInds. They must be equal.")
    
    
    Dicoms = ImportDicoms(DicomDir)
    
    RIS = len(Seg.ReferencedSeriesSequence[0].ReferencedInstanceSequence)
             
    if not RIS == len(Dicoms):
        raise Exception(f"There are {len(Dicoms)} DICOMs and {RIS} sequences "\
                        + "in ReferencedInstanceSequence. They must be equal.")
    
    # Modify ReferencedInstanceSequence:
    for i in range(len(Dicoms)):
        Seg.ReferencedSeriesSequence[0]\
           .ReferencedInstanceSequence[i]\
           .ReferencedSOPInstanceUID = Dicoms[i].SOPInstanceUID
    
    
    Seg.NumberOfFrames = f"{F}"
    
    # Modify SegmentSequence:
    Seg.SegmentSequence[0].SegmentNumber = 1
    
    # Get the ReferencedSOPInstanceUIDs in the ReferencedInstanceSequence:
    RefSOPs = GetRSOPuidsInRIS(Seg)
    
    # Modify PerFrameFunctionalGroupsSequence:
    for i in range(P):
        # The slice index for the i^th sequence:
        s = PFFGStoSliceInds[i]
        
        if LogToConsole:
            print('\n\nResults of ModifySeg:')
            print(f'   PFFGStoSliceInds[{i}] = {PFFGStoSliceInds[i]}')
            print(f'   DICOM slice number = {s}')
        
        Seg.PerFrameFunctionalGroupsSequence[i]\
           .DerivationImageSequence[0]\
           .SourceImageSequence[0]\
           .ReferencedSOPInstanceUID = Dicoms[s].SOPInstanceUID
        
        # Modify the DimensionIndexValues (DIVs), ImagePositionPatient and
        # ReferencedSegmentNumber:
        """
        Since there is always only one segment, the first integer in the DIV 
        will always be 1, as is the Referenced Segment Number. The second 
        integer will be the 1 + the index of the SOP Instance UID for the s^th 
        DICOM within RefSOPs (+1 since ind is an integer counting from 0, 
        whereas the DIVs are integers counting from 1).
        """
        ind = RefSOPs.index(Dicoms[s].SOPInstanceUID)
        
        Seg.PerFrameFunctionalGroupsSequence[i]\
           .FrameContentSequence[0]\
           .DimensionIndexValues = [1, ind + 1]
        
        Seg.PerFrameFunctionalGroupsSequence[i]\
           .PlanePositionSequence[0]\
           .ImagePositionPatient = Dicoms[s].ImagePositionPatient
           
        Seg.PerFrameFunctionalGroupsSequence[i]\
           .SegmentIdentificationSequence[0]\
           .ReferencedSegmentNumber = 1
           
        if LogToConsole:
              print(f'   DimensionIndexValues = {[1, ind + 1]}')
              print(f'   ReferencedSegmentNumber = {1}')
              
        
        
    
    
    if LogToConsole:
        print('\n   Prior to ravelling and packing bits:')
        print(f'   PixArr.shape = {PixArr.shape}')
        [print(f'   np.amax(PixArr[{i}]) = {np.amax(PixArr[i])}') for i in range(PixArr.shape[0])]
    
    

    # Ravel (to 1D array) PixArr and pack bits (see
    # https://github.com/pydicom/pydicom/issues/1230):
    packed = pack_bits(PixArr.ravel())
    
    # Convert PixArr to bytes:
    #Seg.PixelData = PixArr.tobytes() <-- doesn't work
    Seg.PixelData = packed + b'\x00' if len(packed) % 2 else packed
    
    
    if False:
        F, R, C = PixArr.shape
        
        # If there are more than one frames in PixArr:
        if F > 1:
            # Ravel (to 1D array) PixArr and pack bits (see
            # https://github.com/pydicom/pydicom/issues/1230):
            packed = pack_bits(PixArr.ravel())
            
            # Convert PixArr to bytes:
            Seg.PixelData = packed + b'\x00' if len(packed) % 2 else packed
            
            if LogToConsole:
                print(f'\n   len(packed) = {len(packed)}') 
                """ 
                = 39936 for UseCase 1a
                = 6656 for UseCase 1b
                """
        else:
            # Convert PixArr to bytes:
            #Seg.PixelData = PixArr.tobytes()
            
            #if LogToConsole:
                #print(f'\n   len(PixArr.tobytes()) = {len(PixArr.tobytes())}') 
                #""" 
                #=  for UseCase 1a
                #= 212992 for UseCase 1b
                #"""
            
            #PixArr = np.reshape(PixArr, (R, C))
            
            if LogToConsole:
                print('\n   There is only one frame in PixArr, so it was reshaped',
                      f'to shape {PixArr.shape}')
                print(f'   np.amax(PixArr) = {np.amax(PixArr)}')
            
            # Ravel (to 1D array) PixArr and pack bits (see
            # https://github.com/pydicom/pydicom/issues/1230):
            packed = pack_bits(PixArr.ravel())
            
            # Convert PixArr to bytes:
            Seg.PixelData = packed + b'\x00' if len(packed) % 2 else packed
            
            if LogToConsole:
                print(f'\n   len(packed) = {len(packed)}') 
                """ 
                = 39936 for UseCase 1a
                = 6656 for UseCase 1b
                """
        
        
    
    
    
    if LogToConsole:
        print(f'\n   len(packed) = {len(packed)}') 
        """ 
        = 39936 for UseCase 1a
        = 6656 for UseCase 1b
        """
                
        PixArr2 = Seg.pixel_array
        
        print('\n   After packing bits:')
        print(f'   PixArr2.shape = {PixArr2.shape}')
        if len(PixArr2.shape) > 2:
            [print(f'   np.amax(PixArr2[{i}]) = {np.amax(PixArr2[i])}') for i in range(PixArr2.shape[0])]
        else:
            print(f'   np.amax(PixArr2) = {np.amax(PixArr2)}')
    
                                          
    return Seg






def ErrorCheckSeg(Seg, DicomDir, LogToConsole=False):
    """
    Check a SEG for errors in dependencies based on provided directory of
    the DICOMs that relate to the SEG.  
    
    Inputs:
    ******
    
    Seg : Pydicom object
        SEG object to be error checked.
        
    DicomDir : string
        Directory containing the DICOMs that relate to Seg.
        
    LogToConsole : boolean (default False)
        Denotes whether some results will be logged to the console.
                           
    
    Outputs:
    *******
    
    LogList : list of strings
        A list of strings that describe any errors that are found.  If no 
        errors are found an empty list ([]) will be returned.
        
    Nerrors : integer
        The number of errors found.
    """
    
    import importlib
    import GeneralTools
    importlib.reload(GeneralTools)
    
    from copy import deepcopy
    from DicomTools import GetDicomSOPuids
    from DicomTools import ImportDicom
    from ImageTools import GetImageAttributes
    from GeneralTools import AreItemsEqualToWithinEpsilon
    from GeneralTools import AreListsEqualToWithinEpsilon
    
    # The maximum allowed error between two lists/items:
    epsilon = 1e-05
    
    SOPuids = GetDicomSOPuids(DicomDir)
    
    Dicom = ImportDicom(DicomDir)
    
    #Size, Spacings, ST,\
    #IPPs, Dirs = GetImageAttributes(DicomDir=DicomDir, Package='sitk')
    Size, Spacings, ST,\
    IPPs, Dirs = GetImageAttributes(DicomDir=DicomDir, Package='pydicom')
    
    # The number of frames, rows and columns in the SEG's pixel array:
    if len(Seg.pixel_array.shape) > 2:
        PixArrF, PixArrR, PixArrC = Seg.pixel_array.shape
    else:
        PixArrR, PixArrC = Seg.pixel_array.shape
        PixArrF = 1
    
    #NumOfDicoms = len(SOPuids)
    
    LogList = []
    Nerrors = 0
    
    
    """Determine whether MediaStorageSOPInstanceUID matches SOPInstanceUID."""
    MSSOPuid = deepcopy(Seg.file_meta.MediaStorageSOPInstanceUID)
    SOPuid = deepcopy(Seg.SOPInstanceUID)
    
    if MSSOPuid == SOPuid:
        msg = f'INFO:  MediaStorageSOPInstanceUID {MSSOPuid} matches '\
              + f'SOPInstanceUID {SOPuid}.\n'
    else:
        msg = f'ERROR:  MediaStorageSOPInstanceUID {MSSOPuid} does not '\
              + f'match SOPInstanceUID {SOPuid}.\n'
        
        Nerrors = Nerrors + 1
        
    LogList.append(msg)
    
    if LogToConsole:
        print(msg)
    
    
    """Determine whether the number of sequences in 
    ReferencedInstanceSequence matches the number of DICOMs."""
    
    RIS = deepcopy(Seg.ReferencedSeriesSequence[0]\
                      .ReferencedInstanceSequence)
    
    if len(SOPuids) == len(RIS):
        msg = f'INFO:  The number of SOPInstanceUIDs {len(SOPuids)}'\
              + ' matches the number of sequences in '\
              + f'ReferencedInstanceSequence {len(RIS)}.\n'
    else:
        msg = f'ERROR:  The number of SOPInstanceUIDs {len(SOPuids)} does'\
              + ' not match the number of sequences in '\
              + f'ReferencedInstanceSequence {len(RIS)}.\n'
        
        Nerrors = Nerrors + 1
        
    LogList.append(msg)
    
    if LogToConsole:
        print(msg)
    
    
    """Determine whether any of the ReferencedSOPInstanceUIDs do not
    match the SOPInstanceUIDs."""        
    RefSOPuidsInRIS = [RIS[i].ReferencedSOPInstanceUID for i in range(len(RIS))]
    
    # Determine whether the Ref SOP UIDs match the SOP UIDs:
    IsMatch = [RefSOPuid in SOPuids for RefSOPuid in RefSOPuidsInRIS]
    
    NumOfMatches = IsMatch.count(True)
    
    # Find the indices of any non-matching Ref SOP UIDs:
    Inds = [i for i, x in enumerate(IsMatch) if False]
    
    if Inds:
        NonMatchingUids = [RefSOPuidsInRIS[i] for i in Inds]
        
        for i in range(len(NonMatchingUids)):
            uid = NonMatchingUids[i]
            
            msg = f'ERROR:  ReferencedSOPInstanceUID {uid} in '\
                  + f'ReferencedInstanceSequence {i+1} does not match any '\
                  + 'SOPInstanceUID.\n'
            
            Nerrors = Nerrors + 1
    else:
        msg = f'INFO:  The ReferencedSOPInstanceUIDs in '\
                  + f'ReferencedInstanceSequence matches the '\
                  + 'SOPInstanceUIDs.\n'
        
    LogList.append(msg)
    
    if LogToConsole:
        print(msg)
                
                
    
    """Determine whether any of the SOPInstanceUIDs do not match the
    ReferencedSOPInstanceUIDs."""        
    
    # Determine whether the SOP UIDs match the Referenced SOP UIDs:
    IsMatch = [SOPuid in RefSOPuidsInRIS for SOPuid in SOPuids]
    
    NumOfMatches = IsMatch.count(True)
    
    # Find the indices of any non-matching SOP UIDs:
    Inds = [i for i, x in enumerate(IsMatch) if False]
    
    if NumOfMatches == 0:
        NonMatchingUids = [SOPuids[i] for i in Inds]
        
        for i in range(len(NonMatchingUids)):
            uid = NonMatchingUids[i]
            
            msg = f'ERROR:  SOPInstanceUID {uid} is not referenced in any '\
                  + 'ReferencedSOPInstanceUID in '\
                  + 'ReferencedInstanceSequence.\n'
            
            Nerrors = Nerrors + 1
    else:
        msg = f'INFO:  The SOPInstanceUIDs match the '\
                  + 'ReferencedSOPInstanceUIDs in '\
                  + 'ReferencedInstanceSequence.\n'
                  
    LogList.append(msg)
    
    if LogToConsole:
        print(msg)
    
    
                           
    if Seg.ReferencedSeriesSequence[0].SeriesInstanceUID == Dicom.SeriesInstanceUID:
        msg = f'INFO:  SEG SeriesInstanceUID in ReferencedSeriesSequence '\
              + f'{Seg.ReferencedSeriesSequence[0].SeriesInstanceUID} '\
              + 'matches DICOM SeriesInstanceUID '\
              + f'{Dicom.SeriesInstanceUID}.\n'
    else:
        msg = f'ERROR:  SEG SeriesInstanceUID in ReferencedSeriesSequence '\
              + f'{Seg.ReferencedSeriesSequence[0].SeriesInstanceUID} does '\
              + 'not match DICOM SeriesInstanceUID '\
              + f'{Dicom.SeriesInstanceUID}.\n'
        
        Nerrors = Nerrors + 1 
        
    LogList.append(msg)
    
    if LogToConsole:
        print(msg)
            
            
       
    if Seg.PatientName == Dicom.PatientName:
        msg = f'INFO:  SEG PatientName {Seg.PatientName} matches DICOM '\
              + f'PatientName {Dicom.PatientName}.\n'
    else:
        msg = f'ERROR:  SEG PatientName {Seg.PatientName} does not match '\
              + f'DICOM PatientName {Dicom.PatientName}.\n'
            
        Nerrors = Nerrors + 1
        
    LogList.append(msg)
    
    if LogToConsole:
        print(msg)
        
    if Seg.PatientID == Dicom.PatientID:
        msg = f'INFO:  SEG PatientID {Seg.PatientID} matches the '\
              + f'DICOM PatientID {Dicom.PatientID}.\n'
    else:
        msg = f'ERROR:  SEG PatientID ({Seg.PatientID}) does not match the '\
              + f'DICOM PatientID ({Dicom.PatientID}).\n'
        
        Nerrors = Nerrors + 1
        
    LogList.append(msg)
    
    if LogToConsole:
        print(msg)

    if Seg.StudyInstanceUID == Dicom.StudyInstanceUID:
        msg = f'INFO:  SEG StudyInstanceUID {Seg.StudyInstanceUID} '\
              + 'matches the DICOM StudyInstanceUID '\
              + f'{Dicom.StudyInstanceUID}.\n'
    else:
        msg = f'ERROR:  SEG StudyInstanceUID {Seg.StudyInstanceUID} does '\
              + 'not match the DICOM StudyInstanceUID '\
              + f'{Dicom.StudyInstanceUID}.\n'
                      
        Nerrors = Nerrors + 1
        
    LogList.append(msg)
    
    if LogToConsole:
        print(msg)
            
    #if Seg.StudyID == Dicom.StudyID:
    #    msg = f'INFO:  The SEG StudyID {Seg.StudyID} matches the'\
    #          + f' DICOM StudyID {Dicom.StudyID}.'
    #else:
    #    msg = f'ERROR:  The SEG StudyID {Seg.StudyID} does not match the'\
    #          + f' DICOM StudyID {Dicom.StudyID}.'
    #
    #    Nerrors = Nerrors + 1
    #    
    #LogList.append(msg)
    #    
    #if LogToConsole:
    #    print(msg)
            
    if Seg.FrameOfReferenceUID == Dicom.FrameOfReferenceUID:
        msg = f'INFO:  SEG FrameOfReferenceUID {Seg.FrameOfReferenceUID} '\
              + 'matches DICOM FrameOfReferenceUID '\
              + f'{Dicom.FrameOfReferenceUID}.\n'
    else:
        msg = f'ERROR:  SEG FrameOfReferenceUID {Seg.FrameOfReferenceUID} '\
              + 'does not match DICOM FrameOfReferenceUID '\
              + f'{Dicom.FrameOfReferenceUID}.\n'
        
        Nerrors = Nerrors + 1
        
    LogList.append(msg)
    
    if LogToConsole:
        print(msg)
            
    if int(Seg.NumberOfFrames) == PixArrF:
        msg = f'INFO:  NumberOfFrames {Seg.NumberOfFrames} matches the '\
              + f'number of frames in PixelData {PixArrF}.\n'
    else:
        msg = f'ERROR:  NumberOfFrames {Seg.NumberOfFrames} does not '\
              + f'match the number of frames in PixelData {PixArrF}.\n'
        
        Nerrors = Nerrors + 1
        
    LogList.append(msg)
    
    if LogToConsole:
        print(msg)
            
    if Seg.Rows == Dicom.Rows:
        msg = f'INFO:  SEG Rows {Seg.Rows} matches DICOM Rows '\
              + f'{Dicom.Rows}.\n'
    else:
        msg = f'ERROR:  SEG Rows {Seg.Rows} does not match DICOM Rows '\
              + f'{Dicom.Rows}.\n'
              
        Nerrors = Nerrors + 1
        
    LogList.append(msg)
    
    if LogToConsole:
        print(msg)
            
        
    if Seg.Columns == Dicom.Columns:
        msg = f'INFO:  SEG Columns {Seg.Columns} matches DICOM '\
              + f'Columns {Dicom.Columns}.\n'
    else:
        msg = f'ERROR:  SEG Columns {Seg.Columns} does not match DICOM '\
              + f'Columns {Dicom.Columns}.\n'
        
        Nerrors = Nerrors + 1
        
    LogList.append(msg)
    
    if LogToConsole:
        print(msg)
    
    
    """There should only be one sequence in SegmentSequence."""
    N = len(Seg.SegmentSequence)
    
    if N == 1:
        msg = f'INFO:  There are {N} sequences in SegmentSequence.  There '\
              + f'should be only 1.\n'
    else:
        msg = f'ERROR:  There are {N} sequences in SegmentSequence.  There '\
              + f'should be only 1.\n'
        
        Nerrors = Nerrors + 1
              
    LogList.append(msg)
    
    if LogToConsole:
        print(msg)
    
    
    """Verify that the SegmentNumber in SegmentSequence is 1."""
    N = deepcopy(Seg.SegmentSequence[0].SegmentNumber)
    
    if N == 1:
        msg = f'INFO:  SegmentNumber in SegmentSequence is {N}.  It '\
              + 'should be 1.\n'
    else:
        msg = f'ERROR:  SegmentNumber in SegmentSequence is {N}.  It '\
              + 'should be 1.\n'
        
        Nerrors = Nerrors + 1
        
    LogList.append(msg)
    
    if LogToConsole:
        print(msg)
    
    
            
    """Check various tags in SharedFunctionalGroupsSequence."""
    SegIOP = deepcopy(Seg.SharedFunctionalGroupsSequence[0]\
                         .PlaneOrientationSequence[0]\
                         .ImageOrientationPatient)
    
    SegIOP = [float(item) for item in SegIOP]
    
    DcmIOP = [float(item) for item in Dicom.ImageOrientationPatient]
    
    if SegIOP == DcmIOP:
        msg = 'INFO:  SEG ImageOrientationPatient in '\
              + f'SharedFunctionalGroupsSequence {SegIOP} matches '\
              + f'DICOM ImageOrientationPatient {DcmIOP}.\n'
    else:
        if AreListsEqualToWithinEpsilon(SegIOP, DcmIOP, epsilon):
            msg = 'INFO:  SEG ImageOrientationPatient in '\
                  + f'SharedFunctionalGroupsSequence {SegIOP} is within '\
                  + f'{epsilon} of DICOM ImageOrientationPatient {DcmIOP}.\n'
        else:
            msg = 'ERROR:  SEG ImageOrientationPatient in '\
                  + f'SharedFunctionalGroupsSequence {SegIOP} is not within '\
                  + f'{epsilon} of DICOM ImageOrientationPatient {DcmIOP}.\n'
            
            Nerrors = Nerrors + 1
        
    LogList.append(msg)
    
    if LogToConsole:
        print(msg)
       
    
    SegST = deepcopy(Seg.SharedFunctionalGroupsSequence[0]\
                        .PixelMeasuresSequence[0]\
                        .SliceThickness)
    
    """ The SliceThickness appears to be the z-Spacing rather than the
    SliceThickness from the DICOM metadata. """
    
    if float(SegST) == Spacings[2]:
        msg = 'INFO:  SEG SliceThickness in SharedFunctionalGroupsSequence'\
              + f' {SegST} matches the slice thickness calculated '\
              + 'from DICOM ImagePositionPatient and '\
              + f'ImageOrientationPatient {Spacings[2]}.\n'
    else:
        if AreItemsEqualToWithinEpsilon(float(SegST), Spacings[2], epsilon):
            msg = 'INFO:  SEG SliceThickness in '\
                  + f'SharedFunctionalGroupsSequence {SegST} is within '\
                  + f'{epsilon} of the slice thickness calculated from DICOM'\
                  + ' ImagePositionPatient and ImageOrientationPatient '\
                  + f'{Spacings[2]}.\n'
        else:
            print(f'\n{float(SegST) - Spacings[2]}')
            
            msg = 'ERROR:  SEG SliceThickness in '\
                  + f'SharedFunctionalGroupsSequence {SegST} is not within '\
                  + f'{epsilon} of the slice thickness calculated from DICOM '\
                  + 'ImagePositionPatient and ImageOrientationPatient '\
                  + f'{Spacings[2]}.\n'
            
            Nerrors = Nerrors + 1
              
        
    LogList.append(msg)
    
    if LogToConsole:
        print(msg)
    
    
    SegSBS = deepcopy(Seg.SharedFunctionalGroupsSequence[0]\
                         .PixelMeasuresSequence[0]\
                         .SpacingBetweenSlices)
    
    if float(SegSBS) == Spacings[2]:
        msg = 'INFO:  SEG SpacingBetweenSlices in '\
              + f'SharedFunctionalGroupsSequence {SegSBS} matches the slice '\
              + 'thickness calculated from DICOM ImagePositionPatient and '\
              + f'ImageOrientationPatient {Spacings[2]}.\n'
    else:
        if AreItemsEqualToWithinEpsilon(float(SegSBS), Spacings[2], epsilon):
            msg = 'INFO:  SEG SpacingBetweenSlices in '\
                  + f'SharedFunctionalGroupsSequence {SegSBS} is within '\
                  + f'{epsilon} of the slice thickness calculated from DICOM '\
                  + 'ImagePositionPatient and ImageOrientationPatient '\
                  + f'{Spacings[2]}.\n'
        else:
            print(f'\n{float(SegSBS) - Spacings[2]}')
            
            msg = 'ERROR:  SEG SpacingBetweenSlices in '\
                  + f'SharedFunctionalGroupsSequence {SegSBS} is not within '\
                  + f'{epsilon} of the slice thickness calculated from DICOM '\
                  + 'ImagePositionPatient and ImageOrientationPatient '\
                  + f'{Spacings[2]}.\n'
        
            Nerrors = Nerrors + 1
        
    LogList.append(msg)
    
    if LogToConsole:
        print(msg)

    
    SegPS = deepcopy(Seg.SharedFunctionalGroupsSequence[0]\
                        .PixelMeasuresSequence[0]\
                        .PixelSpacing)
    
    SegPS = [float(item) for item in SegPS]
    
    DcmPS = [float(item) for item in Dicom.PixelSpacing]
    
    if SegPS == DcmPS:
        msg = 'INFO:  SEG PixelSpacing in SharedFunctionalGroupsSequence '\
              + f'{SegPS} matches the DICOM PixelSpacing {DcmPS}.\n'
    else:
        if AreListsEqualToWithinEpsilon(SegPS, DcmPS, epsilon):
            msg = 'INFO:  SEG PixelSpacing in SharedFunctionalGroupsSequence '\
                  + f'{SegPS} is within {epsilon} of the DICOM PixelSpacing '\
                  + f'{DcmPS}.\n'
        else:
            msg = 'ERROR:  SEG PixelSpacing in SharedFunctionalGroupsSequence'\
                  + f'{SegPS} is not within {epsilon} of the DICOM '\
                  + f'PixelSpacing {DcmPS}.\n'
            
            Nerrors = Nerrors + 1
        
    LogList.append(msg)
    
    if LogToConsole:
        print(msg)
            
    
    
    """Verify that the number of sequences in PerFrameFunctionalGroupsSequence
    is equal to NumberOfFrames."""
    PFFGS = deepcopy(Seg.PerFrameFunctionalGroupsSequence)
    
    if len(PFFGS) == int(Seg.NumberOfFrames):
        msg = f'INFO:  The number of sequences in '\
              + f'PerFrameFunctionGroupsSequence {len(PFFGS)} '\
              + f'matches NumberOfFrames {Seg.NumberOfFrames}.\n'
    else:
        msg = f'ERROR:  The number of sequences in '\
              + f'PerFrameFunctionGroupsSequence {len(PFFGS)} does not '\
              + f'match NumberOfFrames {Seg.NumberOfFrames}.\n'
        
        Nerrors = Nerrors + 1
        
    LogList.append(msg)
    
    if LogToConsole:
        print(msg)
    
    
    """Determine whether any of the ReferencedSOPInstanceUIDs in the
    PerFrameFunctionGroupsSequence do not match the SOPInstanceUIDs."""        
    RefSOPuidsInPFFGS = [PFFGS[i].DerivationImageSequence[0]\
                                 .SourceImageSequence[0]\
                                 .ReferencedSOPInstanceUID for i in range(len(PFFGS))]
    
    # Determine whether the Ref SOP UIDs match the SOP UIDs:
    IsMatch = [RefSOPuid in SOPuids for RefSOPuid in RefSOPuidsInPFFGS]
    
    NumOfMatches = IsMatch.count(True)
    
    # Find the indices of any non-matching Ref SOP UIDs:
    Inds = [i for i, x in enumerate(IsMatch) if False]
    
    if Inds:
        NonMatchingUids = [RefSOPuidsInPFFGS[i] for i in Inds]
        
        for i in range(len(NonMatchingUids)):
            uid = NonMatchingUids[i]
            
            msg = f'ERROR:  ReferencedSOPInstanceUID {uid} in '\
                  + 'PerFrameFunctionalGroupsSequence {i+1} does not match '\
                  + 'any DICOM SOPInstanceUID.\n'
            
            Nerrors = Nerrors + 1
    else:
        msg = f'INFO:  The ReferencedSOPInstanceUIDs in '\
              + 'PerFrameFunctionalGroupsSequence match the DICOM '\
              + 'SOPInstanceUIDs.\n'
                  
    LogList.append(msg)
    
    if LogToConsole:
        print(msg)
    
    
    """Determine whether the DimensionIndexValues are sensible integers,
    and if the indexed ReferencedSOPInstanceUID agrees with the 
    ReferencedSOPInstance UID within the SourceImageSequence."""
    DIVs = [PFFGS[i].FrameContentSequence[0]\
                    .DimensionIndexValues for i in range(len(PFFGS))]
    
    # Determine whether any of the first elements in the DIVs are not 1  
    # (there should only be one segment, so the first element should always
    # be 1):
    FirstElements = [int(DIVs[i][0]) for i in range(len(DIVs))]
    
    #NumOfMatches = FirstElements.count('1')
    
    # Find the indices of any non-matching elements:
    Inds = [i for i, x in enumerate(FirstElements) if x != 1]
    
    if Inds:
        divs = [DIVs[i] for i in Inds]
        
        for i in range(len(Inds)):
            msg = f'ERROR:  The first element in DimensionalIndexValue {i+1},'\
                  + f' {divs[i]}, is not "1".\n'
            
            Nerrors = Nerrors + 1
    else:
        msg = f'INFO:  The first elements in DimensionalIndexValue are 1.\n'
        
    LogList.append(msg)
    
    if LogToConsole:
        print(msg)
                
    # Determine if any of the second elements in the DIVs exceed the number
    # of sequences in ReferencedInstanceSequence:
    SecondElements = [int(DIVs[i][1]) for i in range(len(DIVs))]
    
    # Find the indices of any elements that exceed len(RIS):
    Inds = [i for i, x in enumerate(SecondElements) if x > len(RIS)]

    if Inds:
        #divs = [DIVs[i] for i in Inds]
        
        for i in range(len(Inds)):
            msg = 'ERROR:  The second element in DimensionalIndexValue '\
                  + f'{i+1}, {DIVs[i]} exceeds the number of sequences in '\
                  + f'ReferencedInstanceSequence {len(RIS)}.\n'
            
            Nerrors = Nerrors + 1
    else:
        msg = 'INFO:  The second elements in DimensionalIndexValue '\
                  + f'matches the number of sequences in '\
                  + f'ReferencedInstanceSequence.\n'
        
    LogList.append(msg)
    
    if LogToConsole:
        print(msg)
                
    """Determine if the ReferencedSOPInstanceUID in the 
    ReferencedInstanceSequence indexed by the second elements in the DIVs 
    match the ReferencedSOPInstanceUID in the SourceImageSequence."""
    for i in range(len(SecondElements)):
        RefSOPinPFFGS = RefSOPuidsInPFFGS[i]
        
        # Need to -1 since i is zero-indexed:
        ind = SecondElements[i] - 1
        
        RefSOPinRIS = RefSOPuidsInRIS[ind]
        
        if RefSOPinPFFGS == RefSOPinRIS:
            msg = 'INFO:  ReferencedSOPInstanceUID referenced in '\
                  + f'SourceImageSequence {i+1} matches '\
                  + 'ReferencedSOPInstanceUID referenced in '\
                  + 'ReferencedInstanceSequence as indexed by the second '\
                  + f'element in DimensionalIndexValue {i+1}, {DIVs[i]}.\n'
        else:
            msg = 'ERROR:  ReferencedSOPInstanceUID referenced in '\
                  + f'SourceImageSequence {i+1} does not match '\
                  + 'ReferencedSOPInstanceUID referenced in '\
                  + 'ReferencedInstanceSequence as indexed by the second '\
                  + f'element in DimensionalIndexValue {i+1}, {DIVs[i]}.\n'
            
            Nerrors = Nerrors + 1
                  
    LogList.append(msg)
    
    if LogToConsole:
        print(msg)
    
    
    """Determine if ImagePositionPatient in PerFrameFunctionalGroupsSequence 
    matches ImagePositionPatient of the DICOM as indexed by the DIVs."""
    IPPsInPFFGS = [PFFGS[i].PlanePositionSequence[0]\
                           .ImagePositionPatient for i in range(len(PFFGS))]
    
    # Convert from strings to floats:
    IPPsInPFFGS = [[float(item) for item in IPP] for IPP in IPPsInPFFGS]
    
    for i in range(len(IPPsInPFFGS)):
        ind = SOPuids.index(RefSOPuidsInPFFGS[i])
        
        IPP = IPPs[ind]
        
        #if IPPsInPFFGS[i] != IPP:
        if AreListsEqualToWithinEpsilon(IPPsInPFFGS[i], IPP, epsilon):
            msg = f'INFO: ImagePositionPatient {IPPsInPFFGS[i]} '\
                  + f'referenced in PlanePositionSequence {i+1} is within '\
                  + f'{epsilon} of the DICOM ImagePositionPatient {IPP} as '\
                  + f'indexed by the second element {SecondElements[i]} in '\
                  + f'DimensionalIndexValue {i+1}, {DIVs[i]}.\n'
        else:
            msg = f'ERROR: ImagePositionPatient {IPPsInPFFGS[i]} '\
                  + f'referenced in PlanePositionSequence {i+1} is not within'\
                  + f' {epsilon} of the DICOM ImagePositionPatient {IPP} as '\
                  + f'indexed by the second element {SecondElements[i]} in '\
                  + f'DimensionalIndexValue {i+1}, {DIVs[i]}.\n'
            
            Nerrors = Nerrors + 1
                  
    LogList.append(msg)
    
    if LogToConsole:
        print(msg)
    
    
    """Determine whether any of the ReferencedSegmentNumber are not 1 (there
    should only be one segment)."""
    RSNs = [PFFGS[i].SegmentIdentificationSequence[0]\
                    .ReferencedSegmentNumber for i in range(len(PFFGS))]
    
    # Find the indices of any non-matching elements:
    Inds = [i for i, x in enumerate(RSNs) if x != 1]
    
    if Inds:        
        for i in range(len(Inds)):
            msg = f'ERROR:  ReferencedSegmentNumber is {i+1}. '\
                  + 'It should be 1.\n'
            
            Nerrors = Nerrors + 1
    else:
        msg = f'INFO:  ReferencedSegmentNumber is {i+1}. It should be 1.'
        
    LogList.append(msg)
    
    if LogToConsole:
        print(msg)
    
    
    """Determine if the dimensions of the pixel array in PixelData do not
    match the expected dimensions (the number of frames (PixArrF) has 
    already been compared to NumberOfFrames)."""
    if PixArrR == Seg.Rows:
        msg = f'INFO:  The number of rows in PixelData {PixArrR} '\
              + f'matches the number of SEG Rows {Seg.Rows}.\n'
    else:
        msg = f'ERROR:  The number of rows in PixelData {PixArrR} does '\
              + f'not match the number of SEG Rows {Seg.Rows}.\n'
        
        Nerrors = Nerrors + 1
        
    LogList.append(msg)
    
    if LogToConsole:
        print(msg)
            
    if PixArrC == Seg.Columns:
        msg = f'INFO:  The number of columns in PixelData {PixArrC} '\
              + f'matches the number of SEG Columns {Seg.Columns}.\n'
    else:
        msg = f'ERROR:  The number of columns in PixelData {PixArrC} does'\
              + f' not match the number of SEG Columns {Seg.Columns}.\n'
        
        Nerrors = Nerrors + 1
        
    LogList.append(msg)
    
    if LogToConsole:
        print(msg)
    
    
    print(f'\nThere were {Nerrors} errors found in the SEG.')
            
    return LogList, Nerrors