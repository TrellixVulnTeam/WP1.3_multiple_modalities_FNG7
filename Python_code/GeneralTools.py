# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 11:57:05 2020

@author: ctorti
"""


# Import packages:
#from copy import deepcopy
#import numpy as np
#import matplotlib.pyplot as plt

##import importlib
##import DicomTools
##importlib.reload(DicomTools)

#from DicomTools import GetDicomSOPuids

#from SegTools import GetPFFGStoSliceInds



"""
******************************************************************************
******************************************************************************
GENERAL UTILITY FUNCTIONS
******************************************************************************
******************************************************************************
"""


def ItemsUniqueToWithin(List, epsilon=1e-5):
    
    UniqueList = []
    
    L = len(List)
    
    if L < 2:
        print(f'The list has {L} items (it must have at least 2 items).')
        
        return UniqueList
    
    else:
        UniqueList.append(List[0])
        
        for i in range(L - 1):
            if abs(List[i] - List[0]) > epsilon:
                UniqueList.append(List[i])
                
        return UniqueList
    






def FlattenList(ListOfLists):
    if len(ListOfLists) == 0:
        return ListOfLists
    if isinstance(ListOfLists[0], list):
        return FlattenList(ListOfLists[0]) + FlattenList(ListOfLists[1:])
    return ListOfLists[:1] + FlattenList(ListOfLists[1:])







def UniqueItems(Items, IgnoreZero=False, MaintainOrder=False):
    """
    Get list of unique items in a list or Numpy data array.
    
    Inputs:
    ******
    
    Items : list of integers/floats or a Numpy data array
    
    IgnoreZero : boolean (optional; False by default)
        If IgnoreZero=True only unique non-zero items will be returned.
        
    MaintainOrder : boolean (optional; False by default)
        If MaintainOrder=True the unique items will be returned in their
        original order.
        
    
    Outputs:
    *******
    
    UniqueItems : list or Numpy data array or None
        List or Numpy array of unique items, or None if Items is empty.
    """
    
    import numpy as np
    from copy import deepcopy
    
    
    if not isinstance(Items, list) and not isinstance(Items, np.ndarray):
        msg = f'The input "Items" is data type {type(Items)}.  Acceptable '\
              + 'data types are "list" and "numpy.ndarray".'
        
        raise Exception(msg)
    
    
    OrigItems = deepcopy(Items)
    
    if isinstance(Items, list):
        #Items = np.array(Items)
    
        ##Items = list(np.concatenate(Items).flat)
        #Items = np.concatenate(Items)
        
        Items = np.array(FlattenList(Items))
            

    if Items.size == 0:
        return None
    
    
    if IgnoreZero:
        inds = np.nonzero(Items)
        
        Items = [Items[ind] for ind in inds[0]]
    
    if MaintainOrder:
        UniqueItems = []
        
        for item in Items:
            if not item in UniqueItems:
                UniqueItems.append(item)
        
    else:
        #UniqueItems = list(set(Items.tolist()))
        UniqueItems = np.unique(Items)
    
    # If Items was a list convert back to a list:
    if isinstance(OrigItems, list):
        UniqueItems = list(UniqueItems) # 18/12/2020
        #UniqueItems = sorted(list(UniqueItems)) # 18/12/2020
        

    
    return UniqueItems
    






def ReplaceIndInC2SindsByRoi(C2SindsByRoi, IndToReplace, ReplacementInd):
    
    for r in range(len(C2SindsByRoi)):
        for c in range(len(C2SindsByRoi[r])):
            if C2SindsByRoi[r][c] == IndToReplace:
                C2SindsByRoi[r][c] = ReplacementInd
    
    return C2SindsByRoi





    
def AppendItemToListAndSort(OrigList, ItemToAppend):
    """
    Append an item to a list and return the sorted list. 
    
    Inputs:
    ******
    
    OrigList : list
        The list to append to. 
        
    ItemToAppend : string, integer or float
        The item to append to OrigList.
        
        
    Outputs:
    *******
    
    NewList : list
        OrigList with ItemToAppend appended to it and sorted. 
    """
    
    from copy import deepcopy
    
    NewList = deepcopy(OrigList)

    NewList.append(ItemToAppend)
    
    NewList.sort()
    
    return NewList









def Unpack(Items):
    """
    Unpack list of 2D or 3D lists (e.g. [x, y] or [x, y, z] coordinates, or 
    [i, j] or [i, j, k] indices) into separate lists for each dimension.
    
    Inputs:
    ******
    
    Items : list of floats/indices
        List of a list of items, e.g. [[x0, y0, z0], [x1, y1, z1], ...].
     
    
    Outputs:
    *******
    X : list of floats/indices
        List of all x coordinates in Items, e.g. [x0, x1, x2, ...].
    
    Y : list of floats/indices
        List of all y coordinates in Items, e.g. [y0, y1, y2, ...].
    
    Z : list of floats/indices
        List of all z coordinates in Items, e.g. [z0, z1, z2, ...].
    """
    
    import numpy as np
    
    nda = np.array(Items)
    
    if len(nda.shape) < 2:
        msg = "The input argument is a list of length 1. There is nothing to" \
              + " unpack."
        
        raise Exception(msg)
        
    dim = nda.shape[1]
    
    # Initialise unpacked lists:
    X = []
    Y = []
    Z = []
    
    if dim == 2:
        # Unpack tuple and store in X, Y:
        for x, y in Items:
            X.append(x)
            Y.append(y)
            
        return X, Y
    
    elif dim == 3:
        # Unpack tuple and store in X, Y, Z:
        for x, y, z in Items:
            X.append(x)
            Y.append(y)
            Z.append(z)
            
        return X, Y, Z
    
    else:
        msg = f"The input argument has dim = {dim}. Only dim = 2 or dim = 3 "\
              + "is allowed."
        
        raise Exception(msg)








def AreItemsEqualToWithinEpsilon(Item0, Item1, epsilon=1e-06):
    """
    Are two items equal to within epsilon?
    
    Default value of epsilon is 1e-06.
    """
    
    AbsDiff = abs(Item0 - Item1)
    
    if AbsDiff < epsilon:
        IsEqual = True
    else:
        IsEqual = False
        
    return IsEqual






def AreListsEqualToWithinEpsilon(List0, List1, epsilon=1e-06):
    """
    Are two lists equal to within epsilon?
    
    Default value of epsilon is 1e-06.
    """
    
    import numpy as np
    
    # Get the maximum value of their absolute differences:
    AbsDiffs = abs(np.array(List0) - np.array(List1))
    MaxAbsDiff = max(AbsDiffs)
    
    if MaxAbsDiff < epsilon:
        IsEqual = True
    else:
        IsEqual = False
        
    return IsEqual





def NumOfListsAtDepthTwo(NestedList):
    """
    Return the number of lists in a nested list at depth two.
    
    Inputs:
    ******
    
    NestedList : list of a list of a list of items
        A nested list of items.
 
    
    Outputs:
    *******
    
    N : integer
        The total number of lists in a nested list up to two levels down.
    """
    
    N = 0
    
    for i in range(len(NestedList)):
        N = N + len(NestedList[i])
        
    return N






def NumOfItemsInAListByDepth(List):
    """
    Return the number of items in a list at each depth.
    
    Inputs:
    ******
    
    List : a list 
        A list of items or nested list of any number of lists.
 
    
    Outputs:
    *******
    
    NumOfItemsByDepth : list of integers
        The number of items in List at each depth.
    """
    
    NumOfItemsByDepth = []
    
    while isinstance(List, list):
        NumOfItemsByDepth.append(len(List))
        
        NumOfItemsNextDepth = []
        
        for i in range(len(List)): 
            NumOfItemsNextDepth.append(len(List[i]))
        
        """ need to continue... """
        
    return NumOfItemsByDepth








def PrintTitle(Title):
    
    ul = '*' * len(Title)
    print('\n' + Title)
    print(ul + '\n')
    
    return





def PrintIndsByRoi(IndsByRoi):
    
    R = len(IndsByRoi)
    
    for r in range(R):
        if r == 0:
            msg = f'   [{IndsByRoi[r]}'
        else:
            msg = f'    {IndsByRoi[r]}'
        
        if r < R - 1:
            msg += ','
        
        if r == R - 1:
            msg += ']'
                
        print(msg)

    C = [len(IndsByRoi[r]) for r in range(R)]
    
    print(f'   Number of contours in each ROI = {C}')
    
    return




            
            
def IsPointInPolygon(point, vertices):
    """
    Determine if a point lies within a polygon.
    
    Inputs:
    ******
    
    Point : list of floats
        A list of length 3 of floats representing a 3D point.
                     
    Vertices : list of floats
        A list of length 8 of floats for all vertices that define a 3D volume.
        
        
    Outputs:
    *******
    
    PtInPoly : boolean
        True/False if Point is/isn't in Polygon.
        
        
    Note:
    ----
    
    This hasn't been tested on 2D points and 2D polygons.
    """
    
    #from shapely.geometry import Polygon, Point
    from shapely.geometry import Point, MultiPoint
    
    """ Use of Polygon requires that the points be ordered specifically. Use
    of MultiPoint and the convex hull allows for the points to be in a random
    order. """
    
    #polygon = Polygon(vertices)
    polygon = MultiPoint(vertices).convex_hull
    
    point = Point(point)
    
    PtInPoly = polygon.contains(point)
    
    return PtInPoly









def CropNonZerosIn2dMask(Orig2dMask):
    
    import numpy as np
    
    #print('\nShape of Orig2dMask =', Orig2dMask.shape)
    
    # The non-zero elements in the Orig2dMask:
    non0 = np.nonzero(Orig2dMask)
    
    # If there are non-zero elements:
    if non0[0].size:
    
        a = non0[0][0]
        b = non0[0][-1]
        
        c = non0[1][0]
        d = non0[1][-1]
    
        # The non-zero (cropped) array:
        Cropped2dMask = Orig2dMask[a:b, c:d]
        
        #print('\nShape of Cropped2dMask =', Cropped2dMask.shape)
        
        return Cropped2dMask
    
    else:
        #print('There were no non-zero elements in the 2D mask.')
        
        return non0[0]
    




def Compare2dMasksFrom3dMasks(OrigSegRoi, NewSegRoi, OrigDicomDir, NewDicomDir):
    """ Compare cropped masks of non-zero elements only. """ 
    
    from DicomTools import GetDicomSOPuids
    from SegTools import GetPFFGStoSliceInds
    import matplotlib.pyplot as plt
    
    # Get the DICOM SOP UIDs:
    OrigSOPuids = GetDicomSOPuids(DicomDir=OrigDicomDir)
    NewSOPuids = GetDicomSOPuids(DicomDir=NewDicomDir)
    
    # Get the Per-frameFunctionalGroupsSequence-to-slice indices:
    OrigPFFGStoSliceInds = GetPFFGStoSliceInds(OrigSegRoi, OrigSOPuids)
    NewPFFGStoSliceInds = GetPFFGStoSliceInds(NewSegRoi, NewSOPuids)
    
    # Combined indices from OrigPFFGStoSliceInds and NewPFFGStoSliceInds:
    AllInds = OrigPFFGStoSliceInds + NewPFFGStoSliceInds
    
    # Remove duplicates:
    AllInds = list(set(AllInds))
    
    
    # Get the 3D SEG masks:
    Orig3dMask = OrigSegRoi.pixel_array
    New3dMask = NewSegRoi.pixel_array
    
    OrigShape = Orig3dMask.shape
    NewShape = New3dMask.shape
    
    print(f'Segments exist in OrigSegRoi on slices {OrigPFFGStoSliceInds}')
    print(f'Shape of Orig3dMask = {OrigShape}')
    print(f'\nSegments exist in NewSegRoi on slices {NewPFFGStoSliceInds}')
    print(f'Shape of New3dMask = {NewShape}\n')
    
    # Initialise the 3D cropped SEG masks:
    Orig3dMaskCropped = []
    New3dMaskCropped = []
    
    for i in range(OrigShape[0]):
        cropped = CropNonZerosIn2dMask(Orig3dMask[i])
        
        Orig3dMaskCropped.append(cropped)
        
    for i in range(NewShape[0]):
        cropped = CropNonZerosIn2dMask(New3dMask[i])
        
        New3dMaskCropped.append(cropped)
    
    
    Nrows = len(AllInds)
    
    Ncols = 2
    
    n = 1 # initialised sub-plot number
    
    fig, ax = plt.subplots(Nrows, Ncols, figsize=(5*Ncols, 6*Nrows))
    
    for i in range(len(AllInds)):
        SliceNum = AllInds[i]
        
        # Does slice SliceNum have a segment in OrigSegRoi or NewSegRoi?
        if SliceNum in OrigPFFGStoSliceInds:
            OrigFrameNum = OrigPFFGStoSliceInds.index(SliceNum)
        
            ax = plt.subplot(Nrows, Ncols, n, aspect='equal')
            ax.imshow(Orig3dMaskCropped[OrigFrameNum])
            ax.set_xlabel('Pixels'); ax.set_ylabel('Pixels')
            ax.set_title(f'Orig slice {SliceNum}')
            
        n += 1 # increment sub-plot number
        
        if SliceNum in NewPFFGStoSliceInds:
            NewFrameNum = NewPFFGStoSliceInds.index(SliceNum)
    
            ax = plt.subplot(Nrows, Ncols, n, aspect='equal')
            ax.imshow(New3dMaskCropped[NewFrameNum])
            ax.set_xlabel('Pixels'); ax.set_ylabel('Pixels')
            ax.set_title(f'New slice {SliceNum}')
            
        n += 1 # increment sub-plot number
    
    return









def GetPhysicalShiftBetweenSlices(Image0, SliceNum0, Image1, SliceNum1):
    """
    Get the physical shift between SliceNum0 in Image0 and SliceNum1 in Image1
    based on the origins of the two slices (i.e. Image0[0,0,SliceNum0] and
    Image1[0,0,SliceNum1]).
    
    Inputs:
    ******
    
    Image0 : SimpleITK image
    
    SliceNum0 : integer
        The slice number in Image0.
    
    Image1 : SimpleITK image
    
    SliceNum1 : integer
        The slice number in Image1.
    
    
    Outputs:
    *******
    
    mmShift : Numpy array
        Shift in mm between Image0[0,0,SliceNum0] and Image1[0,0,SliceNum1].
    """
    
    import numpy as np
    
    mmShift = np.array(Image1.TransformIndexToPhysicalPoint([0,0,SliceNum1])) \
            - np.array(Image0.TransformIndexToPhysicalPoint([0,0,SliceNum0]))
            
    return mmShift







def GetPixelShiftBetweenSlices(Image0, SliceNum0, Image1, SliceNum1, RefImage,
                               Fractional=False):
    """
    Get the shift in pixels between SliceNum0 in Image0 and SliceNum1 in Image1
    based on the origins of the two slices (i.e. Image0[0,0,SliceNum0] and
    Image1[0,0,SliceNum1]).
    
    Inputs:
    ******
    
    Image0 : SimpleITK image
    
    SliceNum0 : integer
        The slice number in Image0.
    
    Image1 : SimpleITK image
    
    SliceNum1 : integer
        The slice number in Image1.
        
    RefImage : SimpleITK image
        The reference image whose voxel spacings will be used to convert the
        physical shift to pixels.
    
    Fractional : boolean (optional; False by default)
        If True the pixel shift will be rounded to the nearest integer value.
    
    
    Outputs:
    *******
    
    PixShift : Numpy array
        Shift in pixels between Image0[0,0,SliceNum0] and Image1[0,0,SliceNum1].
    """
    
    import numpy as np
    
    mmShift = GetPhysicalShiftBetweenSlices(Image0, SliceNum0, 
                                            Image1, SliceNum1)
    
    PixSpacing = np.array(RefImage.GetSpacing())
    
    PixShift = mmShift/PixSpacing
    
    if not Fractional:
        PixShift = np.round(PixShift).astype('int')
            
    return PixShift






    
def ShiftFrame(Frame, PixShift):
    """
    Shift the items in a 2D frame.
    
    Inputs:
    ******
    
    Frame : Numpy array
        A 2D frame from PixelData with shape (1, R, C), where R = number of 
        rows, and C = number of columns.
        
    PixShift : Numpy array
        Shift in pixels, e.g. [di, dj, dz].
        
    
    Outputs:
    *******
    
    ShiftedFrame : Numpy array
        Shifted frame with shape (1, R, C). Only the x- and y-components are 
        shifted.
    """
    
    import numpy as np
    
    F, R, C = Frame.shape
    
    if F > 1:
        msg = f"'Frame' must be a 2D frame with shape (1, R, C) but has shape"\
              + f" ({F}, {R}, {C})."
        
        raise Exception(msg)
    
    # Initialise ShiftedFrame:
    ShiftedFrame = np.zeros((1, R, C), dtype='uint')
    #ShiftedFrame = np.empty_like(Frame, dtype='uint') # this creates 42,932
    # unique values for some reason!
    
    #unique = UniqueItems(Nda=Frame, NonZero=False)
    #print(f'\n---> There are {len(unique)} unique items in Frame')
    #unique = UniqueItems(Nda=ShiftedFrame, NonZero=False)
    #print(f'\n---> There are {len(unique)} unique items in the initialised',
    #      f'ShiftedFrame: {unique[:11]}...')
    
    di, dj, dk = PixShift
    
    ##ShiftedFrame[0, dj:, di:] = Frame[0, :-(1+dj), :-(1+di)]
    ##ShiftedFrame[0, :-(1+dj), :-(1+di)] = Frame[0, dj:, di:]
    #ShiftedFrame[0, :R-dj, :C-di] = Frame[0, dj:, di:]
    
    if di > 0 and dj > 0:
        ShiftedFrame[0, dj:, di:] = Frame[0, :-dj, :-di]
        
    elif di < 0 and dj < 0:
        ShiftedFrame[0, :dj, :di] = Frame[0, -dj:, -di:]
        
    elif di > 0 and dj < 0:
        ShiftedFrame[0, :dj, di:] = Frame[0, -dj:, :-di]
        
    elif di < 0 and dj > 0:
        ShiftedFrame[0, dj:, :di] = Frame[0, :-dj, -di:]
        
    elif di == 0 and dj > 0:
        ShiftedFrame[0, dj:, :] = Frame[0, :-dj, :]
        
    elif di == 0 and dj < 0:
        ShiftedFrame[0, :dj, :] = Frame[0, -dj:, :]
        
    elif di > 0 and dj == 0:
        ShiftedFrame[0, :, di:] = Frame[0, :, :-di]
        
    elif di < 0 and dj == 0:
        ShiftedFrame[0, :, :di] = Frame[0, :, -di:]
        
    elif di == 0 and dj == 0:
        ShiftedFrame[0] = Frame[0]
        
    #unique = UniqueItems(Nda=ShiftedFrame, NonZero=False)
    #print(f'\n---> There are {len(unique)} unique items in the ShiftedFrame',
    #      'after shifting.')
            
    return ShiftedFrame







def ShiftFramesInPixArrByRoi(PixArrByRoi, F2SindsByRoi, SrcImage, SrcSliceNum,
                             TrgImage, TrgSliceNum, RefImage, Fractional=False,
                             LogToConsole=False):
    """
    Shift the items in each frame of each pixel array in a list of 
    pixel-arrays-by-ROI.  This is intended for use with single-framed pixel
    arrays, as in the case of a direct copy to a specified slice.
    
    Inputs:
    ******
    
    PixArrByRoi : list of Numpy arrays
        A list (for each ROI) of pixel arrays.
    
    F2SindsByRoi : list of a list of integers
        List (for each ROI) of a list (for each frame) of slice numbers that 
        correspond to each frame in the pixel arrays in PixArrByRoi.
        
    SrcImage : SimpleITK image
        The Source 3D image.
    
    SrcSliceNum : integer
        The slice number within the Source image stack that the ROI relates to.
    
    TrgImage : SimpleITK image
        The Target 3D image.
    
    TrgSliceNum : integer
        The slice number within the Target image stack that the ROI is to be 
        copied to following the shift in z-components.
        
    RefImage : SimpleITK image
        The reference image whose voxel spacings will be used to convert the
        physical shift to pixels (e.g. TrgImage).
    
    Fractional : boolean (optional; False by default)
        If True the pixel shift will be rounded to the nearest integer value.
    
    LogToConsole : boolean (optional; False by default)
        Denotes whether some results will be logged to the console.
    
    
    Outputs:
    *******
    
    PixArrByRoi : list of Numpy arrays
        As above but with shifted frame with shape (1, R, C). Only the x- and 
        y-components are shifted.
    """
    
    # Get pixel shift between FromSliceNum in SrcIm and ToSliceNum in 
    # TrgIm in the Target image domain:
    PixShift = GetPixelShiftBetweenSlices(Image0=SrcImage, SliceNum0=SrcSliceNum, 
                                          Image1=TrgImage, SliceNum1=TrgSliceNum,
                                          RefImage=TrgImage)
    
    if LogToConsole:
        print(f'\nPixShift = {PixShift}')
            
    
    for r in range(len(PixArrByRoi)):
        #if PixArrByRoi[r]:
        if PixArrByRoi[r].shape[0]: 
            # Replace PixArrByRoi[r] with the result of shifting the in-plane 
            # elements, and replace F2SindsByRoi[r] with [TrgSliceNum]:
            PixArrByRoi[r] = ShiftFrame(Frame=PixArrByRoi[r], PixShift=PixShift)
            F2SindsByRoi[r] = [TrgSliceNum]
            
            if LogToConsole:
                unique = UniqueItems(Items=PixArrByRoi[r], IgnoreZero=False)
                
                print(f'\nThere are {len(unique)} unique items in',
                      f'PixArrByRoi[{r}] after shifting the frame.')
    
        
    return PixArrByRoi
    
    





def ChangeZinds(Indices, NewZind):
    """
    Re-assign the z-components of a list of indeces (as required when
    making a direct copy of contour points).
    
    Inputs:
    ******
    
    Indices : list of a list of integers
        List (for each point) of a list (for each dimension) of indices, 
        e.g. [[i0, j0, k0], [i1, j1, k1], ...].
        
    NewZind : integer
        The value to re-assign to the z-components (i.e. k) of Indeces (e.g.
        ToSliceNum).
    
    
        
    Ouputs:
    ******
    
    Indices : list of a list of integers
        List (for each point) of a list (for each dimension) of the indices 
        with modified z-components, e.g. [[i0, j0, k0], [i1, j1, k1], ...].
    """
    
    if not isinstance(NewZind, int):
        raise Exception(f"NewZind = {NewZind} must be an integer.")
    
    for i in range(len(Indices)):
        Indices[i][2] = NewZind
        
    return Indices







def ZshiftPtsByCntByRoi(PtsByCntByRoi, NewZind, DicomDir):
    """
    Shift the z-component of the points in PtsByCntByRoi (as required when
    making a direct copy of contour points).
    
    Inputs:
    ******
    
    PtsByCntByRoi : list of list of a list of a list of floats
        List (for each ROI) of a list (for all contours) of a list (for each
        point) of a list (for each dimension) of coordinates.
        
    NewZind : integer
        The value to re-assign to the z-components (i.e. k) of Indeces (e.g.
        ToSliceNum).
    
    DicomDir : string 
        Directory containing the corresponding DICOMs.
    
        
    Ouputs:
    ******
    
    NewPtsByCntByRoi : list of list of a list of a list of floats
        As PtsByCntByRoi but with modified z-components.
    """
    
    from ImageTools import ImportImage
    from ConversionTools import Points2Indices, Indices2Points
    
    # Import the image:
    Im = ImportImage(DicomDir)
    
    """ Convert PtsByCntByRoi to indices, modify the z-component of the
    indices, then convert back to physical points. """
    
    IndsByCntByRoi = []
    NewPtsByCntByRoi = []
    
    # Iterate through ROIs:
    for r in range(len(PtsByCntByRoi)): 
        IndsByCnt = []
        NewPtsByCnt = []
        
        if PtsByCntByRoi[r]:
            # Iterate through contours:
            for c in range(len(PtsByCntByRoi[r])):
                pts = PtsByCntByRoi[r][c]
                
                inds = Points2Indices(Points=pts, RefIm=Im, Rounding=False)
                
                # Modify the z-component (k) of the indices to NewZind:
                inds = ChangeZinds(inds, NewZind)
                
                IndsByCnt.append(inds)
                
                # Convert back to physical points:
                pts = Indices2Points(inds, RefIm=Im)
                
                NewPtsByCnt.append(pts)
        
        IndsByCntByRoi.append(IndsByCnt)
        NewPtsByCntByRoi.append(NewPtsByCnt)
        
    return NewPtsByCntByRoi



    
    

def MeanPixArr(PixArr, MakeBinary=True, BinaryThresh=0.5):
    """
    Perform pixel-by-pixel mean of all frames in a pixel array. Output a 
    binary pixel array if binary=True (or undefined).
    
    Inputs:
    ******
    
    PixArr : Numpy array
        PixelData from a SEG file loaded as a Numpy array
        
    MakeBinary : boolean (optional; True by default)
        If MakeBinary = True the mean pixel array will be converted to a binary
        pixel array by thresholding pixel values by BinaryThreshold.
    
    BinaryThreshold : float (optional; 0.5 by default)
        The threshold that will be used when converting to a binary pixel array
        if MakeBinary = True.
        
        
    Outputs:
    *******
    
    MeanPixArr : Numpy array
        Mean pixel array.
    """
    
    import numpy as np
    
    F, R, C = PixArr.shape
    
    # Initialise MeanPixArr:
    MeanPixArr = np.zeros((1, R, C), dtype='uint')
    
    result = np.mean(PixArr, axis=0)
            
    if MakeBinary:
        MeanPixArr[0] = (result >= BinaryThresh) * result
    else:
        MeanPixArr[0] = result
        
    return MeanPixArr






def MeanPixArrByRoi(PixArrByRoi, MakeBinary=True, BinaryThresh=0.5,
                    LogToConsole=False):
    """
    Perform pixel-by-pixel mean of all frames in all pixel arrays in a list
    of pixel-arrays-by-ROI which have more than 1 frame. No changes will be
    made to empty or single-framed pixel arrays.
    
    Inputs:
    ******
    
    PixArrByRoi : list of Numpy arrays
        A list (for each ROI) of pixel arrays.
        
    MakeBinary : boolean (optional; True by default)
        If MakeBinary = True the mean pixel array will be converted to a binary
        pixel array by thresholding pixel values by BinaryThreshold.
    
    BinaryThreshold : float (optional; 0.5 by default)
        The threshold that will be used when converting to a binary pixel array
        if MakeBinary = True.
    
    LogToConsole : boolean (optional; False by default)
        Denotes whether some results will be logged to the console.
    
        
    Outputs:
    *******
    
    PixArrByRoi : list of Numpy arrays
        A list (for each ROI) of pixel arrays averaged to a single-framed
        pixel array.
    """
    
    # Determine the number of frames in each pixel array: 
    NumOfFramesByRoi = [PixArr.shape[0] for PixArr in PixArrByRoi]
    
    for r in range(len(PixArrByRoi)):
        if NumOfFramesByRoi[r] > 1: 
            if LogToConsole:
                print(f'\nPixArrByRoi[{r}] has {NumOfFramesByRoi[r]} frames',
                      'so the pixel arrays will be averaged.')
            
            # Replace PixArrByRoi[r] with the pixel-by-pixel mean across all 
            # frames in the pixel array:
            PixArrByRoi[r] = MeanPixArr(PixArrByRoi[r], MakeBinary,
                                        BinaryThresh)
            
            if LogToConsole:
                print(f'\nPixArrByRoi[{r}] had {NumOfFramesByRoi[r]} frames,',
                      f'but now has {PixArrByRoi[r].shape[0]}.')
        else:
            if LogToConsole:
                print(f'\nPixArrByRoi[{r}] has {NumOfFramesByRoi[r]} frames,',
                      'so no frame averaging was required.')
        
    return PixArrByRoi







def OrPixArrByRoi(PixArrByRoi, LogToConsole=False):
    """
    Perform pixel-by-pixel logical OR of all frames in all pixel arrays in a 
    list of pixel-arrays-by-ROI which have more than 1 frame. No changes will 
    be made to empty or single-framed pixel arrays.
    
    Inputs:
    ******
    
    PixArrByRoi : list of Numpy arrays
        A list (for each ROI) of pixel arrays.
    
    LogToConsole : boolean (optional; False by default)
        Denotes whether some results will be logged to the console.
    
        
    Outputs:
    *******
    
    PixArrByRoi : list of Numpy arrays
        A list (for each ROI) of pixel arrays averaged to a single-framed
        pixel array.
    """
    
    import numpy as np
    
    # Determine the number of frames in each pixel array: 
    NumOfFramesByRoi = [PixArr.shape[0] for PixArr in PixArrByRoi]
    
    # Get the shape of any pixel array:
    F, R, C = PixArrByRoi[0].shape
    
    for r in range(len(PixArrByRoi)):
        if NumOfFramesByRoi[r] > 1: 
            if LogToConsole:
                print(f'\nPixArrByRoi[{r}] has {NumOfFramesByRoi[r]} frames',
                      'so the pixel arrays will be logically ORed.')
            
            # Replace PixArrByRoi[r] with the pixel-by-pixel logical OR across 
            # all frames in the pixel array:
            OrPixArr = PixArrByRoi[r].any(axis=0)
            
            # Reshape to a (1, R, C) pixel array:
            PixArrByRoi[r] = np.reshape(OrPixArr, (1, R, C))
            
            if LogToConsole:
                print(f'\nPixArrByRoi[{r}] had {NumOfFramesByRoi[r]} frames,',
                      f'but now has {PixArrByRoi[r].shape[0]}.')
        else:
            if LogToConsole:
                print(f'\nPixArrByRoi[{r}] has {NumOfFramesByRoi[r]} frames,',
                      'so no logical ORing was required.')
        
    return PixArrByRoi







def Distance(item0, item1):
    """
    Compute the distance between points or indices.  
    
    Inputs:
    ******
    
    item0 : list of floats/integers
        A 2D/3D point or point indices.
        
    item1 : list of floats/integers
        A 2D/3D point or point indices.
    
    
    Outputs:
    *******
    
    distance : float/integer
        Distance between item0 and item1 in Euclidean space or in pixels.
    """
    
    SumOfDims = len(item0) + len(item1)
    
    if SumOfDims == 4:
        # 2D points/indices.
        distance = ((item0[0] - item1[0])**2 \
                    + (item0[1] - item1[1])**2)**0.5
                    
        return distance
        
    elif SumOfDims == 6:
        # 3D points/indices.
        distance = ((item0[0] - item1[0])**2 \
                    + (item0[1] - item1[1])**2 \
                    + (item0[2] - item1[2])**2)**0.5
                    
        return distance
        
        
    else:
        msg = "The inputs must both be 2D or 3D lists of points/indices."
        
        raise Exception(msg)
        
        
        
        
def SplitString(String, SearchString, Separator='_'):
    """
    Split a string to the string of characters on either side of a search
    string bounded by a separator.  
    
    Inputs:
    *******
    
    String : string
        The input string to be separated.
        
    SearchString : string
        The string that defines the split point.
        
    Separator : string (optional; '_' by default)
        The string that separates words within a string.
        
        e.g. The string "Series-4-Slice-9" has separator '-'; The string
        "Series_4_Slice_9" has separator '_'.
        
        
    Outputs:
    *******
        
    StringList : list of strings
        A list of length two of strings (e.g. ['string0', 'string1']).
    """
    
    StringSplit = String.split(Separator)
    
    ind = StringSplit.index(SearchString)
    
    StringList = []
    
    if ind - 1 < 0:
        StringList.append('')
    else:
        StringList.append(StringSplit[ind-1])
        
    if ind + 1 >= len(StringSplit):
        StringList.append('')
    else:
        StringList.append(StringSplit[ind+1])
        
    return StringList





def SliceNoFromFpath(Fpath, SearchString, Separator='_'):
    """
    Parse a filepath for a slice number based on a search string and (optional)
    separator.  This will only work for specific filepath formats.
    
    Inputs:
    *******
    
    Fpath : string
        The filepath to be parsed.
        
    SearchString : string
        The string that identifies the slice number.
        
        e.g. The string "S4_slice9" would require the search string "slice";
        The string "S4_s9" would require "s".
        
    Separator : string (optional; '_' by default)
        The string that separates words within a string.
        
        e.g. The string "S4-s9" has separator '-'; The string "S4_s9" has 
        separator '_'.
        
        
    Outputs:
    *******
        
    SliceNo : int
        The slice number parsed from Fpath.
    """
    
    from os.path import split, splitext
    
    Fname = split(splitext(Fpath)[0])[1]
    
    IntString = Fname.split(SearchString)[1]
    
    try:
        SliceNo = int(IntString)
        
        return SliceNo
        
    except ValueError:
        msg = f'Cannot convert {IntString} into int. \nFpath = {Fpath}, \n' \
              + f'Fname = {Fname}, \nIntString = {IntString}.'
        
        print(msg)
        
        return None





def DataTypeOfElementsInList(Lst, Unique=True):
    """
    Return a list of the data type of the elements in the list.  If the input
    Unique is True or omitted, the set of data types will be returned.  Hence
    a single-itemed list containing a single data type is a permitted output.
    
    Inputs:
    *******
    
    Lst : list of items
        A list of items (e.g. integers, floats, strings, etc.).
        
    Unique : boolean (optional; True by default)
        If True the set of data types will be returned (i.e. only unique data
        types).
        
        
    Outputs:
    *******
        
    Dtypes : list of data types
        A list of the data type of each item in Lst.
    """
    
    Dtypes = [type(item) for item in Lst]
    
    if Unique:
        Dtypes = list(set(Dtypes))
    
    return Dtypes







def ParseTransformParameterFile(Fpath, ParamName):
    """
    Parse a SimpleElastix TransformParameters text file for the value(s) of
    various parameters.
            
    Inputs:
    ******
    
    Fpath : string
        The full filepath of TransformParameters text file.
        
    ParamName : string
        Character string of the parameter name to search and parse.
        
        
    Outputs:
    *******
    
    ParamValues : strings, integers or floats (depends on the parameter of 
    interest)
        The value(s) of the parameter of interest.
    
    
    Notes:
    -----
    
    1.  The text file contains data of the following format:
            
        (FixedImageDimension 2)     <-- single value
        (Size 256 256)              <-- two values
        
    2. See further notes below.
    """

    # Determine whether the parameters need to be converted to integers or
    # float.  
    
    # Create a list of parameter names that belong to int and float data types:
    """
    Notes: 
        1. Many of the parameters are to remain as strings.
        2. The lists below only cover the default parameters, so any additional
           parameters will need to be added.
        3. If the parameter is not found to be in ints or floats it will be 
           assumed that the parameter is a string.
    """
    
    IntParams = ['NumberOfParameters', 'FixedImageDimension', 
                 'MovingImageDimension', 'Size', 'Index', 
                 'FinalBSplineInterpolationOrder']
    
    FloatParams = ['TransformParameters', 'Spacing', 'Origin', 'Direction', 
                   'CenterOfRotationPoint', 'DefaultPixelValue']
    
    if ParamName in IntParams:
        dtype = 'int'
    elif ParamName in FloatParams:
        dtype = 'float'
    else:
        dtype = 'string'
        
    
    # Read in the file:
    FileTxt = open(Fpath, 'r').read()
    
    #print('\nFileTxt:\n', FileTxt)
    
    # Get index of string variable parameter:
    a = FileTxt.index(ParamName)
    
    #print(f'\na = {a}')
    
    """ Note:
    The text file has values encoded in the following format:
    (ParameterName ParameterValue1 ParameterValue2 ...)
    
    so the values begin at a+len(ParameterName)+1 and end at the position 
    before ')'.
    """
    StartInd = a + len(ParamName) + 1 # to account for the space after 
    # ParameterName
    
    #print(f'\nStartInd = {StartInd}')
    
    # Find the position of the first ')' after StartInd:
    b = StartInd + FileTxt[StartInd:].index(')')
    
    #print(f'\nb = {b}')
    
    EndInd = b
    
    #print(f'\nEndInd = {EndInd}')
    
    # Crop the text between StartInd and EndInd:
    CroppedTxt = FileTxt[StartInd:EndInd]
    
    #print(f'\nCroppedTxt = {CroppedTxt}')
    
    """ Note:
    CroppedTxt may be single value or may have multiple values. 
    e.g. (FixedImageDimension 2) <-- single value
         (Size 256 256) <-- two values
         
    If CroppedTxt doesn't contain the space character simply return CroppedTxt.
    If CroppedTxt has a space character, slice and append the elements that 
    preceed it to a new array called ParameterValues, then search for another 
    space, repeat until there are no more spaces.
    """
    # Check if there are any space characters in CroppedTxt:
    AreThereSpaces = ' ' in CroppedTxt
    
    #print('\nAreThereSpaces =', AreThereSpaces)
    
    if AreThereSpaces:
        ParamValues = []
        
        # Continue as long as AreThereSpaces is True:
        while AreThereSpaces:
            # Find the first space character:
            ind = CroppedTxt.index(' ')

            # Slice the characters from 0 to ind:
            ParamValues.append(CroppedTxt[0:ind])
            
            # Remove from CroppedTxt the characters that were appended to 
            # ParamValues but not including the space character:
            CroppedTxt = CroppedTxt[ind+1:]
            
            #print(f'\n   CroppedTxt = {CroppedTxt}')
            
            # Check if there are any space characters in CroppedTxt:
            AreThereSpaces = ' ' in CroppedTxt
            
            #print('\n   AreThereSpaces =', AreThereSpaces)
            
        # There are no remaining spaces so simply append what remains of
        # CroppedTxt to ParamValues:
        if CroppedTxt:
            ParamValues.append(CroppedTxt)
            
        #return ParamValues
        if dtype=='int':
            return [int(item) for item in ParamValues]
        elif dtype=='float':
            return [float(item) for item in ParamValues]
        else:
            return ParamValues
        
    else:
        #return CroppedTxt
        if dtype=='int':
            return [int(item) for item in CroppedTxt]
        elif dtype=='float':
            return [float(item) for item in CroppedTxt]
        else:
            return CroppedTxt
        




def GetVectorLength(Vector):
    """
    Get vector length.
    
    Inputs:
    ******
    
    Vector : list of floats
        A list (for each dimension) of vector components along each axis,
        e.g. [Vx, Vy, Vz] or [Vx, Vy].
        
        
    Outputs:
    *******
    
    VectorL : float
        The length of Vector.
    """
    
    dim = len(Vector)
        
    if dim == 2:
        VectorL = ( Vector[0]**2 + Vector[1]**2 ) ** 0.5
        
    elif dim == 3:
        
        VectorL = ( Vector[0]**2 + Vector[1]**2 + Vector[2]**2 ) ** 0.5
        
    else:
        msg = f'The vector has dim {dim}. It must have 2 or 3 dimensions.'
        
        raise Exception(msg)
    
        
    return VectorL






def SumOfSquaresOfMatrix(Matrix):
    """
    Compute the root-sum-of-squares of a matrix.
    
    Inputs:
    ******
    
    Matrix : Numpy array
        A Numpy array (including matrices).
        
        
    Outputs:
    *******
    
    RSS : float
        The root-sum-of-squares of Matrix.
    """
    
    from numpy import sqrt, sum, square
    
    RSS = sqrt(sum(square(Matrix)))
    
    return RSS







def IsMatrixOrthogonal_OLD(Matrix):
    """
    Determine if a matrix is orthogonal.
    
    Inputs:
    ******
    
    Matrix : Numpy array of square shape
        A Numpy matrix of square shape.
        
        
    Outputs:
    *******
    
    IsOrthogonal : boolean
        True if Matrix is orthogonal, False otherwise.
        
        
    Notes:
    -----
    
    The following tests for orthogonality of a matrix M: 
        
        M is orthogonal if M*M.T = M.T*M, 
        i.e. if np.dot(M, M.T) - np.dot(M.T, M) = 0
    
    
    
    The following tests for orthonomality of a matrix M: 
        
        M is orthonormal if its determinant (np.linalg.det(M)) = +/- 1.
        
        M is orthonormal if M*M.T = I, where I is the identity matrix, 
        i.e. if np.dot(M, M.T) - np.identity(M.shape[0]) = 0
        
        M is orthonormal if M.T = M^-1, 
        i.e. if M.T - np.linalg.inv(M) = 0
        
        
        
    The following test for orthonormality/orthogonality doesn't provide the 
    expected result for either an orthogonal or orthonormal matrix:
        
        M is orthogonal if M.T x M^-1 = I, where I is the identity matrix,
        i.e. if np.cross(M.T, np.linalg.inv(M)) - np.identity(M.shape[0]) = 0
    """
    
    import numpy as np
    
    M = Matrix
    
    #shape = M.shape
    
    if len(M.shape) != 2:
        msg = f'The matrix has {len(M.shape)} dimensions. It must have 2.'
        
        raise Exception(msg)
        
    if M.shape[0] != M.shape[1]:
        msg = f'The matrix has shape {M.shape}. It must be a square matrix.'
        
        raise Exception(msg)
        
    
    Det = np.linalg.det(M)
    
    DotProdResult_1 =  np.dot(M, M.T) - np.identity(M.shape[0])
    
    DotProdResult_2 =  np.dot(M, M.T) - np.dot(M.T, M)
    
    DetInvResult = M.T - np.linalg.inv(M)
    
    CrossProdResult = np.cross(M.T, np.linalg.inv(M)) - np.identity(M.shape[0])
    
    
    IsDet1 = AreItemsEqualToWithinEpsilon(abs(Det), 1, epsilon=1e-06)
    
    SSEofDPR_1 = SumOfSquaresOfMatrix(DotProdResult_1)
    IsDPR0_1 = AreItemsEqualToWithinEpsilon(SSEofDPR_1, 0, epsilon=1e-06)
    
    SSEofDPR_2 = SumOfSquaresOfMatrix(DotProdResult_2)
    IsDPR0_2 = AreItemsEqualToWithinEpsilon(SSEofDPR_2, 0, epsilon=1e-06)
    
    SSEofDIR = SumOfSquaresOfMatrix(DetInvResult)
    IsDIR0 = AreItemsEqualToWithinEpsilon(SSEofDIR, 0, epsilon=1e-06)
    
    SSEofCPR = SumOfSquaresOfMatrix(CrossProdResult)
    IsCPR0 = AreItemsEqualToWithinEpsilon(SSEofCPR, 0, epsilon=1e-06)
    
    
    print(f'\nThe determinant of M = {Det} (must be +/- 1 if M is orthogonal).')
    print(f'\nM*M.T - I = {SSEofDPR_1} (must be 0 if M is orthogonal).')
    print(f'\nM*M.T - M.T*M = {SSEofDPR_2} (must be 0 if M is orthogonal).')
    print(f'\nM.T - M^-1 = {SSEofDIR} (must be 0 if M is orthogonal).')
    print(f'\nM.T x M^-1 - I = {SSEofCPR} (must be 0 if M is orthogonal).')
        
        
    return IsDPR0_1







def IsMatrixOrthogonal(Matrix, LogToConsole=False):
    """
    Determine if a matrix is orthogonal.
    
    Inputs:
    ******
    
    Matrix : Numpy array of square shape
        A Numpy matrix of square shape.
        
    LogToConsole : boolean (optional; False by default)
        Denotes whether intermediate results will be logged to the console.
        
        
    Outputs:
    *******
    
    IsOrthogonal : boolean
        True if Matrix is orthogonal, False otherwise.
        
        
    Notes:
    -----
    
    The following tests for orthogonality of a matrix M: 
        
        M is orthogonal if M*M.T = M.T*M, 
        i.e. if np.dot(M, M.T) - np.dot(M.T, M) = 0
    """
    
    import numpy as np
    
    M = Matrix
    
    if len(M.shape) != 2:
        msg = f'The matrix has {len(M.shape)} dimensions. It must have 2.'
        
        raise Exception(msg)
        
    if M.shape[0] != M.shape[1]:
        msg = f'The matrix has shape {M.shape}. It must be a square matrix.'
        
        raise Exception(msg)
        
    
    result =  np.dot(M, M.T) - np.dot(M.T, M)
    
    SSE = SumOfSquaresOfMatrix(result)
    
    IsOrthogonal = AreItemsEqualToWithinEpsilon(SSE, 0, epsilon=1e-06)
    
    if LogToConsole:
        print(f'\nM*M.T - M.T*M = \n{result}')
        print(f'\nSSE = {SSE}')
        
        if IsOrthogonal:
            print(f'\nM is orthogonal')
        else:
            print(f'\nM is not orthogonal')
        
        
    return IsOrthogonal






def IsMatrixOrthonormal(Matrix, LogToConsole=False):
    """
    Determine if a matrix is orthonormal.
    
    Inputs:
    ******
    
    Matrix : Numpy array of square shape
        A Numpy matrix of square shape.
    
    LogToConsole : boolean (optional; False by default)
        Denotes whether intermediate results will be logged to the console.
    
        
    Outputs:
    *******
    
    IsOrthonormal : boolean
        True if Matrix is orthonormal, False otherwise.
        
        
    Notes:
    -----
    
    The following tests for orthonomality of a matrix M: 
        
        M is orthonormal if its determinant (np.linalg.det(M)) = +/- 1.
        
        M is orthonormal if M*M.T = I, where I is the identity matrix, 
        i.e. if np.dot(M, M.T) - np.identity(M.shape[0]) = 0
        
        M is orthonormal if M.T = M^-1, 
        i.e. if M.T - np.linalg.inv(M) = 0
    """
    
    import numpy as np
    
    M = Matrix
    
    if len(M.shape) != 2:
        msg = f'The matrix has {len(M.shape)} dimensions. It must have 2.'
        
        raise Exception(msg)
        
    if M.shape[0] != M.shape[1]:
        msg = f'The matrix has shape {M.shape}. It must be a square matrix.'
        
        raise Exception(msg)
        
    
    Det = np.linalg.det(M)
    IsOrthonormal = AreItemsEqualToWithinEpsilon(abs(Det), 1, epsilon=1e-06)
    
    MdotM_T =  np.dot(M, M.T) - np.identity(M.shape[0])
    SSEofMdotM_T = SumOfSquaresOfMatrix(MdotM_T)
    #IsOrthonormal = AreItemsEqualToWithinEpsilon(SSEofMdotM_T, 0, 
    #                                             epsilon=1e-06)
    
    TequalsInv = M.T - np.linalg.inv(M)
    SSEofTequalsInv = SumOfSquaresOfMatrix(TequalsInv)
    #IsOrthonormal = AreItemsEqualToWithinEpsilon(SSEofTequalsInv, 0, 
    #                                             epsilon=1e-06)
    
    
    if LogToConsole:
        print(f'\nThe determinant of M = {Det}')
        print(f'\nM*M.T - I = \n{MdotM_T}')
        print(f'\nSSE = {SSEofMdotM_T}')
        print(f'\nM.T - M^-1 = \n{SSEofTequalsInv}')
        print(f'\nSSE = {SSEofTequalsInv}')
        
        if IsOrthonormal:
            print(f'\nM is orthonormal')
        else:
            print(f'\nM is not orthonormal')
        
    return IsOrthonormal





def GetTxMatrixType(LogToConsole=False):
    """
    Determine the Transformation Matrix Type from a list of transformation 
    parameters read from the TransformParameters.0.txt file exported by
    Elastix following an image registration and assumed to be in the current
    working directory.
    
    Inputs:
    ******
    
    LogToConsole : boolean (optional; False by default)
        Denotes whether intermediate results will be logged to the console.
    
        
    Outputs:
    *******
    
    MatrixType : string
        A string containing the matrix type.  Acceptable outputs are:
        'RIGID', 'RIGID_SCALE' or 'AFFINE'.
        
        
    Notes:
    -----
    
    1. The transform parameters will be read from the file 
    TransformParameters.0.txt.  The file is generated by Elastix following an
    image registration, found in the current working directory. It will be 
    assumed that the file is located in the current working directory and that
    the filename is as above.
    
    2. The matrix M is the 3x3 matrix within the 4x4 matrix TxParams read from
    TransformParameters.0.txt.  M only includes the elements that describe 
    rotations, scaling and shearing, i.e not translations (hence only the
    elements [0, 1, 2, 4, 5, 6, 8, 9, 10] in TxParams).
    
    3. There are three types of Registration matrices as defined in C.X.1.1.2
    (page 27) in DICOM Standard Supplement 7.3:
        
        RIGID: 
        - a registration involving only translations and rotations
        - the matrix contains 6 degrees of freedom: 3 translations and 3 
        rotations
        - the matrix must be orthnormal
        
        RIGID_SCALE:
        - a registration involving only translations, rotations and scaling
        - the matrix contains 9 degrees of freedom: 3 translations, 3 rotations
        and 3 scales
        - the matrix must be orthogonal
        
        AFFINE:
        - a registration involving translations, rotations, scaling and 
        shearing
        - the matrix contains 12 degrees of freedom: 3 translations, 3 
        rotations, 3 scales and 3 shears
        - there are no constraints on the matrix elements
    """
    
    import os
    import numpy as np
    
    ParamFname = 'TransformParameters.0.txt'
    ParamFpath = os.path.join(os.getcwd(), ParamFname)

    TxParams = ParseTransformParameterFile(ParamFpath, 'TransformParameters')
    
    inds = [0, 1, 2, 4, 5, 6, 8, 9, 10]

    M = np.array([TxParams[i] for i in inds])
    
    M = np.reshape(M, (3, 3))
    
    IsOrthonormal = IsMatrixOrthonormal(M, LogToConsole)
    
    if IsOrthonormal:
        MatrixType = 'RIGID'
    else:
        IsOrthogonal = IsMatrixOrthogonal(M, LogToConsole)
        
        if IsOrthogonal:
            MatrixType = 'RIGID_SCALE'
        
        else:
            MatrixType = 'AFFINE'
            
            
    if LogToConsole:
        print('Matrix type is', MatrixType)
    
    return MatrixType
        