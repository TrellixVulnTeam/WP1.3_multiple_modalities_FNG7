# -*- coding: utf-8 -*-
"""
Created on Mon Jul 13 09:50:23 2020

@author: ctorti
"""



""" 

******************************************************************************
******************************************************************************
Contour interpolating functions
******************************************************************************
******************************************************************************


The following dictionaries are used as inputs to some of the following 
functions and are appended to by others:
   
***************
FixContourData:
***************

A dictionary of the contour points belonging to the Fixed (input) image, 
containing the keys:

    
  'SliceNo'     - List of integers (for original contour points) or floats (for
                  interpolated contours that correspond to non-imaged planes,
                  e.g. slice interpolated at 2.5 in between slices 2 and 3).
                  
  'ContourType' - List of integers for each DICOM slice; 
                  The integer value denotes whether there is or is not contour 
                  data for any given slice, and if there is, whether it is an
                  original contour, an interpolated contour, or transformed 
                  contour.
                  0 -> No contour points 
                  1 -> Original contour points
                  2 -> Interpolated contour points
                  3 -> Transformed contour points
                  
  'PointPCS'    - List of input points in the Patient Coordinate System if 
                  contour data exists for any given slice, e.g.:
                  [[x0, y0, z0], [x1, y1, z1], ...], 
                  i.e. a list of lists of lists), or [] if not.
                
  'PointICS'    - Same as 'PointPCS' but with points in the Image Coordinate
                  System.

              
**********                          
PointData:
**********        

A dictionary containing the keys:
    
  'PointNo'      - List of integers of all points in ContourData.
  
  'InSliceNo'    - List of integers (for original contour points) or floats 
                   (for interpolated contours that correspond to non-imaged
                   planes, e.g. slice interpolated at 2.5 in between slices
                   2 and 3).
                  
  'InContourNo'  - List of integers of the contour number each point belongs to
                   from the input image.
  
  'ContourType'  - List of integers for each DICOM slice; 
                   The integer value denotes whether there is or is not contour
                   data for any given slice, and if there is, whether it is an 
                   original contour, an interpolated contour, or transformed 
                   contour.
                   0 -> No contour points 
                   1 -> Original contour points
                   2 -> Interpolated contour points
                   3 -> Transformed contour points
                  
  'InPointIndex' - List of indeces [x, y, z] for each point in the input image.
                   
                  
  'InPointPCS'   - List of points in the Patient Coordinate System if contour 
                   data exists for any given slice, e.g.:
                   [[x0, y0, z0], [x1, y1, z1], ...], 
                   i.e. a list of lists of lists), or [] if not.
                
  'InPointICS'   - Same as 'InPointPCS' but with points in the Image 
                   Coordinate System.
                   
  'OutPointIndex - Like 'InPointIndex' but for the output/transformed image.
                   
  'OutPointPCS'  - Like 'InPointPCS' but for the output/transformed image.
                
  'OutPointICS' - Same as 'OutPointPCS' but with points in the Image
                  Coordinate System.
           
            
***********
InterpData:
***********
    
A dictionary containing the keys:
    
  'InterpSliceInd'       - A list of the indices of the interpolated slices 
                          (can be floats if interpolating between two 
                          neighbouring slices), e.g.: [13.5, 14.5, ...]
                          
  'BoundingSliceInds'    - A list of a list of the indices of the nearest 
                           slices that surround the plane to be interpolated, 
                           e.g.: [ [13, 14], [14, 15], ...]
                           
  'FixOSIsOrigNode1'     - A list of booleans whose value denotes whether the 
                           point/node in the list FixOSContour1Pts were 
                           original (True) or added (False).
                           
  'FixOSIsOrigNode2'     - Like FixOSIsOrigNode1 but for FixOSContour2Pts.
  
  'FixOSContour1Inds'    - A list of a list of [x, y, z] indices for each point
                           in FixOSContour1Pts.
                           
  'FixOSContour2Inds'    - Like FixOSContour1Inds but for FixOSContour2Pts.
  
  'FixInterpContourInds' - Like FixOSContour1Inds but for FixInterpContourPts.
  
  'FixOSContour1Pts'     - A list of a list of [x, y, z] coordinates for each
                           point in the over-sampled Contour1 for the Fixed 
                           image.
                           
  'FixOSContour2Pts'     - Like FixOSContour2Pts but for Contour2.
  
  'FixInterpContourPts'  - Like FixOSContour2Pts but for the contour 
                           interpolated from FixOSContour1Pts and 
                           FixOSContour2Pts. 
                           
  'MovOSContour1Inds'    - Like FixOSContour1Inds but for MovOSContour1Pts.
  
  'MovOSContour2Inds'    - Like FixOSContour1Inds but for MovOSContour2Pts.
  
  'MovInterpContourInds' - Like FixOSContour1Inds but for MovInterpContourPts.
  
  'MovOSContour1Pts'     - A list of a list of [x, y, z] coordinates for each
                           point in FixOSContour1Pts transformed to the Moving
                           image domain.
                           
  'MovOSContour2Pts'     - Like MovOSContour1Pts but for the transformation of
                           FixOSContour2Pts.
                           
  'MovInterpContourPts'  - Like MovOSContour1Pts but for the transformation of
                           FixInterpContourPts.
                           


Note:
*****
    PointData is a flat dictionary, that contains contour data on a 
    point-by-point basis.
    
    InContourData is a multi-list dictionary, that contains contour data 
    arranged on a slice-by-slice and contour-by-contour basis for all slices
    within the input DICOM image (including slices that do not contain any
    contour data).
    
    Many of the functions below were adapted from a JavaScript conversion of
    Matt Orton's Matlab code:
    
    https://bitbucket.org/icrimaginginformatics/ohif-viewer-xnat/src/master/Packages/icr-peppermint-tools/client/lib/util/freehandInterpolate/
    
    
    
    
    
    
    
    
List of main functions:
    
    GetIndsOfSlicesWithContours (line 266)
    
    GetBoundingSliceInds (line 321)
    
    CloseContour (line 490)
    
    ReverseIfAntiClockwise (line 513)
    
    GetCumulativePerimeters (line 565)
    
    NormaliseCumulativePerimeters (line 606)
    
    GetNormCumulativeSuperSampledPerimeters (line 630)
    
    GetIsOrigNode (line 689)
    
    GetNodesToAddPerSegment (line 728)
    
    SuperSampleContour (line 813)
    
    IntegrateLineLengths (line 910)
    
    FindIndForMinCumLength (line 954)
    
    ShiftContourPoints (line 1013)
    
    ReduceNodesOfContours (line 1046)
    
    InterpolateBetweenContours (line 1112)
    
    InterpolateContours (line 1227)
    
    TransformInterpolatedContours (line 1442)
    
    GetLinePlaneIntersection (line 1584)
    
    GetIntersectingContoursInMovingPlanes (line 1654)
    
    ClockwiseAngleAndDistance (line 1863)
    
    GetCentroid (line 1925)
    
    SortPointsClockwise (line 1959)
    
    Point0IsClockwiseToPoint1 (line 1982)
    
    CopyRois (line 2021)
    
    
    
List of supplementary functions:
    
    ReduceNodesOfContour (line 2368)
    
    GetSegmentLengths (line 2398)
    
    GetIndsOfSliceNumsOfContourType (line 2430)
    
    GetPointsInImagePlanes (line 2443)

    GetGridOfPointsInImagePlanes (line 2503)
    
    ExportContourPtsToCsv (line 2544)
    
    PlotInterpContours2D_OLD (line 2574)
    
    PlotInterpContours2D (line 2657)
    
    PlotInterpolatedContours3D_OLD (line 2820)
    
    axisEqual3D (line 2992)
    
    PlotInterpolatedContours3D (line 3010)
    
    PlotIntersectingPoints2D_OLD (line 3235)
    
    PlotIntersectingPts2D (line 3307)
    
    PlotJoinedPoints2D (line 3435)
    
    PlotPoints (line 3530)
    
    
"""





def GetIndsOfSlicesWithContours(ContourData, ContourType):
    """
    Get the indices of the rows (slices) within FixContourData that contain a 
    single list of contour points (i.e. only one contour per slice).
    
    Inputs:
        ContourData        - Dictionary containing the key 'PointPCS', whose
                             values are a list of contour points [x, y, z] 
                             arranged along rows for each DICOM slice, and 
                             along columns for different contours (i.e. a list 
                             of lists of lists). Slices without contours have 
                             an empty list ([]).
                             
        ContourType        - Integer that denotes what type of contour to 
                             include in the list SlicesWithContours.
                             Acceptable values are:
                                 1  -> Original contours only
                                 2  -> Interpolated contours only
                                 3  -> Interpolated, transformed contours that
                                       intersect the Moving image planes only
                                 -1 -> Any contours
                      
    Returns:
        SlicesWithContours - List of integers of the indices (row numbers) in
                             FixContourData that contains a single list of 
                             contour points.
    """
    
    # Initialise list of indices of the slices that contain contours:
    SlicesWithContours = []
    
    for i in range(len(ContourData['ContourType'])):
        if ContourType == -1 and ContourData['ContourType'][i] > 0:
            SlicesWithContours.append(i)
            
        else:
            if ContourData['ContourType'][i] == ContourType:
                SlicesWithContours.append(i)
        
    
    if SlicesWithContours:
        # Reduce to list of unique indices:
        SlicesWithContours = list(set(SlicesWithContours))
        
    else:
        # Print warning to console if SlicesWithContours = []:
        print(f'No slices in ContourData found with ContourType = {ContourType}')
        
            
    return SlicesWithContours






def GetIndsOfContourDataWithContourType(ContourData, ContourTypeNo):
    """
    Get the indices of the rows (slices) within ContourData whose 
    ContourType corresponds to ContourTypeNo.
    
    Inputs:
        ContourData   - Dictionary containing the key 'FixContourType' and
                        'MovContourType', whose values determine the "type" of
                        contour.
                         
        ContourTypeNo - Integer that denotes what type of contour to 
                        include in the list of indices.  Acceptable values are:
                            1  -> Original contours
                            2  -> Transformed contours
                            3  -> Intersecting points 
                             
                      
    Returns:
        Indices       - List of integers of the indices (row numbers) in
                        FixContourType or MovContourType that contains 
                        ContourTypeNo.
    """
    
    # Determine the relevant key:
    if ContourTypeNo < 2:
        key = 'FixContourType'
    
    else:
        key = 'MovContourType'
    
    
    # Initialise list of indices of the slices that contain contours:
    Indices = []
    
    for i in range(len(ContourData[key])):
        if ContourTypeNo == -1 and ContourData[key][i] > 0:
            Indices.append(i)
            
        else:
            if ContourData[key][i] == ContourTypeNo:
                Indices.append(i)
        
    
    if Indices:
        # Reduce to list of unique indices:
        Indices = list(set(Indices))
        
    else:
        # Print warning to console if Indices = []:
        print(f'No slices in ContourData found with ContourTypeNo = {ContourTypeNo}')
        
            
    return Indices





def GetIndsOfNonEmptyItems(List):
    """
    Get the indices of non-empty items in a list.
    
    Inputs:
        List    - A list of items (e.g. list of integers/floats/lists/etc).
                                       
    Returns:
        Indices - Indices of non-empty items in List.
    """
    
    # Initialise list of indices of the slices that contain contours:
    Indices = []
    
    for i in range(len(List)):
        if List[i]:
            Indices.append(i)
               
    return Indices







def GetBoundingSliceInds(FixContourData, PointData, InterpSliceInd):
    """ 
    Get the slice indices (row numbers) in FixContourData of the nearest slices 
    that bound the slice to be interpolated.
    
    Inputs:
        FixContourData      - Dictionary containing the key 'PointPCS', 
                              whose values are a list of contour points 
                              [x, y, z] arranged along rows for each DICOM 
                              slice, and along columns for different contours 
                              (i.e. a list of lists of lists). 
                              Slices without contours have empty list ([]).
                              
        PointData          - Dictionary containing the key 'InSliceNo' whose
                             values are a list of integers of the indices of
                             the DICOM slices that contain contour data.
                             
        InterpSliceInd     - The slice index within the DICOM image where a 
                             contour is to be interpolated; May be an integer  
                             (i.e. interpolation at an imaging plane) or a  
                             float (i.e. interpolation between imaging planes).
                      
    Returns:
        BoundingSliceInds  - List of integers of the indices (row numbers) in
                             FixContourData that contains a single list of 
                             contour points.
    
        
    Notes:
        
        1. The JavaScript function _getBoundingPair checks if a contour is an 
        interpolated contour, and if so, it is excluded from the list of 
        possible contours to interpolate between (hence the index of an 
        interpolated contour cannot be included in ContourPair). 
        This has not yet been implemented in GetBoundingSliceInds.
        
        2. Like _getBoundingPair, GetBoundingSliceInds will exclude any slices 
        that have multiple contours.  A more robust version will be required to 
        interpolate contours on slices with multiple contours present.
    """
    
    # Get the indices of the slices that contain contours:
    #SlicesWithContours = GetIndsOfSlicesWithContours(ContourData=ContourData)
    SlicesWithContours = list(set(PointData['InSliceNo']))
    
    #print('SlicesWithContours =', SlicesWithContours)
    
    
    # Get extent of region of contours by slice number (equivalent to function 
    # _getExtentOfRegion in generateInterpolationData.js):
    #Extent = [SlicesWithContours[0], SlicesWithContours[-1]]
    Extent = [min(SlicesWithContours), max(SlicesWithContours)]
    
    #print('Extent =', Extent)

    # Initialise BoundingSliceInds:
    BoundingSliceInds = []
    
    # Initialise booleans:
    FoundLowerSlice = False
    FoundUpperSlice = False
    
    # Cannot interpolate a slice whose index is <= Extent[0], or >= Extent[1]:
    if InterpSliceInd <= Extent[0] or InterpSliceInd >= Extent[1]:
        print(f'Cannot interpolate slice number {InterpSliceInd}')
        return []
    
    else:
        #print(f'Looking for the nearest lower slice to {InterpSliceInd}...')
        
        # Iterate backwards from (InterpSliceInd - 1) to SlicesWithContours[0] 
        # to determine the nearest lowest slice index that contains a single 
        # contour:
        if False:
            for i in range(InterpSliceInd - 1, min(SlicesWithContours) - 1, -1):
                #print(f'\nFixContourData['InPointPCS'][{i}] =', FixContourData['InPointPCS'][i])
                #print(f'\nlen(FixContourData['InPointPCS'][{i}]) = {len(FixContourData['InPointPCS'][i])}')
                
                if len(FixContourData['PointPCS'][i]) == 1:
                    #print(f'\nlen(FixContourData['PointPCS'][{i}]) == 1')
                    #print(f'Appending {i} to BoundingSliceInds')
                    
                    BoundingSliceInds.append(i)
                    
                    FoundLowerSlice = True
                    
                    break
            
            
        """ Allow for the possibility of InterpInd to be a fraction (not an
        integer) by taking floor of InterpInd using (InterpInd//1): """
        FloorInterpInd = int(InterpSliceInd//1)
        
        for i in range(FloorInterpInd, min(SlicesWithContours) - 1, -1):
            if len(FixContourData['PointPCS'][i]) == 1:
                # Append i to BoundingSliceInds if i != InterpSliceInd (which 
                # could arise if InterpSliceInd is an integer):
                if i != InterpSliceInd:
                    BoundingSliceInds.append(i)
                    
                    FoundLowerSlice = True
                    
                    break
                
        
        
                
                
        #print(f'Looking for the nearest upper slice to {InterpSliceInd}...')
        
        # Iterate forwards from (InterpSliceInd + 1) to SlicesWithContours[-1] 
        # to determine the nearest upper slice index that contains a single 
        # contour:
        if False:
            for i in range(InterpSliceInd + 1, max(SlicesWithContours) + 1):
                #print(f'\nFixContourData['PointPCS'][{i}] =', FixContourData['PointPCS'][i])
                #print(f'\nlen(FixContourData['PointPCS'][{i}]) = {len(FixContourData['PointPCS'][i])}')
                #print(f'Appending {i} to BoundingSliceInds')
                
                if len(FixContourData['PointPCS'][i]) == 1:
                    #print(f'\nlen(FixContourData['PointPCS'][{i}]) == 1')
                    #print(f'Appending {i} to BoundingSliceInds')
                    
                    BoundingSliceInds.append(i)
                    
                    FoundUpperSlice = True
                    
                    break
                
        """ Allow for the possibility of InterpSliceInd to be a fraction (not 
        an integer) by taking ceiling of InterpSliceInd using 
        # -(-InterpSliceInd//1): """
        CeilInterpInd = int(-(-InterpSliceInd//1))
        
        for i in range(CeilInterpInd, max(SlicesWithContours) + 1):
            if len(FixContourData['PointPCS'][i]) == 1:
                 # Append i to BoundingSliceInds if i != InterpSliceInd (which 
                 # could arise if InterpInd is an integer):
                if i != InterpSliceInd:
                    BoundingSliceInds.append(i)
                    
                    FoundUpperSlice = True
                    
                    break
        
        # Deal with case where no lower, or upper, or both upper nor lower 
        # slice index can be used for interpolation:
        if not (FoundLowerSlice and FoundUpperSlice):
            if not FoundLowerSlice and FoundUpperSlice:
                print('Did not find suitable lower slice to',
                      f'interpolate slice number {InterpSliceInd}.')
                
            if not FoundUpperSlice and FoundLowerSlice:
                print('Did not find suitable upper slice to',
                      f'interpolate slice number {InterpSliceInd}.')
                
            if not FoundLowerSlice and not FoundUpperSlice:
                print('Did not find suitable lower or upper slice',
                      f'to interpolate slice number {InterpSliceInd}.')
            
            return []
        
        else:
            return BoundingSliceInds 
    




def CloseContour(Contour):
    """
    Close an open contour by appending the first point to the end of the list.
    
    Inputs:
        Contour - An open list of contour points.
        
    Returns:
        Contour - A closed list of contour points.
    """
    
    # Import packages:
    #import copy
    
    #Contour = copy.deepcopy(Points)
    
    # Append the first point to create a closed contour:
    #Contour.append(Points[0])
    Contour.append(Contour[0])
    
    return Contour


def ReverseIfAntiClockwise(Contour):
    """
    Ensures that a contour's points are arranged in a clockwise order.
    
    Inputs:
        Contour - A list of contour points.
        
    Returns:
        Contour - A list of contour points whose points have been reversed if
                  they were counter-clockwise, or the original list if not.
    """
    
    
    P = len(Contour)
    
    # Get mean x position of all points:
    #MeanX = sum([Contour[i][0] for i in range(P)]) / P # correct but might not
    # be clear outside Python
    
    MeanX = 0
    
    for i in range(P):
        MeanX += Contour[i][0] / P
        
    
    # Check the direction of the points:
    CheckSum = 0
    j = 1
    k = 2
    
    for i in range(P):
        CheckSum += (Contour[j][0] - MeanX) * (Contour[k][1] - Contour[i][1])
        
        j += 1
        k += 1
        
        if j >= P:
            j = 0
        if k >= P:
            k = 0
            
            
    if CheckSum > 0:
        Contour.reverse()
        
        print('Contour was reversed.')
        
    return Contour
            

""" Generate list of cumulative perimeters of a contour at each node """

def GetCumulativePerimeters(Contour):
    """
    Generate a list of cumulative "perimeters" of a contour.
    
    Inputs:
        Contour  - A list of contour points.
        
    Returns:
        CumPerim - A list of cumulative "perimeters" of the contour.
    """
    
    #print(f'len(Contour) = {len(Contour)}')
    
    # Initialise the cumulative perimeter and list of cumulative perimeters:
    CumP = 0
    CumPerim = [0]
    
    # Loop through each point:
    for i in range(1, len(Contour)):
        # The segment length between every two points:
        SegmentL = (\
                   (Contour[i-1][0] - Contour[i][0])**2 + \
                   (Contour[i-1][1] - Contour[i][1])**2 + \
                   (Contour[i-1][2] - Contour[i][2])**2 \
                   )**(1/2)
        
        # Save time by omitting the sqrt:
        #SegmentL = (Contour[i-1][0] - Contour[i][0])**2 + \
        #           (Contour[i-1][1] - Contour[i][1])**2 + \
        #           (Contour[i-1][2] - Contour[i][2])**2
        
        CumP = CumP + SegmentL
              
        CumPerim.append(CumP + SegmentL)
        
    return CumPerim





def NormaliseCumulativePerimeters(CumPerimeters): 
    """
    Normalised list of cumulative contour "perimeters".
    
    Inputs:
        CumPerimeters - List of cumulative contour "perimeters".
    
    Returns:
        CumPerimNorm  - List of normalised cumulative contour "perimeters".
    """
    
    # List comprehension is compact but not reader-friendly outside Python:
    #return [CumPerimeters[i]/CumPerimeters[-1] for i in range(len(CumPerimeters))]
    
    # Initialise the list:
    CumPerimNorm = []
    
    for i in range(len(CumPerimeters)):
        CumPerimNorm.append(CumPerimeters[i]/CumPerimeters[-1])
        
    return CumPerimNorm



def GetNormCumulativeSuperSampledPerimeters(CumPerimetersNorm, NumNodesToAdd):
    """ 
    Super-sample a list of normalised cumulative "perimeters".
    
    Inputs:
        CumPerimetersNorm - List of normalised cumulative contour "perimeters".
        
        NumNodesToAdd     - List of integers whose values are the number of 
                            nodes to be added within each segment along the
                            list of normalised cumulative contour perimeters.
        
    Returns:
        CumSSPerimNorm    - List of super-sampled normalised cumulative contour
                            perimeters.    
    
    Notes: 
        
        1. The first (NumNodesToAdd - 2) items in CumSSPerimNorm are the 
        cumulative contour perimeters that ensure that a minimum desired inter-
        node spacing is satisfied.  The -2 is due to skipping of the 0 and 1
        since they are already covered by the first and final items in the 
        input list CumPerimetersNorm.
        
        The next len(CumPerimetersNorm) items in CumSSPerimNorm are the items
        in the input list CumPerimetersNorm (concatenated to the end of the 
        list CumSSPerimNorm following the initial step described above).
        
        2. This function is called _getInterpolatedPerim in the JavaScript code. 
    """
    
    # The inter-node spacing is:
    dP = 1 / (NumNodesToAdd - 1)
    
    """ Exclude the first (0) and last item (1) normalised cumulative perimeter
    since they are already covered by the original normalised cumulative 
    perimeters (i.e. iterate from 1 to NumNodesToAdd - 1)
    """
    # Initialise the normalised cumulative super-sampled perimeters:
    CumSSPerimNorm = [dP]
    
    # First append the cumulative perimeters for the nodes that ensure the
    # minimum inter-node spacing required:
    #for i in range(1, NumNodesToAdd - 1):
    """ 
    Not sure why the upper limit needs to be (NumNodesToAdd - 2) instead of
    (NumNodesToAdd - 1), since the lower limit of 1 (rather than 0) already
    accounts for one, and the -1 accounts for the other. The JavaScript code 
    also has -2 so it's probably correct.
    """
    for i in range(1, NumNodesToAdd - 2):
        CumSSPerimNorm.append(CumSSPerimNorm[-1] + dP)
        
    # Next concatenate the normalised cumulative perimeters:
    CumSSPerimNorm += CumPerimetersNorm
    
    return CumSSPerimNorm
    


def GetIsOrigNode(Contour, NumNodesToAdd):
    """
    Generate an array of booleans that indicate whether the nodes are original
    or interpolated (i.e. super-sampled).
    
    Inputs:
        Contour       - A list of contour points.
        
        NumNodesToAdd - List of integers whose values are the number of 
                        nodes to be added within each segment along the list
                        of normalised cumulative contour perimeters.
                        
    Returns:
        IsOrigNode    - List of booleans whose values denote whether the 
                        corresponding contour point is an original node (True)
                        or an added node (False).
    
    
    Note:
        
        This is called _getIndicatorArray in the JavaScript code.
    """
    
    IsOrigNode = []
    
    # The first NumNodesToAdd - 2 nodes were additional nodes added to achieve 
    # the required minimum inter-node spacing:
    for i in range(NumNodesToAdd - 2):
        IsOrigNode.append(False)
        
    # The next len(Contour) nodes are original nodes from Contour:
    for i in range(len(Contour)):
        IsOrigNode.append(True)
        
        
    return IsOrigNode
    
    

def GetNodesToAddPerSegment(CumSSPerimNorm, IsOrigNode):
    """
    Generate list of the number of nodes to be added for each segment of a
    contour.
    
    Inputs:
        CumSSPerimNorm       - List of super-sampled normalised cumulative 
                               contour perimeters.
        
        IsOrigNode           - List of booleans whose values denote whether the 
                               corresponding contour point is an original node
                               (True) or an added node (False).
        
    Returns:
        Inds                 - List of indices that sort CumSSPerimNorm in
                               ascending order.
                               
        IsOrigNodeSorted     - List of IsOrigNode sorted by Inds.
        
        IndsOrigNodes        - List of indices of original nodes in 
                               CumSSPerimNorm sorted by Inds.
                               
        NodesToAddPerSegment - A list of the integer number of nodes to be
                               added to each original node/point.
    """
    
    # Get the indices that sort the normalised cumulative super-sampled 
    # perimeters:
    Inds = [i[0] for i in sorted(enumerate(CumSSPerimNorm), key=lambda x:x[1])]
    
    # Order the boolean list:
    IsOrigNodeSorted = []
    
    for ind in Inds:
        IsOrigNodeSorted.append(IsOrigNode[ind])
    
    # Get ordered indices of original nodes:
    """
    Seems this isn't needed (I've likely misunderstood the JavaScript code).
    """
    #OrigIndsSorted = []
    #
    #for i in range(len(Inds)):
    #    if IsOrigNodeSorted[i]:
    #        OrigIndsSorted.append(Inds[i])
            
    # Get the indicies of the original nodes in IsOrigNodeSorted:
    IndsOrigNodes = []
    
    for i in range(len(IsOrigNodeSorted)):
        if IsOrigNodeSorted[i]:
            IndsOrigNodes.append(i)
        

    # Order the normalised cumulative super-sampled perimeters:
    """ This is not in the JavaScript code """
    #CumSSPerimNormSorted = [CumSSPerimNorm[i] for i in Inds]

    # Get the list of normailsed cumulative super-sampled perimeters for the
    # original nodes:
    """ This is not in the JavaScript code """
    #CumSSPerimNormSortedOrig = [CumSSPerimNormSorted[i] for i in OrigIndsSorted]

    # The segment lengths are:
    """ This is not in the JavaScript code """
    #SegmentL = [CumSSPerimNormSortedOrig[i+1] - CumSSPerimNormSortedOrig[i] for i in range(len(CumSSPerimNormSortedOrig) - 1)]
    
    # Initialise the list of the number of nodes to add to each segment:
    NodesToAddPerSegment = []
    
    #for i in range(len(OrigIndsSorted) - 1):
        #NodesToAddPerSegment.append(OrigIndsSorted[i + 1] - OrigIndsSorted[i])
        
    for i in range(len(IndsOrigNodes) - 1):
        NodesToAddPerSegment.append(IndsOrigNodes[i + 1] - IndsOrigNodes[i])
    
        
    #return NodesToAddPerSegment
    #return Inds, IsOrigNodeSorted, OrigIndsSorted, NodesToAddPerSegment
    return Inds, IsOrigNodeSorted, IndsOrigNodes, NodesToAddPerSegment



    
    
def SuperSampleContour(Contour, NodesToAddPerSegment):
    """
    Super-sample a contour.
    
    Inputs:
        Contour              - A list of contours points.
        
        NodesToAddPerSegment - A list of the integer number of nodes to be 
                               added to each original node/point in Contour.
        
    Returns:
        SSContour            - A list of super-sampled (with added nodes) 
                               contour points.
        
        SSIsOrigNode         - A list of booleans whose values denote whether  
                               the corresponding contour point in SSContour is 
                               an original node (True) or an added node (False).
    """
    
    # Initialise list of super-sampled contour points and the list of booleans 
    # that indicate if the point/node in the super-sampled list is original 
    # (False if the node was interpolated):
    SSContour = []
    SSIsOrigNode = []
    
    #print(f'len(Contour)         = {len(Contour)}')
    #print(f'len(NodesToAddPerSegment) = {len(NodesToAddPerSegment)}')
    
    # Iterate through each contour point without returning to the 0th point 
    # (which is the final node in the list), i.e. the super-sampled contour 
    # will not be closed:
    for i in range(len(Contour) - 1):
        #print(i)
        
        # Add the original node:
        SSContour.append(Contour[i])
        SSIsOrigNode.append(True)
        
        # Add the linearly interpolated nodes.  Get the spacings along x and y
        # for this segment:
        dx = (Contour[i + 1][0] - Contour[i][0]) / (NodesToAddPerSegment[i] + 1)
        dy = (Contour[i + 1][1] - Contour[i][1]) / (NodesToAddPerSegment[i] + 1)
        
        # Add dx and dy to the x and y components of the last item in SSContour
        # (keep the z component unchanged):
        """
        Not sure why j is iterated to NodesToAddPerSegment[i] - 1, instead of
        NodesToAddPerSegment[i] so deviating from the JavaScript code:
        """
        for j in range(NodesToAddPerSegment[i] - 1):
        #for j in range(NodesToAddPerSegment[i]):
            SSContour.append([
                              SSContour[-1][0] + dx, 
                              SSContour[-1][1] + dy, 
                              SSContour[-1][2]
                              ])
            SSIsOrigNode.append(False)
            
    return SSContour, SSIsOrigNode





#def IntegrateLineLengths(Contour1, Contour2, StartInd2):
#    
#    # Initialise the cummulative line lengths:
#    LineLength = 0
#    
#    for i in range(len(Contour1)):
#        Point1 = Contour1[i]
#        
#        for j in range(len(Contour2)):
#            # The index of the point for Contour2 starts
#            # at StartInd2 and increments to N, then is 
#            # "wrapped" back to 0 and so on until N 
#            # iterations:
#            if StartInd2 + j < len(Contour2):
#                Ind2 = StartInd2 + j
#            else:
#                Ind2 = len(Contour2) - (StartInd2 + j)
#                
#            Point2 = Contour2[Ind2]
#            
#            # The vector length between Point1 and Point2:
#            VectorL = ((Point1[0] - Point2[0])**2 \
#                       + (Point1[1] - Point2[1])**2 \
#                       + (Point1[2] - Point2[2])**2)**(1/2)
#            
#            # Add the line length between Point1 and Point2:
#            LineLength = LineLength + VectorL
#            
#            
#    return LineLength



def IntegrateLineLengths(Contour1, Contour2):
    """ 
    Integrate the line lengths that connect every point in Contour1 with the
    corresponding point in Contour2.  
    
    Inputs:
        Contour1   - A list of contour points.
        
        Contour2   - A list of contour points.
        
    Returns:
        LineLength - The sum of all line lengths that join the points in 
                     Contour1 and Contour2.
                     
    Note: 
        Contour1 and Contour2 must have equal lengths. 
        
    """
    
    # Initialise the cummulative line lengths:
    LineLength = 0
    
    for i in range(len(Contour1)):
            # The vector length between Point1 and Point2:
            VectorL = (
                       (Contour1[i][0] - Contour2[i][0])**2 + \
                       (Contour1[i][1] - Contour2[i][1])**2 + \
                       (Contour1[i][2] - Contour2[i][2])**2 \
                       )**(1/2)
            
            # Omit sqrt to save time:
            #VectorL = (Contour1[i][0] - Contour2[i][0])**2 + \
            #          (Contour1[i][1] - Contour2[i][1])**2 + \
            #          (Contour1[i][2] - Contour2[i][2])**2
            
            LineLength += VectorL
            
            
    return LineLength





def FindIndForMinCumLength(Contour1, Contour2):
    """ 
    Determine the index for Contour2 that would minimise the integrated line
    lengths obtained by joining the points in Contour1 to the corresponding 
    points in Contour2 with the index shift applied to Contour2.
    
    Inputs:
        Contour1 - A list of contour points.
        
        Contour2 - A list of contour points.
        
    Returns:
        Shift    - The starting index for Contour2 that minimises the 
                   integrated line lengths.
    
    
    Note:
        The Shift index is determined by looping through each of N possible
        combinations of Shift index (for N points in Contour2) and applying the 
        function IntegrateLineLengths() with those shifts. The starting index 
        that yields the minimum cumulative line length is equivalent to 
        minimising the surface area (i.e. catenoid) that would be formed by 
        joining each i^th point in Contour1 to each (i + Shift)^th point in 
        Contour 2.

        https://en.wikipedia.org/wiki/Minimal_surface_of_revolution

    """
    
    # Create list to store N cumulative line lengths for all N combinations of 
    # starting index for Contour2:
    LineLengths = []

    # Loop through all N possible starting indeces for Contour2:
    for i in range(len(Contour2)):
        #CumLineLengths.append(IntegrateLineLengths(Contour1=Contour1, 
        #                                           Contour2=Contour2, 
        #                                           StartInd2=i))
        
        # Apply shift to Contour2:
        Contour2Shifted = ShiftContourPoints(Contour=Contour2, Shift=i)
        
        # Get the cumumlative line length for this shift:
        LineLength = IntegrateLineLengths(Contour1=Contour1, 
                                          Contour2=Contour2Shifted)
        
        LineLengths.append(LineLength)

    
    # The index that yields the minimum cumulative line length:
    Shift = LineLengths.index(min(LineLengths))
    
    return Shift






def ShiftContourPoints(Contour, Shift):
    """
    Generate a new list of contour points by shifting the points in the 
    original list of contour points by an integer number.
    
    Inputs:
        Contour        - A list of contour points.
        
        Shift          - A integer value.
        
    Returns:
        ShiftedContour - A list of the contour points in Contour shifted by
                         Shift integer positions.
    """
    
    # Initialise the shifted contour:
    ShiftedContour = []
    
    for i in range(len(Contour)):
        j = i + Shift
        # Wrap j if (i + Shift) >= len(Contour):
        if i + Shift >= len(Contour):
            j = j - (len(Contour) - 1) 

        ShiftedContour.append(Contour[j])
        
    return ShiftedContour






def ReduceNodesOfContours(SuperSampledContour1, SuperSampledContour2, 
                          SuperSampledIsOrigNode1, SuperSampledIsOrigNode2):
    """
    Reduce the number of nodes in a list of super-sampled contour points to a
    "over-sampled" number of nodes.
    
    Inputs:
        SuperSampledContour1    - A list of super-sampled contour points.
        
        SuperSampledContour2    - A list of super-sampled contour points.
        
        SuperSampledIsOrigNode1 - A list of booleans whose values denote   
                                  whether the corresponding contour point in 
                                  SuperSampledContour1 is an original node 
                                  (True) or an added node (False).
        
        SuperSampledIsOrigNode2 - A list of booleans whose values denote   
                                  whether the corresponding contour point in 
                                  SuperSampledContour2 is an original node 
                                  (True) or an added node (False).
        
    Returns:
        OverSampledContour1     - A list of over-sampled contour points after 
                                  removing of any node in SuperSampledContour1
                                  if both that node and the corresponding node
                                  in SuperSampledContour2 was added (i.e. not
                                  original).
        
        OverSampledContour2     - A list of over-sampled contour points after 
                                  removing of any node in SuperSampledContour2
                                  if both that node and the corresponding node
                                  in SuperSampledContour1 was added (i.e. not
                                  original).
        
        OverSampledIsOrigNode1  - A list of booleans whose values denote   
                                  whether the corresponding contour point in 
                                  OverSampledContour1 is an original node 
                                  (True) or an added node (False).
        
        OverSampledIsOrigNode2  - A list of booleans whose values denote   
                                  whether the corresponding contour point in 
                                  OverSampledContour2 is an original node 
                                  (True) or an added node (False).
    """
    
    # Initialise the list of points in the over-sampled contours with some
    # nodes removed, and the corresponding IsOrigNode lists:
    OverSampledContour1 = []
    OverSampledContour2 = []
    OverSampledIsOrigNode1 = []
    OverSampledIsOrigNode2 = []
    
    for i in range(len(SuperSampledContour1)):
        if SuperSampledIsOrigNode1[i] or SuperSampledIsOrigNode2[i]:
            OverSampledContour1.append(SuperSampledContour1[i])
            OverSampledContour2.append(SuperSampledContour2[i])
            
            OverSampledIsOrigNode1.append(SuperSampledIsOrigNode1[i])
            OverSampledIsOrigNode2.append(SuperSampledIsOrigNode2[i])
            
    return OverSampledContour1, OverSampledContour2, \
           OverSampledIsOrigNode1, OverSampledIsOrigNode2
           
           


def InterpolateBetweenContours(Contour1, Contour2, IsOrigNode1, IsOrigNode2,
                               FracInterpSliceInd, Contour1HasMorePts,
                               InterpolateAllPts):
    """ 
    Generate a list of intepolated contour points between two contours.
    
    Inputs:
        Contour1            - A list of contour points.
        
        Contour2            - A list of contour points.
        
        IsOrigNode1         - A list of booleans whose values denote whether
                              the corresponding contour point in Contour1 is an 
                              original node (True) or an added node (False).
                              
        IsOrigNode2         - A list of booleans whose values denote whether 
                              the corresponding contour point in Contour1 is an 
                              original node (True) or an added node (False).
                              
        FracInterpSliceInd  - A integer or float that denotes the fractional 
                              distance of the interpolated contour's plane 
                              within the region bounded by the planes for 
                              Contour1 and Contour2.
                             
        Contour1HasMorePts  - A boolean that denotes whether or not Contour1
                              has more points than Contour2.
                              
        InterpolateAllPts   - A boolean that determines whether or not 
                              interpolation will be performed only between a
                              pair of contour points for which the corresponding
                              node in the longer of the original contours was
                              an original node.  See Note 4.
    
    Returns:
        InterpolatedContour - A list of interpolated contour points.
    
    Notes:
        1. Contour1 and Contour2 would normally be over-sampled contours (i.e. 
        not the original lists of contours).
        
        2. Contour1 and Contour2 must have equal lengths. 
        
        3. The fraction FracInterpSliceInd would be 0 if the interpolated 
        contour were to coincide with the plane containing Contour1, and 1 if 
        it were to coincide with the plane containing Contour2.
        
        4. In the JavaScript code the interpolation is performed between the 
        pair of contour points only if the corresponding contour point in the 
        longer list of contour points was an original node. This results in an 
        interpolated contour with the same number of points in it as the number
        of True values in the longer of IsOrigNode1 and IsOrigNode2, and hence,
        the length of interpolated contour points is shorter than the length of
        Contour1 or Contour2.
        
        In this function I've allowed for either using the truncation used in
        the JavaScript code (InterpolateAllPts = False) or to interpolate all 
        pairs of points, so that the length of Contour1, Contour2 and 
        InterpolatedContour are equal (InterpolateAllPts = True).
    """
    
    N1 = len(Contour1)
    N2 = len(Contour2)
    
    if not N1 == N2:
        print(f'Contour1 (N = {N1}) and Contour2 (N = {N2}) do not have',
              'equal lengths.')
        
        return
    
    # Initialise the interpolated contour:
    InterpolatedContour = []
    
    # If the original Contour1 has more points than the original Contour2..
    if Contour1HasMorePts:
        IsOrigNode = IsOrigNode1
    else:
        IsOrigNode = IsOrigNode2
        
    for i in range(len(Contour1)):
        if InterpolateAllPts:
            # Interpolate all points:
            InterpX = (1 - FracInterpSliceInd) * Contour1[i][0] \
                       + FracInterpSliceInd * Contour2[i][0]
                
            InterpY = (1 - FracInterpSliceInd) * Contour1[i][1] \
                      + FracInterpSliceInd * Contour2[i][1]
                      
            InterpZ = (1 - FracInterpSliceInd) * Contour1[i][2] \
                      + FracInterpSliceInd * Contour2[i][2]
        
            InterpolatedContour.append([InterpX, InterpY, InterpZ])
            
            
        else:
            # Only interpolate between points for which IsOrigNode is True:
            if IsOrigNode[i]:
                InterpX = (1 - FracInterpSliceInd) * Contour1[i][0] \
                          + FracInterpSliceInd * Contour2[i][0]
                
                InterpY = (1 - FracInterpSliceInd) * Contour1[i][1] \
                          + FracInterpSliceInd * Contour2[i][1]
                          
                InterpZ = (1 - FracInterpSliceInd) * Contour1[i][2] \
                          + FracInterpSliceInd * Contour2[i][2]
                          
                InterpolatedContour.append([InterpX, InterpY, InterpZ])
            
            
    return InterpolatedContour






def InterpolateContours(FixContourData, PointData, InterpSliceInd, dP, 
                        InterpolateAllPts):
    """
    Main function for contour interpolation.
    
    Inputs:
        FixContourData    - Dictionary containing a list of contour points 
                            [x, y, z] arranged along rows for each DICOM slice, 
                            and along columns for different contours (i.e. a 
                            list of lists of lists). Slices without contours 
                            have empty list ([]).
                              
        PointData         - Dictionary containing the key 'InSliceNo' whose 
                            values are a list of integers of the indices of the
                            DICOM slices that contain contour data.
                             
        InterpSliceInd    - The index within the DICOM image where a contour is
                            to be interpolated; May be an integer (i.e. 
                            interpolation at an imaging plane) or a float (i.e.  
                            interpolation between imaging planes).
                             
        dP                - A float denoting the desired inter-node spacing to 
                            use when super-sampling the contours.
                         
        InterpolateAllPts - A boolean that determines whether or not 
                            interpolation will be performed only between a pair
                            of contour points for which the corresponding node
                            in the longer of the original contours was an
                            original node.  See Note 4 in the function 
                            InterpolateBetweenContours.
        
    Returns:
        InterpContour     - A list of interpolated contour points.
     
    """
    
    import copy
    
    # Get bounding slice indices:
    BoundingSliceInds = GetBoundingSliceInds(FixContourData=FixContourData,
                                             PointData=PointData,
                                             InterpSliceInd=InterpSliceInd)
    
    
    # Escape if None was returned for BoundingSliceInds (i.e. if two slice 
    # indices were not found):
    if not BoundingSliceInds:
        return
    
    print(f'Interpolating between slice {BoundingSliceInds[0]} and',
          f'{BoundingSliceInds[1]} for slice at {InterpSliceInd}')
    
    # Define the contours:
    """
    Note: 
    
    Need to add [0] to the end of FixContourData['PointPCS'][BoundingSliceInds[0]] 
    since the contour points are a list within the list for each slice.
    """
    Contour1 = copy.deepcopy(FixContourData['PointPCS'][BoundingSliceInds[0]][0])
    Contour2 = copy.deepcopy(FixContourData['PointPCS'][BoundingSliceInds[1]][0])
    
    # Close the contours:
    Contour1.append(Contour1[0])
    Contour2.append(Contour2[0])
    
    # Get the segment lengths (surplus to interpolation algorithm):
    #SegmentLengths1 = GetSegmentLengths(Contour1)
    #SegmentLengths2 = GetSegmentLengths(Contour2)
    
    # Ensure that the points in both contours run clockwise:
    Contour1 = ReverseIfAntiClockwise(Contour=Contour1)
    Contour2 = ReverseIfAntiClockwise(Contour=Contour2)
    
    # Get the cumulative perimeters of the two bounding contours:
    CumPerim1 = GetCumulativePerimeters(Contour=Contour1)
    CumPerim2 = GetCumulativePerimeters(Contour=Contour2)
    
    # Normalise the cumulative perimeters:
    CumPerim1Norm = NormaliseCumulativePerimeters(CumPerimeters=CumPerim1)
    CumPerim2Norm = NormaliseCumulativePerimeters(CumPerimeters=CumPerim2)
    
    # The number of nodes required for Contour1 and Contour2 to achieve the 
    # minimum inter-node spacing of dP:
    """ 
    Note:
        a//b yields floor(a/b)
        
        - (-a//b) yields ceil(a/b)
    """
    MinNumNodes1 = round(- (- CumPerim1[-1] // dP))
    MinNumNodes2 = round(- (- CumPerim2[-1] // dP))
    
    # The minimum number of nodes that will need to be added:
    MinNumNodes = max(MinNumNodes1, MinNumNodes2)
    
    # The number of nodes that will have to be added to Contour1 and Contour2 
    # are MinNumNodes plus the number of original nodes in Contour2 and Contour1
    # respectively (i.e. the nodes not common to either)?:
    NumNodesToAdd1 = MinNumNodes + len(Contour2)
    NumNodesToAdd2 = MinNumNodes + len(Contour1)
    
    # Get the cumulative super-sampled perimeters:
    CumSSPerim1 = GetNormCumulativeSuperSampledPerimeters(CumPerimetersNorm=CumPerim1Norm,
                                                          NumNodesToAdd=NumNodesToAdd1)
    CumSSPerim2 = GetNormCumulativeSuperSampledPerimeters(CumPerimetersNorm=CumPerim2Norm,
                                                          NumNodesToAdd=NumNodesToAdd2)
    
    # Get list of booleans for original (True) and added (False) nodes:
    IsOrigNode1 = GetIsOrigNode(Contour=Contour1, NumNodesToAdd=NumNodesToAdd1)
    IsOrigNode2 = GetIsOrigNode(Contour=Contour2, NumNodesToAdd=NumNodesToAdd2)
    
    # Get the nodes per segment:
    Inds1,\
    IsOrigNodeSorted1,\
    IndsOrigNodes1,\
    NodesToAddPerSegment1 = GetNodesToAddPerSegment(CumSSPerimNorm=CumSSPerim1, 
                                                    IsOrigNode=IsOrigNode1)
    
    Inds2,\
    IsOrigNodeSorted2,\
    IndsOrigNodes2,\
    NodesToAddPerSegment2 = GetNodesToAddPerSegment(CumSSPerimNorm=CumSSPerim2, 
                                                    IsOrigNode=IsOrigNode2)
    
    # Super-sample the contours:
    SSContour1,\
    SSIsOrigNode1 = SuperSampleContour(Contour=Contour1, 
                                       NodesToAddPerSegment=NodesToAddPerSegment1)
    
    SSContour2,\
    SSIsOrigNode2 = SuperSampleContour(Contour=Contour2, 
                                       NodesToAddPerSegment=NodesToAddPerSegment2)
    
    # Find the starting index for SSContour2 that minimises the integrated line 
    # lengths (i.e. minimal area of the surfaces created by linking points in 
    # SSContour1 and SSContour2 N different ways for all N points in 
    # SSContour2):
    IndMinCumL = FindIndForMinCumLength(Contour1=SSContour1, Contour2=SSContour2)
    
    # Shift the points in SSContour2 (and also SSIsOrigNode2):
    SSContour2Shifted = ShiftContourPoints(Contour=SSContour2, Shift=IndMinCumL)
    SSIsOrigNode2Shifted = ShiftContourPoints(Contour=SSIsOrigNode2, Shift=IndMinCumL)
    
    # Remove added nodes uncommon to both original contours:
    OSContour1,\
    OSContour2,\
    OSIsOrigNode1,\
    OSIsOrigNode2 = ReduceNodesOfContours(SuperSampledContour1=SSContour1,
                                          SuperSampledContour2=SSContour2Shifted,
                                          SuperSampledIsOrigNode1=SSIsOrigNode1, 
                                          SuperSampledIsOrigNode2=SSIsOrigNode2Shifted)
    
    # Define Contour1HasMorePts:
    if len(Contour1) > len(Contour2):
        Contour1HasMorePts = True
    else:
        Contour1HasMorePts = False
    
    
    """ 
    Note:  What if len(Contour1) = len(Contour2)?...
    """
    
    # Define the fractional interpolated slice number:
    FracInterpInd = (InterpSliceInd - BoundingSliceInds[0]) / (BoundingSliceInds[1] - BoundingSliceInds[0])
    
    # Linearly interpolate between the two over-sampled contours:
    InterpContour = InterpolateBetweenContours(Contour1=OSContour1,
                                               Contour2=OSContour2,
                                               IsOrigNode1=OSIsOrigNode1,
                                               IsOrigNode2=OSIsOrigNode2,
                                               FracInterpSliceInd=FracInterpInd,
                                               Contour1HasMorePts=Contour1HasMorePts,
                                               InterpolateAllPts=InterpolateAllPts)
    
    
    
    #return InterpContour
    return BoundingSliceInds, OSContour1, OSIsOrigNode1,\
           OSContour2, OSIsOrigNode2, InterpContour


    
    """ Deviate from the JavaScript code - try interpolating using the 
    super-sampled contours (i.e. before reducing the num of nodes): """
    if False:
        InterpSSContour = InterpolateBetweenContours(Contour1=SSContour1,
                                                     Contour2=SSContour2,
                                                     IsOrigNode1=SSIsOrigNode1,
                                                     IsOrigNode2=SSIsOrigNode2,
                                                     FracInterpSliceInd=FracInterpInd,
                                                     Contour1HasMorePts=Contour1HasMorePts)
        
        # Define boolean list of indices to keep in the super-sampled 
        # interpolated contour:
        IsOrigNode1or2 = IsOrigNode1 or IsOrigNode2
        
        # Reduce the number of nodes of InterpSSContour:
        ReducedInterpSSContour = ReduceNodesOfContour(Contour=InterpSSContour, 
                                                      IndsToKeep=IsOrigNode1or2)
        
        return InterpContour, InterpSSContour, ReducedInterpSSContour
    



#def ResampleAllFixedContours(ContourData, dP, FixedDicomDir):
def ResampleAllFixedContours(ContourData, dP):
    """
    Resample all contours belonging to the Fixed image domain.
    
    Inputs:
        ContourData - Dictionary containing a list of contour points [x, y, z]
                      arranged along rows for each DICOM slice, and along 
                      columns for different contours (i.e. a list of lists of 
                      lists). Slices without contours have empty list ([]).
        
        dP          - A float denoting the desired inter-node spacing to use
                      when super-sampling the contours.
        
        
    Returns:
        ContourData - Dictionary with resampled contours added.
    
    """
    # Import packages and functions:
    import copy
    #from GetImageAttributes import GetImageAttributes
    #import importlib
    #import PCStoICS
    #importlib.reload(PCStoICS)
    #from PCStoICS import PCStoICS
    
    # Get the indices of the slices that contain contours in the Fixed image:
    Cinds = GetIndsOfContourDataWithContourType(ContourData=ContourData, 
                                                ContourTypeNo=1)
    
    # The number of contours:
    C = len(Cinds)
    
    #print('Contours exist on slices', Cinds, '\n')
    
    # Initialise lists:
    Contours = []
    NumContourPts = []
    #CumPerims = []
    NormCumPerims = []
    MinNumNodes = []
        
    # Loop through all Inds:
    for i in Cinds:
        """ 
        Note:
            The list of contours needs to be addressed with [0] since there is
            at most one contour per slice.
            
            The algorithm may need to be generalised should it need to deal 
            with cases where there is more than one contour per slice.
        """
        Contour = ContourData['FixPtsPCS'][i][0]
        
        #print(f'\n\ni = {i}\nContour =', Contour)
        
        #print(f'There are {len(Contour)} points in the contour on slice {i}.')
        
        # Close the contour:
        Contour.append(Contour[0])
        
        # Ensure that the points run clockwise:
        Contour = ReverseIfAntiClockwise(Contour=Contour)
        
        Contours.append(Contour)
        
        NumContourPts.append(len(Contour))
    
        # Get the cumulative perimeters:
        CumPerims = GetCumulativePerimeters(Contour=Contour)
        
        # Normalise the cumulative perimeters:
        NormCumPerims.append(NormaliseCumulativePerimeters(CumPerimeters=CumPerims))
        
        # The number of nodes required to achieve the minimum inter-node 
        # spacing of dP:
        """ 
        Note:
            a//b yields floor(a/b)
            
            - (-a//b) yields ceil(a/b)
        """
        MinNumNodes.append(round(- (- CumPerims[-1] // dP)) )
        
    
    print(f'\nThere are {NumContourPts} nodes in each contour (total of',
          f'{sum(NumContourPts)} nodes) in all {C} contours.')
    
    # The minimum number of nodes that will need to be added:
    MinNumNodesToAdd = max(MinNumNodes)
    
    # Get list representing the contour numbers:
    ContourNums = list(range(len(Contours)))
    
    # Initialise lists:
    SSContours = []
    SSIsOrigNodes = []
    SSNumPts = []
    
    # Loop through all Contours:
    for c in range(C):
        # For iterable c, the other contour indices are:
        OtherInds = copy.deepcopy(ContourNums) # start with copy of ContourNums
        OtherInds.pop(c) # remove c from list
        
        # The number of contour points in all contours other than the c^th
        # contour (i.e. in all contour numbers given by the list OtherInds):
        NumPtsInOthers = 0
        
        for j in OtherInds:
            NumPtsInOthers += len(Contours[j])
        
        # The number of nodes that will have to be added to each contour is the 
        # MinNumNodesToAdd plus the number of original nodes in all other 
        # contours (= NumPtsInOthers):
        NumNodesToAdd = MinNumNodesToAdd + NumPtsInOthers
        
        # Get the cumulative super-sampled perimeter:
        CumSSPerims = GetNormCumulativeSuperSampledPerimeters(CumPerimetersNorm=NormCumPerims[c],
                                                              NumNodesToAdd=NumNodesToAdd)
        
        # Get list of booleans for original (True) and added (False) nodes:
        IsOrigNode = GetIsOrigNode(Contour=Contours[c], NumNodesToAdd=NumNodesToAdd)

        
        #if c == 0:
        #    print('\n')
        #print(f'c = {c}, NumPtsInOthers = {NumPtsInOthers}, NumNodesToAdd = {NumNodesToAdd}, len(CumSSPerims) = {len(CumSSPerims)}')
        
        # Get the nodes per segment:
        Inds,\
        IsOrigNodeSorted,\
        IndsOrigNodes,\
        NodesToAddPerSegment = GetNodesToAddPerSegment(CumSSPerimNorm=CumSSPerims, 
                                                       IsOrigNode=IsOrigNode)
        
        # Super-sample the contour:
        SSContour,\
        SSIsOrigNode = SuperSampleContour(Contour=Contours[c], 
                                          NodesToAddPerSegment=NodesToAddPerSegment)
        
        SSContours.append(SSContour)
        SSIsOrigNodes.append(SSIsOrigNode)
        SSNumPts.append(len(SSContour))
        
        
    # Re-order SSContours and SSIsOrigNodes from the 2nd item onwards such that
    # the integrated line lengths are minimised (i.e. minimal area of the 
    # surfaces created by linking points in SSContours[0] and SSContours[1], N 
    # different ways for all N points in SSContours, and so on for 
    # SSContours[1] and SSContours[2]):
    for c in range(C - 1):
        # Find the starting index for SSContours[c+1] that minimises the 
        # integrated line lengths between it and SSContours[c]:
        IndMinCumL = FindIndForMinCumLength(Contour1=SSContours[c], 
                                            Contour2=SSContours[c+1])
        
        # Shift the points in SSContours[c+1] and SSIsOrigNodes[c+1]:
        SSContours[c+1] = ShiftContourPoints(Contour=SSContours[c+1], 
                                             Shift=IndMinCumL)
        
        SSIsOrigNodes[c+1] = ShiftContourPoints(Contour=SSIsOrigNodes[c+1], 
                                                Shift=IndMinCumL)
    
    
    # Number of points in each super-sampled contour:
    P = SSNumPts[0]
    
    print(f'\nThere are {P} nodes in each super-sampled contour (total of',
          f'{sum(SSNumPts)} nodes) in all {C} contours.')
    
    
    # Remove all nodes which are not original to all super-sampled contours, 
    # leaving behind "over-sampled" contours:
    # Initialise lists:
    OSContours = [ [] for i in range(C) ]
    OSIsOrigNodes = [ [] for i in range(C) ]
    OSNumPts = [ 0 for i in range(C) ]
    
    # Loop through each super-sampled point:
    for p in range(P):
        # Initialise the list of boolean values of OSIsOrigNodes for each 
        # point:
        SSIsOrigNodes_p = []
        
        # Loop through each super-sampled contour:
        for c in range(C):
            SSIsOrigNodes_p.append(SSIsOrigNodes[c][p])
            
        # If the sum of SSIsOrigNodes_p = 0 (i.e. if all entries are False),
        # point p in all contours are not original nodes.
        # If the sum is greater than 0, at least one node is original, in which
        # case, keep this node in the list of over-sampled contours:
        if sum(SSIsOrigNodes_p) > 0:
            # Loop through each contour and add this point:
            for c in range(C):
                OSContours[c].append(SSContours[c][p])
                OSIsOrigNodes[c].append(SSIsOrigNodes[c][p])
                OSNumPts[c] += 1
    
    
    #print('OSNumPts =', OSNumPts)
    
    #OSNumPts = []

    #for c in range(C):
    #    OSNumPts.append(len(OSContours))
        
    # Number of points in each over-sampled contour:
    Q = OSNumPts[0]
    
    print(f'\nThere are {Q} nodes in each over-sampled contour (total of',
          f'{sum(OSNumPts)} nodes) in all {C} contours.')        
    
    
    # The number of slices:
    S = len(ContourData['SliceNo'])
    
    #print(f'C = {C}, len(Cinds) = {len(Cinds)}, len(SSContours) = {len(SSContours)}')
    
    # Get the Image Attributes for the Fixed image domain:
    #FixOrigin, FixDirs,\
    #FixSpacings, FixDims = GetImageAttributes(DicomDir=FixedDicomDir, 
    #                                          Package='pydicom')
    
    # Create a new list of super-sampled and over-sampled contours containing 
    # [] for slices that have no contours:
    FixSSContoursPCS = [ [] for i in range(S) ]
    #FixSSContoursICS = [ [] for i in range(S) ]
    FixSSIsOrigNodes = [ [] for i in range(S) ]
    FixOSContoursPCS = [ [] for i in range(S) ]
    #FixOSContoursICS = [ [] for i in range(S) ]
    FixOSIsOrigNodes = [ [] for i in range(S) ]
    
    # Add the non-empty lists:
    """ Note:
        The [] around SSContours[c], OSContours[c], SSIsOrigNodes[c] and 
        OSIsOrigNodes[c] ensures that the list of points (which correspond a 
        single contour) is itself a list (so that for every slice, there is one 
        contour with N points, rather than a list of N points).
    """
    for c in range(C):
        #FixSSContoursPCS[Cinds[c]] = SSContours[c]
        FixSSContoursPCS[Cinds[c]] = [SSContours[c]]
        
        #FixOSContoursPCS[Cinds[c]] = OSContours[c]
        FixOSContoursPCS[Cinds[c]] = [OSContours[c]]
        
        #FixSSContoursICS[Cinds[c]] = PCStoICS(Pts_PCS=SSContours[c], 
        #                                      Origin=FixOrigin, 
        #                                      Directions=FixDirs, 
        #                                      Spacings=FixSpacings)
        
        #FixOSContoursICS[Cinds[c]] = PCStoICS(Pts_PCS=OSContours[c], 
        #                                      Origin=FixOrigin, 
        #                                      Directions=FixDirs, 
        #                                      Spacings=FixSpacings)
        
        #FixSSIsOrigNodes[Cinds[c]] = SSIsOrigNodes[c]
        FixSSIsOrigNodes[Cinds[c]] = [SSIsOrigNodes[c]]
        
        #FixOSIsOrigNodes[Cinds[c]] = OSIsOrigNodes[c]
        FixOSIsOrigNodes[Cinds[c]] = [OSIsOrigNodes[c]]
    
    
    #print(f'len(FixSSContoursPCS) = {len(FixSSContoursPCS)}')
    
    # Add the super-sampled contours to ContourData:
    ContourData.update({'FixSSPtsPCS' : FixSSContoursPCS,
                        #'FixSSPointsICS' : FixSSContoursICS,
                        'FixOSPtsPCS' : FixOSContoursPCS#,
                        #'FixOSPointsICS' : FixOSContoursICS
                        })
    
    return ContourData






def ResampleAllTransformedContours(ContourData, dP):
    """
    Resample all transformed contours belonging to the Fixed image domain.
    
    Inputs:
        ContourData - Dictionary containing a list of contour points [x, y, z]
                      arranged along rows for each DICOM slice, and along 
                      columns for different contours (i.e. a list of lists of 
                      lists). Slices without contours have empty list ([]).
        
        dP          - A float denoting the desired inter-node spacing to use
                      when super-sampling the contours.
        
        
    Returns:
        ContourData - Dictionary with resampled contours added.
    
    
    Note:
        This function is adapted from ResampleAllFixedContours.  This function
        resamples the transformed Fixed contours rather than the original ones.
    """
    # Import packages and functions:
    import copy
    #from GetImageAttributes import GetImageAttributes
    #import importlib
    #import PCStoICS
    #importlib.reload(PCStoICS)
    #from PCStoICS import PCStoICS
    
    # Get the indices of the slices that contain contours in the Fixed image:
    Cinds = GetIndsOfContourDataWithContourType(ContourData=ContourData, 
                                                ContourTypeNo=1)
    
    # The number of contours:
    C = len(Cinds)
    
    #print('Contours exist on slices', Cinds, '\n')
    
    # Initialise lists:
    Contours = []
    NumContourPts = []
    #CumPerims = []
    NormCumPerims = []
    MinNumNodes = []
        
    # Loop through all Inds:
    for i in Cinds:
        """ 
        Note:
            The list of contours needs to be addressed with [0] since there is
            at most one contour per slice.
            
            The algorithm may need to be generalised should it need to deal 
            with cases where there is more than one contour per slice.
        """
        Contour = ContourData['FixPtsPCS'][i][0]
        
        #print(f'\n\ni = {i}\nContour =', Contour)
        
        #print(f'There are {len(Contour)} points in the contour on slice {i}.')
        
        # Close the contour:
        Contour.append(Contour[0])
        
        # Ensure that the points run clockwise:
        Contour = ReverseIfAntiClockwise(Contour=Contour)
        
        Contours.append(Contour)
        
        NumContourPts.append(len(Contour))
    
        # Get the cumulative perimeters:
        CumPerims = GetCumulativePerimeters(Contour=Contour)
        
        # Normalise the cumulative perimeters:
        NormCumPerims.append(NormaliseCumulativePerimeters(CumPerimeters=CumPerims))
        
        # The number of nodes required to achieve the minimum inter-node 
        # spacing of dP:
        """ 
        Note:
            a//b yields floor(a/b)
            
            - (-a//b) yields ceil(a/b)
        """
        MinNumNodes.append(round(- (- CumPerims[-1] // dP)) )
        
    
    print(f'\nThere are {NumContourPts} nodes in each contour (total of',
          f'{sum(NumContourPts)} nodes) in all {C} contours.')
    
    # The minimum number of nodes that will need to be added:
    MinNumNodesToAdd = max(MinNumNodes)
    
    # Get list representing the contour numbers:
    ContourNums = list(range(len(Contours)))
    
    # Initialise lists:
    SSContours = []
    SSIsOrigNodes = []
    SSNumPts = []
    
    # Loop through all Contours:
    for c in range(C):
        # For iterable c, the other contour indices are:
        OtherInds = copy.deepcopy(ContourNums) # start with copy of ContourNums
        OtherInds.pop(c) # remove c from list
        
        # The number of contour points in all contours other than the c^th
        # contour (i.e. in all contour numbers given by the list OtherInds):
        NumPtsInOthers = 0
        
        for j in OtherInds:
            NumPtsInOthers += len(Contours[j])
        
        # The number of nodes that will have to be added to each contour is the 
        # MinNumNodesToAdd plus the number of original nodes in all other 
        # contours (= NumPtsInOthers):
        NumNodesToAdd = MinNumNodesToAdd + NumPtsInOthers
        
        # Get the cumulative super-sampled perimeter:
        CumSSPerims = GetNormCumulativeSuperSampledPerimeters(CumPerimetersNorm=NormCumPerims[c],
                                                              NumNodesToAdd=NumNodesToAdd)
        
        # Get list of booleans for original (True) and added (False) nodes:
        IsOrigNode = GetIsOrigNode(Contour=Contours[c], NumNodesToAdd=NumNodesToAdd)

        
        #if c == 0:
        #    print('\n')
        #print(f'c = {c}, NumPtsInOthers = {NumPtsInOthers}, NumNodesToAdd = {NumNodesToAdd}, len(CumSSPerims) = {len(CumSSPerims)}')
        
        # Get the nodes per segment:
        Inds,\
        IsOrigNodeSorted,\
        IndsOrigNodes,\
        NodesToAddPerSegment = GetNodesToAddPerSegment(CumSSPerimNorm=CumSSPerims, 
                                                       IsOrigNode=IsOrigNode)
        
        # Super-sample the contour:
        SSContour,\
        SSIsOrigNode = SuperSampleContour(Contour=Contours[c], 
                                          NodesToAddPerSegment=NodesToAddPerSegment)
        
        SSContours.append(SSContour)
        SSIsOrigNodes.append(SSIsOrigNode)
        SSNumPts.append(len(SSContour))
        
        
    # Re-order SSContours and SSIsOrigNodes from the 2nd item onwards such that
    # the integrated line lengths are minimised (i.e. minimal area of the 
    # surfaces created by linking points in SSContours[0] and SSContours[1], N 
    # different ways for all N points in SSContours, and so on for 
    # SSContours[1] and SSContours[2]):
    for c in range(C - 1):
        # Find the starting index for SSContours[c+1] that minimises the 
        # integrated line lengths between it and SSContours[c]:
        IndMinCumL = FindIndForMinCumLength(Contour1=SSContours[c], 
                                            Contour2=SSContours[c+1])
        
        # Shift the points in SSContours[c+1] and SSIsOrigNodes[c+1]:
        SSContours[c+1] = ShiftContourPoints(Contour=SSContours[c+1], 
                                             Shift=IndMinCumL)
        
        SSIsOrigNodes[c+1] = ShiftContourPoints(Contour=SSIsOrigNodes[c+1], 
                                                Shift=IndMinCumL)
    
    
    # Number of points in each super-sampled contour:
    P = SSNumPts[0]
    
    print(f'\nThere are {P} nodes in each super-sampled contour (total of',
          f'{sum(SSNumPts)} nodes) in all {C} contours.')
    
    
    # Remove all nodes which are not original to all super-sampled contours, 
    # leaving behind "over-sampled" contours:
    # Initialise lists:
    OSContours = [ [] for i in range(C) ]
    OSIsOrigNodes = [ [] for i in range(C) ]
    OSNumPts = [ 0 for i in range(C) ]
    
    # Loop through each super-sampled point:
    for p in range(P):
        # Initialise the list of boolean values of OSIsOrigNodes for each 
        # point:
        SSIsOrigNodes_p = []
        
        # Loop through each super-sampled contour:
        for c in range(C):
            SSIsOrigNodes_p.append(SSIsOrigNodes[c][p])
            
        # If the sum of SSIsOrigNodes_p = 0 (i.e. if all entries are False),
        # point p in all contours are not original nodes.
        # If the sum is greater than 0, at least one node is original, in which
        # case, keep this node in the list of over-sampled contours:
        if sum(SSIsOrigNodes_p) > 0:
            # Loop through each contour and add this point:
            for c in range(C):
                OSContours[c].append(SSContours[c][p])
                OSIsOrigNodes[c].append(SSIsOrigNodes[c][p])
                OSNumPts[c] += 1
    
    
    #print('OSNumPts =', OSNumPts)
    
        
    # Number of points in each over-sampled contour:
    Q = OSNumPts[0]
    
    print(f'\nThere are {Q} nodes in each over-sampled contour (total of',
          f'{sum(OSNumPts)} nodes) in all {C} contours.')        
    
    
    # The number of slices:
    S = len(ContourData['SliceNo'])
    
    #print(f'C = {C}, len(Cinds) = {len(Cinds)}, len(SSContours) = {len(SSContours)}')
    
    
    # Create a new list of super-sampled and over-sampled contours containing 
    # [] for slices that have no contours:
    TraSSContoursPCS = [ [] for i in range(S) ]
    #TraSSContoursICS = [ [] for i in range(S) ]
    TraSSIsOrigNodes = [ [] for i in range(S) ]
    TraOSContoursPCS = [ [] for i in range(S) ]
    #TraOSContoursICS = [ [] for i in range(S) ]
    TraOSIsOrigNodes = [ [] for i in range(S) ]
    
    # Add the non-empty lists:
    """ Note:
        The [] around SSContours[c], OSContours[c], SSIsOrigNodes[c] and 
        OSIsOrigNodes[c] ensures that the list of points (which correspond a 
        single contour) is itself a list (so that for every slice, there is one 
        contour with N points, rather than a list of N points).
    """
    for c in range(C):
        #TraSSContoursPCS[Cinds[c]] = SSContours[c]
        TraSSContoursPCS[Cinds[c]] = [SSContours[c]]
        
        #TraOSContoursPCS[Cinds[c]] = OSContours[c]
        TraOSContoursPCS[Cinds[c]] = [OSContours[c]]
        
        #TraSSContoursICS[Cinds[c]] = PCStoICS(Pts_PCS=SSContours[c], 
        #                                      Origin=FixOrigin, 
        #                                      Directions=FixDirs, 
        #                                      Spacings=FixSpacings)
        
        #TraOSContoursICS[Cinds[c]] = PCStoICS(Pts_PCS=OSContours[c], 
        #                                      Origin=FixOrigin, 
        #                                      Directions=FixDirs, 
        #                                      Spacings=FixSpacings)
        
        #TraSSIsOrigNodes[Cinds[c]] = SSIsOrigNodes[c]
        TraSSIsOrigNodes[Cinds[c]] = [SSIsOrigNodes[c]]
        
        #TraOSIsOrigNodes[Cinds[c]] = OSIsOrigNodes[c]
        TraOSIsOrigNodes[Cinds[c]] = [OSIsOrigNodes[c]]
    
    
    #print(f'len(TraSSContoursPCS) = {len(TraSSContoursPCS)}')
    
    # Add the super-sampled contours to ContourData:
    ContourData.update({'TraSSPtsPCS' : TraSSContoursPCS,
                        #'TraSSPointsICS' : TraSSContoursICS,
                        'TraOSPtsPCS' : TraOSContoursPCS#,
                        #'TraOSPointsICS' : TraOSContoursICS
                        })
    
    return ContourData
    
    
    
    
  
    

def RegisterImageStacks(FixedDicomDir, MovingDicomDir):
    """
    Register image stacks using SimpleElastix.
    
    Inputs:
        FixedDicomDir      - Directory containing the DICOMs for the Fixed 
                             image domain.
        
        MovingDicomDir     - Directory containing the DICOMs for the Moving 
                             image domain.
        
        
    Returns:
        FixIm              - 3D Fixed image as a SimpleITK object
        
        MovIm              - 3D Moving image as a SimpleITK object
        
        RegIm              - 3D Registered image as a SimpleITK object
        
        ElastixImFilt      - Image transformation filter used by Elastix to
                             transform MovingImage to the Fixed image domain.
    
    """

    # Import packages and functions:
    import SimpleITK as sitk
    from GetImageAttributes import GetImageAttributes
    from RunSimpleElastixReg import RunSimpleElastixReg
                                                                     
    # Chose which package to use to get the Image Plane Attributes:
    #package = 'sitk'
    package = 'pydicom'

    # Get the Image Attributes for the images:
    FixOrigin, FixDirs,\
    FixSpacings, FixDims = GetImageAttributes(DicomDir=FixedDicomDir, 
                                              Package=package)
    
    MovOrigin, MovDirs,\
    MovSpacings, MovDims = GetImageAttributes(DicomDir=MovingDicomDir, 
                                              Package=package)

    # Read in the 3D stack of Fixed DICOMs:
    FixReader = sitk.ImageSeriesReader()
    FixNames = FixReader.GetGDCMSeriesFileNames(FixedDicomDir)
    FixReader.SetFileNames(FixNames)
    FixIm = FixReader.Execute()
    FixIm = sitk.Cast(FixIm, sitk.sitkFloat32)
    
    # Read in the 3D stack of Moving DICOMs:
    MovReader = sitk.ImageSeriesReader()
    MovNames = MovReader.GetGDCMSeriesFileNames(MovingDicomDir)
    MovReader.SetFileNames(MovNames)
    MovIm = MovReader.Execute()
    MovIm = sitk.Cast(MovIm, sitk.sitkFloat32)
    
    # Register MovIm to FixIm to obtain the transformation filter:
    RegIm, ElastixImFilt = RunSimpleElastixReg(FixedIm=FixIm, MovingIm=MovIm, 
                                               LogToConsole=False)
    
    return FixIm, MovIm, RegIm, ElastixImFilt
    
    
    
    
def TransformInterpolatedContours(InterpData, ElastixImFilt, MovIm):
    """
    Transform the interpolated contours and the over-sampled contours that were
    used to interpolate, using the transformation filter from Elastix, within
    the dictionary InterpData.
    
    Inputs:
        InterpData         - A dictionary containing interpolated data.
        
        ElastixImFilt      - Image transformation filter used by Elastix to
                             transform MovingImage to the Fixed image domain.
                             
        MovIm              - 3D Moving image as a SimpleITK object
        
        
    Returns:
        InterpData         - As above but with added entries for the 
                             transformed contours.
    
    """

    # Import packages and functions:
    from CreateInputFileForElastix import CreateInputFileForElastix
    from TransformPoints import TransformPoints
    from ParseTransformixOutput import ParseTransformixOutput

                                                         
    """
    BaseKeys = ['OSContour1', 'OSContour2', 'InterpContour']
    
    FixIndsKeys = ['FixOSContour1Inds', 'FixOSContour2Inds', 'FixInterpContourInds']
    FixPtsKeys = ['Fix' + BaseKeys[i] + 'Pts' for i in range(len(BaseKeys))]
    
    MovIndsKeys = ['Mov' + BaseKeys[i] + 'Inds' for i in range(len(BaseKeys))]
    MovPtsKeys = ['Mov' + BaseKeys[i] + 'Pts' for i in range(len(BaseKeys))]
    """
    
    
    
    # Initialise the additional keys to be added to InterpData (to ensure that 
    # the keys are added in the same order for Mov as for Fix):
    InterpData.update({
                       'MovOSContour1Inds':[],
                       'MovOSContour2Inds':[],
                       'MovInterpContourInds':[],
                       'MovOSContour1Pts':[],
                       'MovOSContour2Pts':[],
                       'MovInterpContourPts':[]
                       })
    
    # Initialise a list of all points (along rows, no grouping by slice index):
    AllPoints = []
    
    # Create lists of keys in InterpData whose points will be appended to AllPoints:
    FixPtsKeys = ['FixOSContour1Pts', 'FixOSContour2Pts', 'FixInterpContourPts']

    # Loop through each row in InterpData::
    for i in range(len(InterpData['InterpSliceInd'])):
        # Loop through each key in FixPtsKeys:
        for key in FixPtsKeys:
            Points = InterpData[key][i]
            
            # If Points is not []:
            if Points:
                #AllPoints.append(Points)
                AllPoints.extend(Points)
            
    # Create inputpoints.txt for Elastix, containing the contour points to be
    # transformed:
    CreateInputFileForElastix(Points=AllPoints)

    # Transform MovingContourPts:
    TransformPoints(Points=AllPoints, Image=MovIm, 
                    TransformFilter=ElastixImFilt)

    # Parse outputpoints.txt:
    PtNos, FixInds, FixPts_PCS,\
    FixOutInds, MovPts_PCS,\
    Def_PCS, MovInds = ParseTransformixOutput()
    
    
    """
    # Append the transformed results to InterpData:
    InterpData[FixIndsKeys[k]].append(FixInds) # the indices of the input (fixed) points
    #InterpData[MovIndsKeys[k]].append(MovInds) # the indices of the output (moving/transformed) points
    #InterpData[MovPtsKeys[k]].append(MovPts_PCS) # the output (moving/transformed) points
    
    # Get list of keys in InterpData:
    keys = list(InterpData.keys())
    
    if MovIndsKeys[k] in keys:
        InterpData[MovIndsKeys[k]].append(MovInds) # the indices of the output (moving/transformed) points
    else:
        InterpData.update({MovIndsKeys[k] : [MovInds]}) # the indices of the output (moving/transformed) points
        
    if MovPtsKeys[k] in keys:
        InterpData[MovPtsKeys[k]].append(MovPts_PCS) # the output (moving/transformed) points
    else:
        InterpData.update({MovPtsKeys[k] : [MovPts_PCS]}) # the output (moving/transformed) points
    """
    
    
    # Re-group the transformed data that was parsed into the corresponding rows
    # and columns (keys) in InterpData.
    
    # Create lists of keys that will be added to InterpData:
    FixIndsKeys = ['FixOSContour1Inds', 'FixOSContour2Inds', 'FixInterpContourInds']
    MovIndsKeys = ['MovOSContour1Inds', 'MovOSContour2Inds', 'MovInterpContourInds']
    MovPtsKeys = ['MovOSContour1Pts', 'MovOSContour2Pts', 'MovInterpContourPts']
    
    # Keep track of the number of points/indices that are assigned to each new 
    # key:
    N = 0
    
    # Loop through each row in InterpData::
    for i in range(len(InterpData['InterpSliceInd'])):
        # Loop through each key in FixPtsKeys:
        for k in range(len(FixPtsKeys)):
            Points = InterpData[FixPtsKeys[k]][i]
            
            # Append the Fixed (input) indices:
            InterpData[FixIndsKeys[k]].append(FixInds[N : N + len(Points)])
            
            # Append the Moving (transformed) indices: 
            InterpData[MovIndsKeys[k]].append(MovInds[N : N + len(Points)])
            
            # Append the Moving (transformed) points:
            InterpData[MovPtsKeys[k]].append(MovPts_PCS[N : N + len(Points)])
            
            # Update the number of points/indices that have been assigned:
            N += len(Points)
    
    
    return InterpData





def TransformFixedContours(ContourData, ElastixImFilt, MovIm):
    """
    Transform the Fixed contours in ContourData using the transformation 
    filter from Elastix.
    
    Inputs:
        ContourData   - Dictionary containing a list of contour points 
                        [x, y, z] arranged along rows for each DICOM slice, 
                        and along columns for different contours (i.e. a list 
                        of lists of lists).  Slices without contours have empty 
                        list ([]).
        
        ElastixImFilt - Image transformation filter used by Elastix to 
                        transform MovingImage to the Fixed image domain.
                             
        MovIm         - 3D Moving image as a SimpleITK object
        
        
    Returns:
        ContourData  - As above but with added entries for the transformed
                       contour points.
    
    """

    # Import packages and functions:
    from CreateInputFileForElastix import CreateInputFileForElastix
    from TransformPoints import TransformPoints
    from ParseTransformixOutput import ParseTransformixOutput

    
    # Initialise the additional keys to be added to ContourData (to ensure  
    # that the keys are added in the same order for Mov as for Fix):
    ContourData.update({
                        'TraPtsPCS':[],
                        'TraSSPtsPCS':[],
                        'TraOSPtsPCS':[],
                        'FixInds':[],
                        'FixSSInds':[],
                        'FixOSInds':[],
                        'TraInds':[],
                        'TraSSInds':[],
                        'TraOSInds':[]
                        })
    
    # Initialise a list of all points (along rows, no grouping by slice index):
    AllPoints = []
    
    # Create lists of keys in ContourData whose points will be appended to 
    # AllPoints:
    FixPtsKeys = ['FixPtsPCS', 'FixSSPtsPCS', 'FixOSPtsPCS']
    
    # The number of slices:
    S = len(ContourData['FixPtsPCS'])

    # Loop through each row in ContourData::
    for s in range(S):
        # Loop through each key in FixPtsKeys:
        for key in FixPtsKeys:
            ContourList = ContourData[key][s]
            
            # If ContourList is not []:
            if ContourList:
                """ 
                Note:
                    The [0] indexing of ContourData[key][s] is because each
                    slice for the Fixed contours consists of a single list of N 
                    points, rather than a list of N points (see the function
                    ResampleAllFixedContours).
                    
                    This algorithm may need to be modified to deal with the 
                    general case of multiple contours per slice.
                """
                Points = ContourList[0]
            
                #AllPoints.append(Points)
                AllPoints.extend(Points)
            
    # Create inputpoints.txt for Elastix, containing the contour points to be
    # transformed:
    CreateInputFileForElastix(Points=AllPoints)

    # Transform MovingContourPts:
    TransformPoints(Points=AllPoints, Image=MovIm, 
                    TransformFilter=ElastixImFilt)

    # Parse outputpoints.txt:
    PtNos, FixInds, FixPts_PCS,\
    FixOutInds, TraPts_PCS,\
    Def_PCS, TraInds = ParseTransformixOutput()
    
    
    
    # Re-group the transformed data that was parsed into the corresponding rows
    # and columns (keys) in ContourData.
    
    # Create lists of keys in ContourData that will be updated:
    FixIndsKeys = ['FixInds', 'FixSSInds', 'FixOSInds']
    TraIndsKeys = ['TraInds', 'TraSSInds', 'TraOSInds']
    TraPtsKeys = ['TraPtsPCS', 'TraSSPtsPCS', 'TraOSPtsPCS']
    
    # Keep track of the number of points/indices that are assigned to each new 
    # key:
    N = 0
    
    # Loop through each slice:
    for s in range(S):
        # Loop through each key in FixPtsKeys, MovIndsKeys and MovPtsKeys:
        for k in range(len(FixPtsKeys)):
            ContourList = ContourData[FixPtsKeys[k]][s]
            
            # If ContourList != []:
            if ContourList:
                Points = ContourList[0] # [0] since only one contour for now
                
                # Append the Fixed (input) indices:
                #ContourData[FixIndsKeys[k]].append(FixInds[N : N + len(Points)])
                ContourData[FixIndsKeys[k]].append([FixInds[N : N + len(Points)]])
                
                # Append the Moving (transformed) indices: 
                #ContourData[MovIndsKeys[k]].append(MovInds[N : N + len(Points)])
                ContourData[TraIndsKeys[k]].append([TraInds[N : N + len(Points)]])
                
                # Append the Moving (transformed) points:
                #ContourData[MovPtsKeys[k]].append(MovPts_PCS[N : N + len(Points)])
                ContourData[TraPtsKeys[k]].append([TraPts_PCS[N : N + len(Points)]])
                
                # Update the number of points/indices that have been assigned:
                N += len(Points)
        
            else:
                ContourData[FixIndsKeys[k]].append([])
    
                ContourData[TraIndsKeys[k]].append([])
    
                ContourData[TraPtsKeys[k]].append([])
    
    
    """
    Note:
        The lists added to ContourData are enclosed within [] to ensure that
        they are a single list of N points rather than a list of N points.
    """
    
    return ContourData






def TransformFixedContours_v2(ContourData, ElastixImFilt, MovIm):
    """
    Transform the Fixed contours in ContourData using the transformation 
    filter from Elastix.
    
    Inputs:
        ContourData   - Dictionary containing a list of contour points 
                        [x, y, z] arranged along rows for each DICOM slice, 
                        and along columns for different contours (i.e. a list 
                        of lists of lists).  Slices without contours have empty 
                        list ([]).
        
        ElastixImFilt - Image transformation filter used by Elastix to 
                        transform MovingImage to the Fixed image domain.
                             
        MovIm         - 3D Moving image as a SimpleITK object
        
        
    Returns:
        ContourData  - As above but with added entries for the transformed
                       contour points.
    
    
    Note:
        This is adapted from TransformFixedContours.  The difference is that for
        the previous version, the Fixed contour points were resampled prior to
        transforming.  In this version, the Fixed points will be transformed, and 
        the resulting points will later be resampled.
        
        The keys commented out in the initialisation of the additional keys in
        ContourData reflect the lists that were inputted in the previous version
        but not here.
    """

    # Import packages and functions:
    from CreateInputFileForElastix import CreateInputFileForElastix
    from TransformPoints import TransformPoints
    from ParseTransformixOutput import ParseTransformixOutput

    
    # Initialise the additional keys to be added to ContourData (to ensure  
    # that the keys are added in the same order for Mov as for Fix):
    ContourData.update({
                        'TraPtsPCS':[],
                        #'TraSSPtsPCS':[],
                        #'TraOSPtsPCS':[],
                        'FixInds':[],
                        #'FixSSInds':[],
                        #'FixOSInds':[],
                        'TraInds':[]#,
                        #'TraSSInds':[],
                        #'TraOSInds':[]
                        })
    
    # Initialise a list of all points (along rows, no grouping by slice index):
    AllPoints = []
    
    # The number of slices:
    S = len(ContourData['FixPtsPCS'])

    # Loop through each slice in ContourData['FixPtsPCS']:
    for s in range(S):
        ContourList = ContourData['FixPtsPCS'][s]
        
        # If ContourList is not []:
        if ContourList:
            """ 
            Note:
                The [0] indexing of ContourData['FixPtsPCS'][s] is because 
                each slice for the Fixed contours consists of a single list  
                of N points, rather than a list of N points (see the 
                function ResampleAllFixedContours).
                
                This algorithm may need to be modified to deal with the 
                general case of multiple contours per slice.
            """
            Points = ContourList[0]
        
            #AllPoints.append(Points)
            AllPoints.extend(Points)
            
    # Create inputpoints.txt for Elastix, containing the contour points to be
    # transformed:
    CreateInputFileForElastix(Points=AllPoints)

    # Transform MovingContourPts:
    TransformPoints(Points=AllPoints, Image=MovIm, 
                    TransformFilter=ElastixImFilt)

    # Parse outputpoints.txt:
    PtNos, FixInds, FixPts_PCS,\
    FixOutInds, TraPts_PCS,\
    Def_PCS, TraInds = ParseTransformixOutput()
    
    
    
    # Re-group the transformed data that was parsed into the corresponding rows
    # and columns (keys) in ContourData.  
    # Keep track of the number of points/indices that are assigned to each new 
    # key:
    N = 0
    
    # Loop through each slice:
    for s in range(S):
        ContourList = ContourData['FixPtsPCS'][s]
        
        # If ContourList != []:
        if ContourList:
            Points = ContourList[0] # [0] since only one contour for now
            
            # Append the Fixed (input) indices:
            #ContourData[FixIndsKeys[k]].append(FixInds[N : N + len(Points)])
            ContourData['FixInds'].append([FixInds[N : N + len(Points)]])
            
            # Append the Moving (transformed) indices: 
            #ContourData[MovIndsKeys[k]].append(MovInds[N : N + len(Points)])
            ContourData['TraInds'].append([TraInds[N : N + len(Points)]])
            
            # Append the Moving (transformed) points:
            #ContourData[MovPtsKeys[k]].append(MovPts_PCS[N : N + len(Points)])
            ContourData['TraPtsPCS'].append([TraPts_PCS[N : N + len(Points)]])
            
            # Update the number of points/indices that have been assigned:
            N += len(Points)
    
        else:
            ContourData['FixInds'].append([])

            ContourData['TraInds'].append([])

            ContourData['TraPtsPCS'].append([])
    
    
    """
    Note:
        The lists added to ContourData are enclosed within [] to ensure that
        they are a single list of N points rather than a list of N points.
    """
    
    return ContourData
    
    
    
    



def LinkPointsAcrossContours(Contours):
    """
    Link points across contours (coordinates that link the same node across 
    all contours).
    
    Inputs:
        Contours      - List of a list of contour points
        
    Outputs:
        SweepAllNodes - List of linked points across all contours for all 
                        contour points.
        
    """
    
    # Import packages:
    import numpy as np
    
    # Initialise the number of points in each slice containing contours, and
    # the indices of the slices containing contours:
    NumPtsPerSliceContainingContours = []
    IndsSlicesContainingContours = []
    
    # The number of slices:
    S = len(Contours)
    
        
    # Loop through all slices:    
    for s in range(S):
        contours = Contours[s]
        
        # Get the shape of the contour data for this slice:
        DataShape = np.array(contours).shape
        
        #LenDataShape = len(DataShape)
        
        # The number of contours:
        C = DataShape[0]
        
        # If C != 0, get the Npoints in each contour:
        if C:
            # Initialise the number of points for each contour:
            P = 0
            
            # Loop through all contours:
            for c in range(C):
                P += len(contours[c])
                
            NumPtsPerSliceContainingContours.append(P)
            
            IndsSlicesContainingContours.append(s)
        else:
            P = 0
            
            
    # Get the list of unique number of points per slice containing contours:
    SetOfNumPts = list(set(NumPtsPerSliceContainingContours))
                
    #print('SetOfNumPts =', SetOfNumPts) 
    
    # If len(SetOfNumPts) = 1, all contours have the same number of points,
    # so can be linked along each point in each contour:
    if len(SetOfNumPts) == 1:
        # The number of nodes:
        N = SetOfNumPts[0]
        
        #print(f'N = {N}')
        
        # Initialise the list of linked nodes across all contours ("sweep") for 
        # all nodes along the contours:
        SweepAllNodes = []
            
        # Loop through each point:
        for n in range(N):
            # Initialise the list of linked nodes across all contours ("sweep")
            # for this node:
            SweepThisNode = []
            
            # Loop through each contour:
            for i in IndsSlicesContainingContours:
                SweepThisNode.append(Contours[i][0][n])
                
            
            SweepAllNodes.append(SweepThisNode)
        
        return SweepAllNodes
                
    else:
        print('There are an unequal number of points in the contours:',
              NumPtsPerSliceContainingContours)
        
        return
    
    
    
    
    
def CreateContourSweepData(ContourData):
    """
    Create a new dictionary called ContourSweepData, containing the lists of
    points that link each node across all contours.
    
    Inputs:
        ContourData      - Dictionary containing a list of contour points 
                           [x, y, z] arranged along rows for each DICOM slice,  
                           and along columns for different contours (i.e. a  
                           list of lists of lists). Slices without contours 
                           have empty list ([]).
        
        
    Returns:
        ContourSweepData - Dictionary containing the list of points [x, y, z]
                           that link any given node in each contour, for all
                           nodes. 
    
    """
    
    # Create a list of all the keys in ContourData corresponding to the set of
    # contours to be linked (note only groups of contours with equal length can
    # be linked):
    Keys = ['FixSSPtsPCS', 'FixOSPtsPCS', 'TraSSPtsPCS', 'TraOSPtsPCS']
    
    # Initialise the new dictionary:
    ContourSweepData = {}
    
    # Loop through each key in Keys:
    for key in Keys:
        SweepAllNodes = LinkPointsAcrossContours(ContourData[key])
        
        # Update the dictionary:
        ContourSweepData.update({key : SweepAllNodes})
        
    
    return ContourSweepData
    
    
    


def CreateContourSweepData_v2(ContourData):
    """
    Create a new dictionary called ContourSweepData, containing the lists of
    points that link each node across all contours.
    
    Inputs:
        ContourData      - Dictionary containing a list of contour points 
                           [x, y, z] arranged along rows for each DICOM slice,  
                           and along columns for different contours (i.e. a  
                           list of lists of lists). Slices without contours 
                           have empty list ([]).
        
        
    Returns:
        ContourSweepData - Dictionary containing the list of points [x, y, z]
                           that link any given node in each contour, for all
                           nodes. 
    
    Note:
        This function was adapated from CreateContourSweepData, to work with
        ContourData that does not have resampled Fixed points ('FixSSPtsPCS'
        and 'FixOSPtsPCS').
    """
    
    # Create a list of all the keys in ContourData corresponding to the set of
    # contours to be linked (note only groups of contours with equal length can
    # be linked):
    #Keys = ['FixSSPtsPCS', 'FixOSPtsPCS', 'TraSSPtsPCS', 'TraOSPtsPCS']
    Keys = ['TraSSPtsPCS', 'TraOSPtsPCS']
    
    # Initialise the new dictionary:
    ContourSweepData = {}
    
    # Loop through each key in Keys:
    for key in Keys:
        SweepAllNodes = LinkPointsAcrossContours(ContourData[key])
        
        # Update the dictionary:
        ContourSweepData.update({key : SweepAllNodes})
        
    
    return ContourSweepData
    
    
    
    


    
def GetLinePlaneIntersection(PlaneN, PlaneP, LineP0, LineP1, MustBeOnLineSeg):
    """ 
    Get the intersection between a line and a plane.
    
    Inputs:
        PlaneN          - A list of the [x, y, z] components of the plane's 
                          normal
                        
        PlaneP          - A list of the [x, y z] components of a point lying 
                          on the plane

        LineP0          - A list of the [x, y, z] components of a point lying
                          on the line
                        
        LineP1          - A list of the [x, y z] components of a point lying 
                          on the line
                        
        MustBeOnLineSeg - Boolean value that determines whether the 
                          intersection point must lie on the line segment 
                          (True) or not (False)
                        
    Returns:
        IntersP         - A list of the [x, y, z] components of the point 
                          that intersects the line and plane; or None
                        
        OnLineSegment   - Boolean value that indicates whether the intersection 
                          point lies on the line segment (True) or not (False)
    
    Code adapted from:
    https://stackoverflow.com/questions/5666222/3d-line-plane-intersection
    """
    
    epsilon=1e-6
        
    LineV = [LineP1[0] - LineP0[0],
             LineP1[1] - LineP0[1],
             LineP1[2] - LineP0[2]
             ]
    
    PlaneN_dot_LineV = PlaneN[0] * LineV[0] + \
                       PlaneN[1] * LineV[1] + \
                       PlaneN[2] * LineV[2]
    
    if abs(PlaneN_dot_LineV) < epsilon:
        raise RuntimeError("The line is parallel to the plane")
        return None
        
    PlaneLineV = [LineP0[0] - PlaneP[0],
                  LineP0[1] - PlaneP[1],
                  LineP0[2] - PlaneP[2]
                  ]
    
    PlaneN_dot_PlaneLineV = PlaneN[0] * PlaneLineV[0] + \
                            PlaneN[1] * PlaneLineV[1] + \
                            PlaneN[2] * PlaneLineV[2]
    
    factor = - PlaneN_dot_PlaneLineV / PlaneN_dot_LineV
    
    IntersP = [LineP0[0] + factor * LineV[0],
               LineP0[1] + factor * LineV[1],
               LineP0[2] + factor * LineV[2]
               ]
    
    if MustBeOnLineSeg and ( factor < 0 ) or ( factor > 1 ):
        # IntersP does not lie on the line segment.
        return None, None
        
    else:
        if ( factor < 0 ) or ( factor > 1 ):
            # The point does not lie on the line segment.
            return IntersP, False
        else: 
            # The point does lie on the line segment.
            return IntersP, True
        
        
        
        

def GetVectorPlaneIntersection(PlaneNorm, PlanePt, Point, Vector, 
                               MustBeOnLineSeg):
    """ 
    Get the intersection between a vector originating from a point and a plane.
    
    Inputs:
        PlaneNorm       - A list of the [x, y, z] components of the plane's 
                          normal
                        
        PlanePt         - A list of the [x, y z] components of a point lying 
                          on the plane

        Point           - A list of the [x, y, z] components of a point 
                        
        Vector          - A list of the [x, y z] components of a vector
                        
        MustBeOnLineSeg - Boolean value that determines whether the 
                          intersection point must lie on the line segment 
                          (True) or not (False)
                        
    Returns:
        IntersP         - A list of the [x, y, z] components of the point 
                          that intersects the plane (i.e. projection of a point
                          onto a plane with vector direction); or None
                        
        OnLineSegment   - Boolean value that indicates whether the intersection 
                          point lies on the line segment (True) or not (False)
    
    Adapted from GetLinePlaneIntersection to find the projection of a point
    in a contour onto a plane given the contour normal vector.
    """
    
    epsilon=1e-6
    
    PlaneNorm_dot_V = PlaneNorm[0] * Vector[0] + \
                      PlaneNorm[1] * Vector[1] + \
                      PlaneNorm[2] * Vector[2]
    
    if abs(PlaneNorm_dot_V) < epsilon:
        #print("The vector is parallel to the plane")
        raise RuntimeError("The vector is parallel to the plane")
        return None, None
        
    PlanePt_Pt_V = [Point[0] - PlanePt[0],
                    Point[1] - PlanePt[1],
                    Point[2] - PlanePt[2]
                    ]
    
    PlaneNorm_dot_PlanePt_Pt_V = PlaneNorm[0] * PlanePt_Pt_V[0] + \
                                 PlaneNorm[1] * PlanePt_Pt_V[1] + \
                                 PlaneNorm[2] * PlanePt_Pt_V[2]
    
    factor = - PlaneNorm_dot_PlanePt_Pt_V / PlaneNorm_dot_V
    
    IntersPt = [Point[0] + factor * Vector[0],
                Point[1] + factor * Vector[1],
                Point[2] + factor * Vector[2]
                ]
    
    #print(f'IntersPt = {IntersPt}; factor = {factor}\n')
    
    if MustBeOnLineSeg and ( factor < 0 ) or ( factor > 1 ):
        # IntersP does not lie on the line segment.
        return None, None
        
    else:
        if ( factor < 0 ) or ( factor > 1 ):
            # The point does not lie on the line segment.
            return IntersPt, False
        else: 
            # The point does lie on the line segment.
            return IntersPt, True
        
        
        
        



def GetDistanceFromPointToPlane(PlaneNorm, PlanePt, Pt):
    """ 
    Get the intersection between a line and a plane.
    
    Inputs:
        PlaneNorm - A list of the [x, y, z] components of the plane's normal
                        
        PlanePt   - A list of the [x, y z] components of a point lying on the 
                    plane

        Pt        - A list of the [x, y, z] components of a point
                        
                        
    Returns:
        Dist      - A float of the distance bewteen the point and the plane 
                        
    """
        
    # Vector from PlanePt to Pt:
    PtVect = [Pt[0] - PlanePt[0],
              Pt[1] - PlanePt[1],
              Pt[2] - PlanePt[2]
              ]
    
    # Dist is the projection of PtV onto PlaneNorm:
    Dist = PtVect[0] * PlaneNorm[0] + \
           PtVect[1] * PlaneNorm[1] + \
           PtVect[2] * PlaneNorm[2]
    
        
    return Dist



        
        
        

def GetIntersectingPointsInMovingPlanes(InterpData, MovingDicomDir, 
                                        UseInterp, MustBeOnLineSeg):
    """
    Get the list of intersection points of the lines that join each 
    over-sampled-to-interpolated contour #1 to each imaging plane, and likewise 
    for each interpolated-to-over-sampled contour #2.
    
    Inputs:
        InterpData      - A dictionary containing interpolated data.
        
        MovingDicomDir  - Directory containing the DICOMs for the Moving image
                          domain.
                         
        UseInterp       - Boolean that determines whether interpolated contours
                          will be used (True) when finding intersecting points
                          or not (False).
                         
        MustBeOnLineSeg - Boolean value that determines whether the 
                          intersection point must lie on the line segment 
                          (True) or not (False)
        
        
    Returns:
        MovContourData  - A dictionary containing the contour data belonging to
                          the Moving image domain.
                          
    """
    
    # Import packages and functions:
    from GetImageAttributes import GetImageAttributes
    #from PCStoICS import PCStoICS
    
    # Chose which package to use to get the Image Plane Attributes:
    #package = 'sitk'
    package = 'pydicom'
    
    # Get the Image Attributes for the Moving image:
    MovOrigin, MovDirs,\
    MovSpacings, MovDims = GetImageAttributes(DicomDir=MovingDicomDir, 
                                              Package=package)
    
    # The imaging plane normal:
    PlaneNormal = MovDirs[6:9]
    
    #print(f'Length of PlaneNormal is {GetVectorLength(PlaneNormal)}')
    
    # Initialise a list of contours consisting of the intersecting points 
    # for each imaging plane:
    #IntersContours = [[] for i in range(MovDims[2])]
    
    # Initialise the list of intersecting points for all planes:
    PtsAllPlanes = []
    
    PtsGroupedByPlane = [[] for i in range(MovDims[2])]
    
    # Loop through all imaging planes in Moving Image and get the intersecting
    # points of Point0->Point1 and Point1->Point2 with each plane:
    for k in range(MovDims[2]):
        print(f'\nPlane k = {k}')
        print('^^^^^^^^^^^^^^^')

        # Need a point lying on the plane - use the plane's origin:
        PlaneOrigin = [MovOrigin[0] + k*MovSpacings[2]*PlaneNormal[0], 
                       MovOrigin[1] + k*MovSpacings[2]*PlaneNormal[1], 
                       MovOrigin[2] + k*MovSpacings[2]*PlaneNormal[2]
                       ]
            
            
        # Initialise the list of intersecting points for this plane:
        PtsThisPlane = []
        
        # Loop through each trio of contours (i.e. each set of interpolation 
        # data in InterpData):
        for i in range(len(InterpData['InterpSliceInd'])):
            #print(f'\ni = {i}')
            print('\nInterpSliceInd =', InterpData['InterpSliceInd'][i])
            
            # Initialise the contour pairs for this set of interpolation data:
            ContourPairs = []
            
            if UseInterp:
                ContourPairs.append([InterpData['MovOSContour1Pts'][i],
                                     InterpData['MovInterpContourPts'][i]])
                
                ContourPairs.append([InterpData['MovInterpContourPts'][i],
                                     InterpData['MovOSContour2Pts'][i]])
            else:
                ContourPairs.append([InterpData['MovOSContour1Pts'][i],
                                     InterpData['MovOSContour2Pts'][i]])
            
            #print('ContourPairs =', ContourPairs, '\n')
            #print(f'len(ContourPairs) = {len(ContourPairs)}\n')
            
            # Initialise the list of intersecting points for all contour pairs:
            PtsAllContourPairs = []
                
            # Loop through each contour pair:
            """ Note: There are 2 contour pairs if UseInterp is True, 
            and 1 if False. """
            for j in range(len(ContourPairs)):
                # Initialise the list of intersecting points for this contour 
                # pair:
                PtsThisContourPair = []
                
                # The number of points in the first contour pair (all contours 
                # have the same number of points):
                P = len(ContourPairs[j][0])
                
                # Loop through each point in the contours:
                for p in range(P):
                    # Point0 is the p^th point in the first (0^th) contour in 
                    # ContourPairs, and Point1 is the p^th point in the second 
                    # (1^st) contour:
                    Point0 = ContourPairs[j][0][p]
                    Point1 = ContourPairs[j][1][p]

                    IntersPoint, \
                    OnLineSeg = GetLinePlaneIntersection(PlaneN=PlaneNormal, 
                                                         PlaneP=PlaneOrigin,
                                                         LineP0=Point0,
                                                         LineP1=Point1,
                                                         MustBeOnLineSeg=MustBeOnLineSeg)
                    
                    # Append IntersPoint to InterPtsThisContourPair if 
                    # IntersPoint is not None: 
                    if IntersPoint:
                        PtsThisContourPair.append(IntersPoint)
                        
                if PtsThisContourPair:
                    print(f'\n   Contour pair no {j + 1}:')
                    print(f'      There were {P} points in these contours.')
                    print(f'      There were {len(PtsThisContourPair)} intersection points found.')
                        
                # Append PtsThisContourPair to PtsAllContourPairs:
                PtsAllContourPairs.append(PtsThisContourPair)
                
                # Append PtsThisContourPair to PtsGroupedByPlane for this k: 
                PtsGroupedByPlane[k].append(PtsThisContourPair)
                
            # Append PtsAllContourPairs to PtsThisPlane:
            PtsThisPlane.append(PtsAllContourPairs)

        # Append PtsThisPlane to PtsAllPlanes:
        PtsAllPlanes.append(PtsThisPlane)
    
    
    # Create dictionary MovContourData with intersection points as lists of 
    # list of points for each slice but without [] lists (as in 
    # PtsGroupedByPlane):
    MovContourData = CreateMovContourData(PtsGroupedByPlane, MovOrigin, 
                                          MovDirs, MovSpacings, MovDims)
    
    #return PtsAllPlanes, PtsGroupedByPlane
    return MovContourData
                



def CreateMovContourData(PtsGroupedByPlane, MovOrigin, MovDirs, MovSpacings, MovDims):
    # Import packages and functions:
    #from GetImageAttributes import GetImageAttributes
    from PCStoICS import PCStoICS
    
    # Initialise a list of all intersection points for all slices without []s 
    # in the Patient Coordinate System, and for the Image Coordinate System:
    PtsAllSlicesPCS = []
    PtsAllSlicesICS = []
    ContourTypeAllSlices = []
        
    
    # Loop through each slice in PtsGroupedByPlane:
    for k in range(MovDims[2]):
        # Initialise a list of all intersection points for this slice without []s
        # in the Patient Coordinate System, and for the Image Coordinate System:
        PtsThisSlicePCS = []
        PtsThisSliceICS = []
        ContourType = 0

        # Loop through each list:
        for i in range(len(PtsGroupedByPlane[k])):
            # Append lists that are not empty:
            if PtsGroupedByPlane[k][i]:
                PtsThisSlicePCS.append(PtsGroupedByPlane[k][i])
                
                PtsThisSliceICS.append(PCStoICS(Pts_PCS=PtsGroupedByPlane[k][i],
                                                Origin=MovOrigin, 
                                                Directions=MovDirs, 
                                                Spacings=MovSpacings))
                
                ContourType = 3
                
        
        PtsAllSlicesPCS.append(PtsThisSlicePCS)
        
        PtsAllSlicesICS.append(PtsThisSliceICS)
        
        ContourTypeAllSlices.append(ContourType)
        
        
    
    # Create a list of slice numbers:
    SliceNo = list(range(MovDims[2]))
    
    MovContourData = {
                      'SliceNo'        : SliceNo, 
                      'ContourType'    : ContourTypeAllSlices,
                      'PointPCS'       : PtsAllSlicesPCS,
                      'PointICS'       : PtsAllSlicesICS
                       }
    
    
    return MovContourData





def GetIntersectingPtsFromContourSweepData(ContourSweepData, Method,
                                           MustBeOnLineSeg, MaxDistToPts,
                                           MovingDicomDir, ContourData):
    """
    Get the list of intersection points of the "sweep curves" and the image
    planes.  The "sweep curves" are the curves formed by joining any given
    node to the same corresponding node in the other contours.
    
    At the moment the intersection points will be found both for the 
    transformed super-sampled contours ('TraSSPtsPCS') and the transformed
    over-sampled contours ('TraOSPtsPCS'). One could be omitted at a later date 
    if the other is deemed less useful.
    
    Inputs:
        ContourSweepData - Dictionary containing the list of points [x, y, z]
                           that link any given node in each contour, for all
                           nodes.
        
        Method           - String that determines how the intersection points 
                           are found.  Acceptable inputs are:
                               'linear':
                                
                                   The intersection of each line segment that 
                                   links every pair of adjacent nodes along a 
                                   sweep "curve" and all image planes.
                                   
                               'cubic':
                                   
                                   The intersection of the cubic fit of the
                                   sweep "curve" and all image planes.
                           
        MovingDicomDir   - Directory containing the DICOMs for the Moving image
                           domain.
                           
        ContourData      - Dictionary containing a list of contour points 
                           [x, y, z] arranged along rows for each DICOM slice,  
                           and along columns for different contours (i.e. a  
                           list of lists of lists). Slices without contours 
                           have empty list ([]).
      
        
    Returns:
        ContourData      - As above but with added entries for intersection 
                           points. 
                          
    """
    
    # Decide whether the intersection point must lie on the line segment:
    #MustBeOnLineSeg = True
    #MustBeOnLineSeg = False
    
    # Decide on the maximum z-distance between the plane and either of the two
    # points that define the line segment:
    #MaxDistToPts = 5
    
    
    # Import packages and functions:
    from GetImageAttributes import GetImageAttributes
    #from PCStoICS import PCStoICS
    
    # Chose which package to use to get the Image Plane Attributes:
    #package = 'sitk'
    package = 'pydicom'
    
    # Get the Image Attributes for the Moving image:
    MovOrigin, MovDirs,\
    MovSpacings, MovDims = GetImageAttributes(DicomDir=MovingDicomDir, 
                                              Package=package)
    
    # The imaging plane normal:
    PlaneNormal = MovDirs[6:9]
    
    #print(f'Length of PlaneNormal is {GetVectorLength(PlaneNormal)}')
    
    # Initialise a list of contours consisting of the intersecting points 
    # for each imaging plane:
    #IntersContours = [[] for i in range(MovDims[2])]
    
    # Initialise the list of intersecting points for all planes:
    #PtsAllPlanes = []
    
    #PtsGroupedByPlane = [[] for i in range(MovDims[2])]
    
    
    # The keys in ContourSweepData to loop through:
    KeysIn = ['TraSSPtsPCS', 'TraOSPtsPCS']
    
    for key in KeysIn:
        
        SweepData = ContourSweepData[key]
        
        # The number of sweep curves (= number of Points in each contour):
        P = len(SweepData)
        
        # The number of points in each sweep (= the number of Contours):
        C = len(SweepData[0])
        
        # Initialise the list of intersection points grouped by plane:
        PtsGroupedByPlane = []
        
        # Initialise the list of contour type numbers:
        MovContourType = []
        
        # Loop through all imaging planes:
        for k in range(MovDims[2]):
            print(f'\nPlane k = {k}')
            print('^^^^^^^^^^^^^^^')
    
            # Need a point lying on the plane - use the plane's origin:
            PlaneOrigin = [MovOrigin[0] + k*MovSpacings[2]*PlaneNormal[0], 
                           MovOrigin[1] + k*MovSpacings[2]*PlaneNormal[1], 
                           MovOrigin[2] + k*MovSpacings[2]*PlaneNormal[2]
                           ]
                
                
            # Initialise the list of intersecting points for all contour pairs:
            PtsGroupedByContourPair = []
            
            # Initialise the list of the number of intersection points for all
            # contour pairs:
            NumPtsGroupedByContourPair = []
            
            # Loop through each pair of contours:
            for c in range(C - 1):
                #print(f'\nc = {c}')
                
                # Initialise the list of intersecting points for this pair of
                # contours:
                PtsThisContourPair = []
                NumPtsThisContourPair = 0
                    
                # Loop through each point:
                for p in range(P):
                    # Point0 is the p^th point in the c^th contour, and Point1 
                    # is the p^th point in the (c+1)^th contour:
                    Point0 = SweepData[p][c]
                    Point1 = SweepData[p][c+1]

                    IntersPoint, \
                    OnLineSeg = GetLinePlaneIntersection(PlaneN=PlaneNormal, 
                                                         PlaneP=PlaneOrigin,
                                                         LineP0=Point0,
                                                         LineP1=Point1,
                                                         MustBeOnLineSeg=MustBeOnLineSeg)
                    
                    # Append IntersPoint to InterPtsThisContourPair if 
                    # IntersPoint is not None: 
                    if IntersPoint:
                        if MustBeOnLineSeg:
                            PtsThisContourPair.append(IntersPoint)
                            
                        else:
                            # Find the z-distance of IntersPoint and Point0 and
                            # Point1:
                            Dist1 = abs(IntersPoint[2] - Point0[2])
                            Dist2 = abs(IntersPoint[2] - Point1[2])
                            
                            #print(f'Dist1 = {Dist1}, Dist2 = {Dist2}')
                            
                            if (Dist1 < MaxDistToPts) or (Dist2 < MaxDistToPts):
                                print(f'Dist1 = {Dist1}, Dist2 = {Dist2}')
                                
                                PtsThisContourPair.append(IntersPoint)
                                
                        # Increment NumPtsThisContourPair:
                        NumPtsThisContourPair += 1
                        
                if PtsThisContourPair:
                    print(f'\n   Contour pair no {c}:')
                    print(f'      There were {P} points in these contours.')
                    print(f'      There were {len(PtsThisContourPair)} intersection points found.')
                        
                # Append PtsThisContourPair to PtsGroupedByContourPair:
                """ 
                Ensure that the every pair of contours has a resulting list of
                intersection point(s) - even if there's only one point 
                (e.g. [ [x,y,z] ]). 
                """
                if NumPtsThisContourPair == 1:
                    PtsGroupedByContourPair.append([PtsThisContourPair])
                    NumPtsGroupedByContourPair.append(1)
                else:
                    PtsGroupedByContourPair.append(PtsThisContourPair)
                    NumPtsGroupedByContourPair.append(len(PtsThisContourPair))
                
                ## Append PtsThisContourPair to PtsGroupedByPlane for this k: 
                #PtsGroupedByPlane[k].append(PtsThisContourPair)
                
            
            # If there were no intersection points for all contour pairs 
            # PtsGroupedByContourPair may be a list of empty lists 
            # (e.g. [ [], [], [], [] ]).  If so, reduce the list to a flat
            # empty list:
            if sum(NumPtsGroupedByContourPair) == 0:
                PtsGroupedByContourPair = []
                
                MovContourType.append(0)
                
            else:
                MovContourType.append(1)
            
            # Append PtsGroupedByContourPair to PtsGroupedByPlane:
            PtsGroupedByPlane.append(PtsGroupedByContourPair)

        
        
        # Add MovContourType to ContourData (this need only be done once):
        if key == KeysIn[0]:
            ContourData.update({'MovContourType' : MovContourType})
        
        
        # Add the intersection points to ContourData (as 'MovSSPtsPCS' and 
        # 'MovOSPtsPCS' since they lie in the Moving image planes):
        # The key that will be added to ContourData:
        KeyOut = key.replace('Tra', 'Mov')
        
        ContourData.update({KeyOut : PtsGroupedByPlane})
        
        
        # Equate the lengths of the items in ContourData since there may be 
        # more slices in the Fixed/Moving image stack than in Moving/Fixed:
        ContourData = EquateListLengthsInContourData(ContourData)
    
    return ContourData







def GetIntersectingPtsFromContourSweepData2(ContourSweepData, MustBeOnLineSeg, 
                                            MaxDistToPts, ContourData):
    """
    Get the list of intersection points of the "sweep curves" and the image
    planes.  The "sweep curves" are the curves formed by joining any given
    node to the same corresponding node in the other contours.
    
    At the moment the intersection points will be found both for the 
    transformed super-sampled contours ('TraSSPtsPCS') and the transformed
    over-sampled contours ('TraOSPtsPCS'). One could be omitted at a later date 
    if the other is deemed less useful.
    
    This function is adapted from GetIntersectingPtsFromContourSweepData, which
    has the additional input 'MovingDicomDir', which is an input to 
    GetImageAttributes.  The function GetImageAttributes imports SimpleElastix,
    so this function (GetIntersectingPtsFromContourSweepData2) instead will 
    search for the files 'MovOrigin.json', 'MovDirs.json', 'MovSpacings.json'
    and 'MovDims.json' in the current working directory.
    
    Inputs:
        ContourSweepData - Dictionary containing the list of points [x, y, z]
                           that link any given node in each contour, for all
                           nodes.
                           
        ContourData      - Dictionary containing a list of contour points 
                           [x, y, z] arranged along rows for each DICOM slice,  
                           and along columns for different contours (i.e. a  
                           list of lists of lists). Slices without contours 
                           have empty list ([]).
      
        
    Returns:
        ContourData      - As above but with added entries for intersection 
                           points. 
                          
    """
    
    # Decide whether the intersection point must lie on the line segment:
    #MustBeOnLineSeg = True
    #MustBeOnLineSeg = False
    
    # Decide on the maximum z-distance between the plane and either of the two
    # points that define the line segment:
    #MaxDistToPts = 5
    
    
    # Import packages and functions:
    #from GetImageAttributes import GetImageAttributes
    #from PCStoICS import PCStoICS
    from ImportImageAttributesFromJson import ImportImageAttributesFromJson as ImportImAtt

    # Get the image attributes for the Moving image:
    MovOrigin, MovDirs, MovSpacings, MovDims = ImportImAtt(FilePrefix='Mov')

    
    # The imaging plane normal:
    PlaneNormal = MovDirs[6:9]
    
    #print(f'Length of PlaneNormal is {GetVectorLength(PlaneNormal)}')
    
    # Initialise a list of contours consisting of the intersecting points 
    # for each imaging plane:
    #IntersContours = [[] for i in range(MovDims[2])]
    
    # Initialise the list of intersecting points for all planes:
    #PtsAllPlanes = []
    
    #PtsGroupedByPlane = [[] for i in range(MovDims[2])]
    
    
    # The keys in ContourSweepData to loop through:
    KeysIn = ['TraSSPtsPCS', 'TraOSPtsPCS']
    
    for key in KeysIn:
        
        SweepData = ContourSweepData[key]
        
        # The number of sweep curves (= number of Points in each contour):
        P = len(SweepData)
        
        # The number of points in each sweep (= the number of Contours):
        C = len(SweepData[0])
        
        # Initialise the list of intersection points grouped by plane:
        PtsGroupedByPlane = []
        
        # Initialise the list of contour type numbers:
        MovContourType = []
        
        # Loop through all imaging planes:
        for k in range(MovDims[2]):
            print(f'\nPlane k = {k}')
            print('^^^^^^^^^^^^^^^')
    
            # Need a point lying on the plane - use the plane's origin:
            PlaneOrigin = [MovOrigin[0] + k*MovSpacings[2]*PlaneNormal[0], 
                           MovOrigin[1] + k*MovSpacings[2]*PlaneNormal[1], 
                           MovOrigin[2] + k*MovSpacings[2]*PlaneNormal[2]
                           ]
                
                
            # Initialise the list of intersecting points for all contour pairs:
            PtsGroupedByContourPair = []
            
            # Initialise the list of the number of intersection points for all
            # contour pairs:
            NumPtsGroupedByContourPair = []
            
            # Loop through each pair of contours:
            for c in range(C - 1):
                #print(f'\nc = {c}')
                
                # Initialise the list of intersecting points for this pair of
                # contours:
                PtsThisContourPair = []
                NumPtsThisContourPair = 0
                    
                # Loop through each point:
                for p in range(P):
                    # Point0 is the p^th point in the c^th contour, and Point1 
                    # is the p^th point in the (c+1)^th contour:
                    Point0 = SweepData[p][c]
                    Point1 = SweepData[p][c+1]

                    IntersPoint, \
                    OnLineSeg = GetLinePlaneIntersection(PlaneN=PlaneNormal, 
                                                         PlaneP=PlaneOrigin,
                                                         LineP0=Point0,
                                                         LineP1=Point1,
                                                         MustBeOnLineSeg=MustBeOnLineSeg)
                    
                    # Append IntersPoint to InterPtsThisContourPair if 
                    # IntersPoint is not None: 
                    if IntersPoint:
                        if MustBeOnLineSeg:
                            PtsThisContourPair.append(IntersPoint)
                            
                        else:
                            # Find the z-distance of IntersPoint and Point0 and
                            # Point1:
                            Dist1 = abs(IntersPoint[2] - Point0[2])
                            Dist2 = abs(IntersPoint[2] - Point1[2])
                            
                            #print(f'Dist1 = {Dist1}, Dist2 = {Dist2}')
                            
                            if (Dist1 < MaxDistToPts) or (Dist2 < MaxDistToPts):
                                print(f'Dist1 = {Dist1}, Dist2 = {Dist2}')
                                
                                PtsThisContourPair.append(IntersPoint)
                                
                        # Increment NumPtsThisContourPair:
                        NumPtsThisContourPair += 1
                        
                if PtsThisContourPair:
                    print(f'\n   Contour pair no {c}:')
                    print(f'      There were {P} points in these contours.')
                    print(f'      There were {len(PtsThisContourPair)} intersection points found.')
                        
                # Append PtsThisContourPair to PtsGroupedByContourPair:
                """ 
                Ensure that the every pair of contours has a resulting list of
                intersection point(s) - even if there's only one point 
                (e.g. [ [x,y,z] ]). 
                """
                if NumPtsThisContourPair == 1:
                    PtsGroupedByContourPair.append([PtsThisContourPair])
                    NumPtsGroupedByContourPair.append(1)
                else:
                    PtsGroupedByContourPair.append(PtsThisContourPair)
                    NumPtsGroupedByContourPair.append(len(PtsThisContourPair))
                
                ## Append PtsThisContourPair to PtsGroupedByPlane for this k: 
                #PtsGroupedByPlane[k].append(PtsThisContourPair)
                
            
            # If there were no intersection points for all contour pairs 
            # PtsGroupedByContourPair may be a list of empty lists 
            # (e.g. [ [], [], [], [] ]).  If so, reduce the list to a flat
            # empty list:
            if sum(NumPtsGroupedByContourPair) == 0:
                PtsGroupedByContourPair = []
                
                MovContourType.append(0)
                
            else:
                MovContourType.append(1)
            
            # Append PtsGroupedByContourPair to PtsGroupedByPlane:
            PtsGroupedByPlane.append(PtsGroupedByContourPair)

        
        
        # Add MovContourType to ContourData (this need only be done once):
        if key == KeysIn[0]:
            ContourData.update({'MovContourType' : MovContourType})
        
        
        # Add the intersection points to ContourData (as 'MovSSPtsPCS' and 
        # 'MovOSPtsPCS' since they lie in the Moving image planes):
        # The key that will be added to ContourData:
        KeyOut = key.replace('Tra', 'Mov')
        
        ContourData.update({KeyOut : PtsGroupedByPlane})
        
        
        # Equate the lengths of the items in ContourData since there may be 
        # more slices in the Fixed/Moving image stack than in Moving/Fixed:
        ContourData = EquateListLengthsInContourData(ContourData)
    
    return ContourData






def GetIntersectingPtsFromContourSweepData_v3(ContourSweepData, ContourData):
    """
    Get the list of intersection points of the "sweep curves" and the image
    planes.  The "sweep curves" are the curves formed by joining any given
    node to the same corresponding node in the other contours.
    
    At the moment the intersection points will be found both for the 
    transformed super-sampled contours ('TraSSPtsPCS') and the transformed
    over-sampled contours ('TraOSPtsPCS'). One could be omitted at a later date 
    if the other is deemed less useful.
    
    This function is adapted from GetIntersectingPtsFromContourSweepData2, which
    has the additional input 'MovingDicomDir', which is an input to 
    GetImageAttributes.  The function GetImageAttributes imports SimpleElastix,
    so this function (GetIntersectingPtsFromContourSweepData2) instead will 
    search for the files 'MovOrigin.json', 'MovDirs.json', 'MovSpacings.json'
    and 'MovDims.json' in the current working directory.
    
    Inputs:
        ContourSweepData - Dictionary containing the list of points [x, y, z]
                           that link any given node in each contour, for all
                           nodes.
                           
        ContourData      - Dictionary containing a list of contour points 
                           [x, y, z] arranged along rows for each DICOM slice,  
                           and along columns for different contours (i.e. a  
                           list of lists of lists). Slices without contours 
                           have empty list ([]).
      
        
    Returns:
        ContourData      - As above but with added entries for intersection 
                           points. 
                           
                           
    Note:
        Comparison with GetIntersectingPtsFromContourSweepData2: Rather than
        defining MustBeOnLineSeg and MaxDistToPts, all intersection points with
        all planes will be found, and OnLineSeg.  Then all intersection points
        for which OnLineSeg = False other than the first intersection on either
        side of the cluster of intersection points for which OnLineSeg = True
        will be discarded.
                          
    """
    
    # Import packages and functions:
    #from GetImageAttributes import GetImageAttributes
    #from PCStoICS import PCStoICS
    from ImportImageAttributesFromJson import ImportImageAttributesFromJson as ImportImAtt

    # Get the image attributes for the Moving image:
    MovOrigin, MovDirs, MovSpacings, MovDims = ImportImAtt(FilePrefix='Mov')

    
    # The imaging plane normal:
    PlaneNormal = MovDirs[6:9]
    
    #print(f'Length of PlaneNormal is {GetVectorLength(PlaneNormal)}')
    
    # Initialise a list of contours consisting of the intersecting points 
    # for each imaging plane:
    #IntersContours = [[] for i in range(MovDims[2])]
    
    # Initialise the list of intersecting points for all planes:
    #PtsAllPlanes = []
    
    #PtsGroupedByPlane = [[] for i in range(MovDims[2])]
    
    
    # The keys in ContourSweepData to loop through:
    KeysIn = ['TraSSPtsPCS', 'TraOSPtsPCS']
    
    for key in KeysIn:
        
        SweepData = ContourSweepData[key]
        
        # The number of sweep curves (= number of Points in each contour):
        P = len(SweepData)
        
        # The number of points in each sweep (= the number of Contours):
        C = len(SweepData[0])
        
        # Initialise the list of intersection points grouped by plane:
        PtsGroupedByPlane = []
        OLSGroupedByPlane = []
        
        # Initialise the list of contour type numbers:
        MovContourType = []
        
        # Loop through all imaging planes:
        for k in range(MovDims[2]):
            print(f'\nPlane k = {k}')
            print('^^^^^^^^^^^^^^^')
    
            # Need a point lying on the plane - use the plane's origin:
            PlaneOrigin = [MovOrigin[0] + k*MovSpacings[2]*PlaneNormal[0], 
                           MovOrigin[1] + k*MovSpacings[2]*PlaneNormal[1], 
                           MovOrigin[2] + k*MovSpacings[2]*PlaneNormal[2]
                           ]
                
                
            # Initialise the list of intersecting points for all contour pairs:
            PtsGroupedByContourPair = []
            OLSGroupedByContourPair = []
            
            # Initialise the list of the number of intersection points for all
            # contour pairs:
            NumPtsGroupedByContourPair = []
            
            # Loop through each pair of contours:
            for c in range(C - 1):
                #print(f'\nc = {c}')
                
                # Initialise the list of intersecting points for this pair of
                # contours:
                PtsThisContourPair = []
                OLSThisContourPair = []
                NumPtsThisContourPair = 0
                    
                # Loop through each point:
                for p in range(P):
                    # Point0 is the p^th point in the c^th contour, and Point1 
                    # is the p^th point in the (c+1)^th contour:
                    Point0 = SweepData[p][c]
                    Point1 = SweepData[p][c+1]

                    IntersPoint, \
                    OnLineSeg = GetLinePlaneIntersection(PlaneN=PlaneNormal, 
                                                         PlaneP=PlaneOrigin,
                                                         LineP0=Point0,
                                                         LineP1=Point1,
                                                         MustBeOnLineSeg='False')
                    
                    # Append IntersPoint to InterPtsThisContourPair if 
                    # IntersPoint is not None: 
                    if IntersPoint:
                        PtsThisContourPair.append(IntersPoint)
                        OLSThisContourPair.append(OnLineSeg)
                            
                        # Increment NumPtsThisContourPair:
                        NumPtsThisContourPair += 1
                        
                if PtsThisContourPair:
                    print(f'\n   Contour pair no {c}:')
                    print(f'      There were {P} points in these contours.')
                    print(f'      There were {len(PtsThisContourPair)} intersection points found.')
                    
                        
                # Append PtsThisContourPair to PtsGroupedByContourPair:
                """ 
                Ensure that the every pair of contours has a resulting list of
                intersection point(s) - even if there's only one point 
                (e.g. [ [x,y,z] ]). 
                """
                if NumPtsThisContourPair == 1:
                    PtsGroupedByContourPair.append([PtsThisContourPair])
                    OLSGroupedByContourPair.append([OLSThisContourPair])
                    NumPtsGroupedByContourPair.append(1)
                else:
                    PtsGroupedByContourPair.append(PtsThisContourPair)
                    OLSGroupedByContourPair.append(OLSThisContourPair)
                    NumPtsGroupedByContourPair.append(len(PtsThisContourPair))
                
                ## Append PtsThisContourPair to PtsGroupedByPlane for this k: 
                #PtsGroupedByPlane[k].append(PtsThisContourPair)
                
            
            # If there were no intersection points for all contour pairs 
            # PtsGroupedByContourPair may be a list of empty lists 
            # (e.g. [ [], [], [], [] ]).  If so, reduce the list to a flat
            # empty list:
            if sum(NumPtsGroupedByContourPair) == 0:
                PtsGroupedByContourPair = []
                OLSGroupedByContourPair = []
                
                MovContourType.append(0)
                
            else:
                MovContourType.append(1)
            
            # Append PtsGroupedByContourPair to PtsGroupedByPlane:
            PtsGroupedByPlane.append(PtsGroupedByContourPair)
            OLSGroupedByPlane.append(OLSGroupedByContourPair)

        
        # 21/09:
        # Get the index of the first slice that contains 
        
        
        
        
        # Add MovContourType to ContourData (this need only be done once):
        if key == KeysIn[0]:
            ContourData.update({'MovContourType' : MovContourType})
        
        
        # Add the intersection points to ContourData (as 'MovSSPtsPCS' and 
        # 'MovOSPtsPCS' since they lie in the Moving image planes):
        # The key that will be added to ContourData:
        KeyPtsOut = key.replace('Tra', 'Mov')
        KeyOLSOut = KeyPtsOut.replace('PtsPCS', 'OLS')
        
        ContourData.update({KeyPtsOut : PtsGroupedByPlane})
        ContourData.update({KeyOLSOut : OLSGroupedByPlane})
        
        
        # Equate the lengths of the items in ContourData since there may be 
        # more slices in the Fixed/Moving image stack than in Moving/Fixed:
        ContourData = EquateListLengthsInContourData(ContourData)
    
    return ContourData






def NormOfTransformedFixedPlanes(FixOrigin, FixDirs, FixSpacings, FixDims, 
                                 MovIm, ElastixImFilt):
    """ Compute the unit normal vector of the transformed Fixed planes (which
    are the planes that the transformed contours will lie in), and hence, the
    unit normal of the transformed contours.
    
    Inputs:
        FixOrigin     - The ImagePositionPatient (pydicom) for the Fixed image
                        stack
                
                        e.g. [x0, y0, z0]
    
        FixDirs       - The direction cosine along x (rows), y (columns) and 
                        z (slices) for the Fixed image stack
                     
                        e.g. [Xx, Xy, Xz, Yx, Yy, Yz, Zx, Zy, Zz]
                    
                        SimpleITK returns all returns all direction cosines.
                        For pydicom, the cross product of the x and y vectors 
                        are used to obtain the z vector.
        
        FixSpacings   - The pixel spacings along x, y and z for the Fixed image
                        stack
        
                        e.g. [di, dj, dk]
                    
                        SimpleITK returns all pixel spacings.
                        For pydicom, the SliceThickness is added to the 
                        PixelSpacing.
                    
        FixDims       - The dimensions of the Fixed image stack
        
        MovIm         - The SimpleITK 3D image
        
        ElastixImFilt - The SimpleITK image transform filter (used for image
                        registration)
        
    Outputs:
        TraNorm       - The unit normal vector for the transformed planes/
                        contours

    """
    from ContourPlottingFuncs import GetPointsInImagePlanes_v2
    from TransformPoints import TransformPoints
    from ParseTransformixOutput import ParseTransformixOutput
    
        
    # Generate a list of points in the Fixed planes:
    PlanesPts = GetPointsInImagePlanes_v2(Origin=FixOrigin, Dirs=FixDirs, 
                                          Spacings=FixSpacings, Dims=FixDims)
    
    # The origin for the last plane:
    LastPlaneOrig = PlanesPts[-1][0]
    
    # The points to transform are the origins of the first plane (SourceOrigin)
    # and the last plane::
    InPts = [FixOrigin, LastPlaneOrig]
    
    # Transform InPts:
    TransformPoints(Points=InPts, Image=MovIm, TransformFilter=ElastixImFilt)
    
    # Parse outputpoints.txt:
    PtNos, FixInds, FixPts,\
    FixOutInds, MovPts,\
    Defs, MovInds = ParseTransformixOutput()
    
    # The z-vector between the origins at the last and first planes:
    Zvect = [MovPts[1][0] - MovPts[0][0],
             MovPts[1][1] - MovPts[0][1],
             MovPts[1][2] - MovPts[0][2]
             ]
    
    ZvectL = GetVectorLength(MovPts[0], MovPts[1])
    
    # Normalise Zvect (get the normal unit vector):
    TraNorm = [Zvect[0] / ZvectL,
               Zvect[1] / ZvectL,
               Zvect[2] / ZvectL
               ]
    
    return TraNorm






def GetProjectionOfContourPtsOnPlanes(ContourPts,
                                      FixOrigin, FixDirs, FixSpacings, FixDims, 
                                      MovOrigin, MovDirs, MovSpacings, MovDims,
                                      MovIm, ElastixImFilt, LogToConsole):
    """ Get the projection of the points in a contour onto the Moving image 
    planes.
    
    Inputs:
        ContourPts     - A list of the list of [x, y, z] coordinates that make 
                         up a contour
                        
        FixOrigin      - The ImagePositionPatient (pydicom) for the Fixed image
                         stack
                
                         e.g. [x0, y0, z0]
    
        FixDirs        - The direction cosine along x (rows), y (columns) and 
                         z (slices) for the Fixed image stack
                     
                         e.g. [Xx, Xy, Xz, Yx, Yy, Yz, Zx, Zy, Zz]
                    
                         SimpleITK returns all returns all direction cosines.
                         For pydicom, the cross product of the x and y vectors 
                         are used to obtain the z vector.
        
        FixSpacings    - The pixel spacings along x, y and z for the Fixed image
                         stack
        
                         e.g. [di, dj, dk]
                    
                         SimpleITK returns all pixel spacings.
                         For pydicom, the SliceThickness is added to the 
                         PixelSpacing.
                    
        FixDims        - The dimensions of the Fixed image stack
        
        MovOrigin      - The ImagePositionPatient (pydicom) for the Moving image
                         stack
    
        MovDirs        - The direction cosine along x (rows), y (columns) and 
                         z (slices) for the Moving image stack
        
        MovSpacings    - The pixel spacings along x, y and z for the Moving 
                         image stack
                    
        MovDims        - The dimensions of the Moving image stack
        
        MovIm          - The SimpleITK 3D image
        
        ElastixImFilt  - The SimpleITK image transform filter (used for image
                         registration)
        
        LogToConsole   - Log some results to the console.
        
    Outputs:
        ProjPtsByPlane - A list (by plane/slice index) of a list (by contours)
                         of a list of [x, y, z] coordinates of the projection/
                         intersection of ContourPts and the Moving image 
                         planes. 
                         
                         
                         
    Note 23/09/20:
        At the moment ContourPts must be a list of points, so each non-empty
        list in ProjPtsByPlane will have a single sub-list (= 1 contour), 
        containing a sub-list of the intersection/projected points.

    """
    
    
    # Work out the unit normal vector of the transformed image planes
    # (i.e. the unit normal vector of the transformed contours):
    TraNorm = NormOfTransformedFixedPlanes(FixOrigin, FixDirs, FixSpacings, 
                                           FixDims, MovIm, ElastixImFilt)
    
    # The number of contour points:
    P = len(ContourPts)

    # Initialise lists of the projected points (ProjPts), OnLineSegs, and
    # projected points grouped by slice (ProjPtsByPlane)::
    ProjPts = []
    OnLineSegs = []
    ProjPtsByPlane = [[] for i in range(MovDims[2])]
    
    # Loop through all points:
    for p in range(P):
        point = ContourPts[p]
        
        # Initialise the list of distances and absolute distances for this p:
        Dists = []
        AbsDists = []
        
        # Loop through all Moving image planes:
        for k in range(MovDims[2]):
    
            # Need a point lying on the plane - use the plane's origin:
            PlaneOrig = [MovOrigin[0] + k*MovSpacings[2]*MovDirs[6], 
                         MovOrigin[1] + k*MovSpacings[2]*MovDirs[7], 
                         MovOrigin[2] + k*MovSpacings[2]*MovDirs[8]
                         ]
    
            dist = GetDistanceFromPointToPlane(PlaneNorm=MovDirs[6:9], 
                                               PlanePt=PlaneOrig, 
                                               Pt=point)
            
            Dists.append(dist)
            AbsDists.append(abs(dist))
            
    
        # The index of the closest plane:
        ind = AbsDists.index(min(AbsDists))
    
        if LogToConsole:
            print(f'Point {p} is closest to Plane {ind} with distance',
                  f'{Dists[ind]} mm')
        
        # The plane origin for the closest plane:
        PlaneOrig = [MovOrigin[0] + ind*MovSpacings[2]*MovDirs[6], 
                     MovOrigin[1] + ind*MovSpacings[2]*MovDirs[7], 
                     MovOrigin[2] + ind*MovSpacings[2]*MovDirs[8]
                     ]
        
        # Get the intersection point between the point and the closest Moving
        # plane:
        IntersPt, OnLineSeg = GetVectorPlaneIntersection(PlaneNorm=MovDirs[6:9], 
                                                         PlanePt=PlaneOrig, 
                                                         Point=point, 
                                                         Vector=TraNorm, 
                                                         MustBeOnLineSeg=False)
        
        ProjPts.append(IntersPt)
        OnLineSegs.append(OnLineSeg)
        
        if IntersPt:
            ProjPtsByPlane[ind].append(IntersPt)
        
        if LogToConsole:
            print(f'The intersection point {IntersPt} and OnLineSeg = {OnLineSeg}\n')
    
    
    if LogToConsole:
        # The number of points that did not have an intersection point:
        NumNone = ProjPts.count(None)
        
        PercentNone = round(100*ProjPts.count(None)/P, 1)
        
        print(f'{NumNone} out of {P} points ({PercentNone} %) did not have',
              'intersection points')
        
        
    # Convert ProjPtsByPlane into a nested list of lists (for compatibility
    # with other functions):
    for k in range(MovDims[2]):
        if ProjPtsByPlane[k]:
            ProjPtsByPlane[k] = [ProjPtsByPlane[k]]
    
        
    return ProjPtsByPlane





def FlattenListOfPts(ListOfPts):
    """ 
    Flatten a list of points of the form [[x0, y0, z0], [x1, y1, z1], ...] to
    the form [x0, y0, z0, x1, y1, z1, ...] (matching the form required of
    ContourData in an ROI Collection).
    
    Inputs:
        ListOfPts    - A list of a list of [x, y, z] coordinates
        
    Outputs:
        ListOfCoords - A list of [x, y, z] coordinates flattened from ListOfPts
    """
    # Initialise the flattened list:
    ListOfCoords = []
    
    for point in ListOfPts:
        # Initialise the list of coordinates for this point:
        coords = []
        
        # Loop through each coordinate:
        for coord in point:
            # Convert the coordinate to a string and extend coords:
            coords.append(str(coord))
        
        ListOfCoords.extend(coords)
            
    return ListOfCoords






def EquateListLengthsInDictionary(Dictionary):
    """ Equate the number of values (length of list per key) in a dictionary.
    
    Inputs:
        Dictionary - Dictionary with unequal number of values.
        
    Outputs:
        Dictionary - As above but with [] added to entries of shorter lists.

    """
    
    Keys = list(Dictionary.keys())
    
    Lengths = []
    
    for key, value in Dictionary.items():
        Lengths.append(len(value))
        
    
    MaxLength = max(Lengths)

    for k in range(len(Keys)):
        if Lengths[k] < MaxLength:
            for i in range(MaxLength - Lengths[k]):
                Dictionary[Keys[k]].append([])
        
    return Dictionary
        



def EquateListLengthsInContourData(ContourData):
    """ Equate the number of values (length of list per key) in ContourData.
    
    Inputs:
        ContourData    - Dictionary containing the list of points [x, y, z] 
                         that link any given node in each contour, for all 
                         nodes.
        
    Outputs:
        ContourDataOut - As above but with [] added to entries of shorter lists.

    """
    # Import packages:
    import copy
    
    ContourDataOut = copy.deepcopy(ContourData)
    
    Keys = list(ContourData.keys())
    
    Lengths = []
    
    for key, value in ContourData.items():
        Lengths.append(len(value))
        
    
    MaxLength = max(Lengths)

    for k in range(len(Keys)):
        key = Keys[k]
        
        length = Lengths[k]
        
        if length < MaxLength:
            for i in range(MaxLength - length):
                if key == 'SliceNo':
                    ContourDataOut[key].append(length + i)
                    
                elif key == 'FixContourType':
                    ContourDataOut[key].append(0)
                    
                else:
                    ContourDataOut[key].append([])
        
    return ContourDataOut







def ClockwiseAngleAndDistance(Point, OriginPt):
    """
    Get the angle of Point with respect to OriginPt.
    
    Inputs:
        Point    - A list containing the [x, y, z] ([x, y] should also work) 
                   components of a point.
        
        OriginPt - A list containing the [x, y, z] ([x, y] should also work) 
                   components of a point defined as the origin.
        
    Returns:
        Angle    - A float representing the angle in radians of Point w.r.t.
                   OriginPt.
        
        VectorL  - A float representing the vector length of OriginPt -> Point.
    
    Both the Angle and VectorL are returned, and in that order since the angle
    will be the primary sorting criterion.  If two vectors have the same angle 
    then the points will sorted by the shorter distance.
    
    Code adapted from:
    https://stackoverflow.com/questions/41855695/sorting-list-of-two-dimensional-coordinates-by-clockwise-angle-using-python
    """
    import math
    
    # Define the reference vector:
    RefVector = [0, 1] # pointing up
    RefVector = [0, -1] # pointing down
    #RefVector = [1, 0] # pointing right
    #RefVector = [-1, 0] # pointing left
    
    # Vector between Point and the OriginPt: v = p - o
    Vector = [Point[0] - OriginPt[0], Point[1] - OriginPt[1]]
    
    # Length of vector: ||v||
    VectorL = math.hypot(Vector[0], Vector[1])
    
    # If length is zero there is no angle
    if VectorL == 0:
        return -math.pi, 0
    
    # Normalize vector: v/||v||
    VectorNorm = [Vector[0]/VectorL, Vector[1]/VectorL]
    
    DotProd  = VectorNorm[0] * RefVector[0] + VectorNorm[1] * RefVector[1]     # x1*x2 + y1*y2
    
    DiffProd = RefVector[1] * VectorNorm[0] - RefVector[0] * VectorNorm[1]     # x1*y2 - y1*x2
    
    Angle = math.atan2(DiffProd, DotProd)
    
    # Negative angles represent counter-clockwise angles so need to subtract  
    # them from 2*pi (360 degrees):
    if Angle < 0:
        return 2*math.pi + Angle, VectorL

    else:
        return Angle, VectorL
    
    
    

def GetCentroid(Points):
    """
    Get centroid of points.
    
    Input:
        Points   - A list of the [x, y, z] (or [x, y]) components of the points
                 
    Returns:
        Centroid - A list of the [x, y, z] (or [x, y]) components of the 
                   centroid of Points
    """
    
    # Get the dimensions of Points:
    dim = len(Points[0])
    
    # Get list of x- and y-coords of Points:
    Points_x = [Points[i][0] for i in range(len(Points))]
    Points_y = [Points[i][1] for i in range(len(Points))]
    if dim > 2:
        Points_z = [Points[i][2] for i in range(len(Points))]
    
    Mean_x = sum(Points_x)/len(Points_x)
    Mean_y = sum(Points_y)/len(Points_y)
    if dim > 2:
        Mean_z = sum(Points_z)/len(Points_z)
    
        return [Mean_x, Mean_y, Mean_z]
    
    else:
        return [Mean_x, Mean_y]
    
    
    
    
def SortPointsClockwise(Points):
    """
    Sort points by clockwise ordering.
    
    Inputs:
        Points   - A list of the [x, y, z] ([x, y] should also work) components
                   of the points to be sorted.
        
    Returns:
        Ordered  - A list of the [x, y, z] ([x, y] should also work) components
                   of the points sorted in a clockwise ordering.
    """
    
    OriginPt = GetCentroid(Points)
    
    Ordered = sorted(Points, key=lambda Points: ClockwiseAngleAndDistance(Points, OriginPt))
    
    return Ordered


    


def Point0IsClockwiseToPoint1(Point0, Point1, Centroid):
    """
    Check if Point0 is oriented in a clockwise position to Point1 relative to
    Centroid.
    
    Code adapted from:
    https://stackoverflow.com/questions/6989100/sort-points-in-clockwise-order
    
    Comment 05/08/20:
        This approach doesn't work.  The sorted points zig-zag.
    """

    if ( Point0[0] - Centroid[0] >= 0 ) and ( Point1[0] - Centroid[0] < 0 ):
        return True
    if ( Point0[0] - Centroid[0] < 0 ) and ( Point1[0] - Centroid[0] >= 0 ):
        return False
    if ( Point0[0] - Centroid[0] == 0 ) and ( Point1[0] - Centroid[0] == 0 ):
        if ( Point0[1] - Centroid[1] >= 0 ) or ( Point1[1] - Centroid[1] >= 0 ):
            return Point0[1] > Point1[1]
        return Point1[1] > Point0[1]
    

    # Compute the cross product of vectors (Centroid -> Point0) x (Centroid -> Point1):
    det = (Point0[0] - Centroid[0]) * (Point1[1] - Centroid[1]) - \
          (Point1[0] - Centroid[0]) * (Point0[1] - Centroid[1]);
    if det < 0:
        return True
    if det > 0:
        return False

    # Point0 and Point1 are on the same line from the centroid.
    # Check which point is closer to the centroid:
    d1 = (Point0[0] - Centroid[0]) * (Point0[0] - Centroid[0]) + \
         (Point0[1] - Centroid[1]) * (Point0[1] - Centroid[1])
    
    d2 = (Point1[0] - Centroid[0]) * (Point1[0] - Centroid[0]) + \
         (Point1[1] - Centroid[1]) * (Point1[1] - Centroid[1])
    
    return d1 > d2





def GetVectorLength(Point0, Point1):
    """
    Get vector length between Point0 and Point1.
    
    Inputs:
        Point0  - A list of [x, y, z] (or [x, y]) coordinates of a point
        
        Point1  - A list of [x, y, z] (or [x, y]) coordinates of a point
        
    Returns:
        VectorL - The length of the vector created by Point0 -> Point1
    """
    
    # Get the dimensions of Point0:
    #dim = len(Point0[0]) # 13/08
    dim = len(Point0) # 13/08
    
    #print('Point0 =', Point0)
    #print('Point1 =', Point1)
        
    if dim > 2:
        Vector = [Point1[0] - Point0[0], 
                  Point1[1] - Point0[1], 
                  Point1[2] - Point0[2]]
    
        VectorL = ( Vector[0]**2 + Vector[1]**2 + Vector[2]**2 ) ** 0.5
        
    else:
        Vector = [Point1[0] - Point0[0], 
                  Point1[1] - Point0[1]]
    
        VectorL = ( Vector[0]**2 + Vector[1]**2 ) ** 0.5
        #VectorL = ( Vector[0]**2 + Vector[1]**2 ) # doesn't reduce time by much
        
    return VectorL




def GetVectorLengths(Point0, Points):
    """
    Get list of vector lengths.
    
    Inputs:
        Point0  - A list of [x, y, z] (or [x, y]) coordinates of a point
        
        Points  - A list of [x, y, z] (or [x, y]) coordinates of a list of 
                  points
        
    Returns:
        Lengths - A list of lengths of the vectors defined by Point0 to every
                  point in Points
    """
    
    Lengths = []
    
    for i in range(len(Points)):
        Point1 = Points[i]
        
        Lengths.append(GetVectorLength(Point0, Point1))
        
    return Lengths





def GetContourPerimeter(Contour):
    """ 
    Calculate the perimeter of a contour.
    
    Input:
        Contour   - A list of points (each point a list of [x, y, z] coordinates)
        
    Returns:
        Perimeter - Perimeter of the contour (sum off all segment lengths) 
    """
    
    Perimeter = 0
    
    # Loop through each point and integrate the vector lengths:
    for i in range(len(Contour) - 1):
        Point0 = Contour[i]
        Point1 = Contour[i+1]
        
        VectorL = GetVectorLength(Point0, Point1)
        
        Perimeter += VectorL
        
    return Perimeter





def SortByClosest(Points):
    """ 
    Sort a list of points starting with the first point and the closest until
    no points remain.
    
    Input:
        Points  - A list of [x, y, z] (or [x, y]) coordinates of a list of 
                 points
                 
    Returns:
        Ordered - A list of points in Points ordered by closest
    
    
    Comment 05/08/20:
        This approach doesn't work.
    """
    
    #import copy
    
    # The first point:
    Point0 = Points[0]
    #Point0 = copy.deepcopy(Points[0])
    
    # Remaining points:
    RemPts = [Points[i] for i in range(1, len(Points))]
    #RemPts = copy.deepcopy([Points[i] for i in range(1, len(Points))])
    
    # Initiate sorted list of Points:
    Ordered = [Point0]
    #Ordered = [copy.deepcopy(Point0)]
    
    while RemPts:
        Lengths = GetVectorLengths(Point0, RemPts)
    
        # Get index of point in RemPts that is closest to Point0:
        ind = Lengths.index(min(Lengths))
    
        # Re-define Point0:
        Point0 = RemPts[ind]
        #Point0 = copy.deepcopy(RemPts[ind])
        
        Ordered.append(Point0)
    
        # Pop the ind^th point in RemPts:
        RemPts.pop(ind)
    
    
    return Ordered

   
    
    



def CopyRoisWithInterpolation(FixedDicomDir, MovingDicomDir, FixedRoiFpath, dP, 
                              InterpolateAllPts, UseInterp, LogToConsole, 
                              PlotResults, AnnotatePtNums, ExportResults):
    """
    Copy ROIs from the Fixed to Moving image domain using interpolation between
    adjacent contours.  
    
    This is a main function that runs the following functions:
        1. InterpolateContours
        
        2. TransformInterpolatedContours
        
        3. GetIntersectingContoursInMovingPlanes
        
        
    Interpolation will be midway between all contours in a ROI collection for
    the Fixed image domain by running the main function InterpolateContours() 
    iteratively.
    
    The interpolated contours and the contours used to interpolate them (the
    over-sampled original contours) are then transformed from the Fixed to 
    Moving image domain.
    
    Then the intersecting points between the lines that link each point in the
    first over-sampled contour and the interpolated contour, and each point in
    the interpolated contour and the second over-sampled contour, with the 
    imaging planes is found. These points form contours that lie in the Moving
    image planes.
    
    
    Inputs:
        FixedDicomDir     - Directory containing the DICOMs for the Fixed 
                            image domain.
        
        MovingDicomDir    - Directory containing the DICOMs for the Moving 
                            image domain.
                             
        FixedRoiFpath     - Full path to the ROI Collection RT-STRUCT file.
                             
        dP                - A float denoting the desired inter-node spacing to 
                            use when super-sampling the contours used for 
                            interpolation.
                         
        InterpolateAllPts - A boolean that determines whether or not 
                            interpolation will be performed only between a pair
                            of contour points for which the corresponding node
                            in the longer of the original contours was an
                            original node.  See Note 4 in the function 
                            InterpolateBetweenContours.
                            
        UseInterp         - A boolean that determines whether or not 
                            interpolated contour points will be used when 
                            searching for intersection points between the line 
                            segments that join points on adjacent transformed 
                            contours and the image planes in the Moving domain. 
    
        LogToConsole      - Log some results to the console.
                            
        PlotResults       - Boolean that denotes whether or not results will be
                            plotted.
                            
        AnnotatePtNums     - Boolean value determines whether points are 
                             annotated with point numbers
        
        ExportResults     - Boolean that denotes whether or not plotted results
                            are to be exported.
        
    Returns:
        PointData         - Dictionary containing the data on all points in all
                            contours for the Fixed image and with added entries 
                            for interpolated points.
        
        FixContourData    - Dictionary containing the data on all points 
                            arranged slices, including the interpolated points.
        
        InterpData        - A dictionary containing interpolated data.
    
    """
    
    # Import packages and functions:
    import time
    from GetImageAttributes import GetImageAttributes
    from GetInputPoints import GetInputPoints
    from PCStoICS import PCStoICS
    
    # Force ExportResults to False if PlotResults is False:
    if not PlotResults:
        ExportResults = False
    
    
    # Start timing:
    times = []
    times.append(time.time())
    
    # Chose which package to use to get the Image Plane Attributes:
    #package = 'sitk'
    package = 'pydicom'
    
    # Get the Image Attributes for the Fixed image:
    FixOrigin, FixDirs,\
    FixSpacings, FixDims = GetImageAttributes(DicomDir=FixedDicomDir, 
                                              Package=package)
    
    
    # Get contour points into necessary arrays:
    FixPtsPCS, FixPtsBySliceAndContourPCS,\
    FixPtsICS, FixPtsBySliceAndContourICS,\
    LUT, PointData, FixContourData,\
    ContourData = GetInputPoints(FixedDicomDir=FixedDicomDir, 
                                    FixedRoiFpath=FixedRoiFpath)
    
    
    # Get the indices of the slices that contain contours in the Fixed image:
    FixSlicesWithContours = GetIndsOfSlicesWithContours(ContourData=FixContourData,
                                                        ContourType=1)
    
    
    print('Contours exist on slices', Inds)

    # Initialise a dictionary to store the interpolation results:
    InterpData = {'InterpSliceInd'       : [],
                  'BoundingSliceInds'    : [],
                  'FixOSIsOrigNode1'     : [],
                  'FixOSIsOrigNode2'     : [],
                  'FixOSContour1Inds'    : [],
                  'FixOSContour2Inds'    : [],
                  'FixInterpContourInds' : [],
                  'FixOSContour1Pts'     : [],
                  'FixOSContour2Pts'     : [],
                  'FixInterpContourPts'  : []
                  }
    
    # Iterate through all FixSlicesWithContours and interpolate between each
    # two slices:
    for i in range(len(FixSlicesWithContours) - 1):
        InterpSliceInd = FixSlicesWithContours[i] + 0.5
        
        if LogToConsole:
            print(f'\nAttempting to interpolate at slice {InterpSliceInd}...')
    
    
        #InterpContour = InterpolateContours(FixContourData, PointData, InterpSliceInd, dP)
        
        BoundingSliceInds,\
        OSContour1,\
        OSIsOrigNode1,\
        OSContour2,\
        OSIsOrigNode2,\
        InterpContourPCS = InterpolateContours(FixContourData, PointData, 
                                               InterpSliceInd, dP,
                                               InterpolateAllPts)
    
        # Continue only if None was not returned for InterpContourPCS:
        if InterpContourPCS:
            #print(f'len(InterpContourPCS) = {len(InterpContourPCS)}')
    
            # The maximum contour number in the original contour data:
            LastCntNo = PointData['InContourNo'][-1]
    
            # Add interpolated contour to PointData:
            for i in range(len(InterpContourPCS)):
                PointData['PointNo'].append(PointData['PointNo'][-1] + 1)
                PointData['InSliceNo'].append(InterpSliceInd)
                PointData['InContourNo'].append(LastCntNo + 1)
                PointData['InContourType'].append(2)
                PointData['InPointIndex'].append([])
                PointData['InPointPCS'].append(InterpContourPCS[i])
                PointData['InPointICS'].append(PCStoICS(Pts_PCS=InterpContourPCS[i], 
                                                        Origin=FixOrigin, 
                                                        Directions=FixDirs, 
                                                        Spacings=FixSpacings))
    
            # Add interpolated contour to FixContourData:
            FixContourData['SliceNo'].append(InterpSliceInd)
            FixContourData['ContourType'].append(2)
            #FixContourData['PointPCS'].append(InterpContourPCS)
            #FixContourData['PointICS'].append(PCStoICS(Pts_PCS=InterpContourPCS, 
            #                                           Origin=FixOrigin, 
            #                                           Directions=FixDirs, 
            #                                           Spacings=FixSpacings))
            """
            The list of contour points needs to be in a list structure to be 
            consistent with the other contour data in the dictionary.  
            Should verify this (July 23).
            """
            FixContourData['PointPCS'].append([InterpContourPCS])
            InterpContourICS = PCStoICS(Pts_PCS=InterpContourPCS, 
                                        Origin=FixOrigin, 
                                        Directions=FixDirs, 
                                        Spacings=FixSpacings)
            FixContourData['PointICS'].append([InterpContourICS])
        
            
            # Store the interpolation output in InterpData:
            InterpData['InterpSliceInd'].append(InterpSliceInd)
            InterpData['BoundingSliceInds'].append(BoundingSliceInds)
            InterpData['FixOSIsOrigNode1'].append(OSIsOrigNode1)
            InterpData['FixOSIsOrigNode2'].append(OSIsOrigNode2)
            InterpData['FixOSContour1Pts'].append(OSContour1)
            InterpData['FixOSContour2Pts'].append(OSContour2)
            InterpData['FixInterpContourPts'].append(InterpContourPCS)
                         
   
                
     
    times.append(time.time())
    Dtime = round(times[-1] - times[-2], 1)
    if LogToConsole:
        print(f'\nTook {Dtime} s to interpolate {len(FixSlicesWithContours)}',
              'contours.\n')
        
    
    # Register the image stacks:
    if LogToConsole:
        print('\nRegistering image stacks...')
 
    FixIm, MovIm, RegIm,\
    ElastixImFilt = RegisterImageStacks(FixedDicomDir, MovingDicomDir)
    
    times.append(time.time())
    Dtime = round(times[-1] - times[-2], 1)
    if LogToConsole:
        print(f'Took {Dtime} s to register the Moving image stack to the',
              'Fixed image stack.\n')
        
        
    
    # Transform the interpolated contours and over-sampled contours used to
    # interpolate:
    if LogToConsole:
        print('\nTransforming points...')
 
    InterpData = TransformInterpolatedContours(InterpData, ElastixImFilt, MovIm)
    
    times.append(time.time())
    Dtime = round(times[-1] - times[-2], 1)
    if LogToConsole:
        print(f'Took {Dtime} s to transform the contour points.\n\n')
    
    # Generate contours in the Moving image planes:
    if LogToConsole:
        print('\nFinding intersection of transformed points with the Moving',
              'image planes...\n')
    

    # Choose whether or not the intersection points must lie on the line
    # segments:
    MustBeOnLineSeg = True
    
    # Get the intersecting points of the contours on the moving planes: 
    MovContourData = GetIntersectingPointsInMovingPlanes(InterpData, 
                                                         MovingDicomDir,
                                                         UseInterp,
                                                         MustBeOnLineSeg)
    
    times.append(time.time())
    Dtime = round(times[-1] - times[-2], 1)
    if LogToConsole:
        print(f'\nTook {Dtime} s to find the intersection points.\n\n')
        
    
    """ 
    Comment 01/09/20:
        
        The stuff below is not meaningful, so revert to a modification of v1 of 
        GetIntersectingPointsInMovingPlanes.
    """
    ## Get the intersecting points of the contours on the moving planes:
    #InterpData = GetIntersectingPointsInMovingPlanes_v2(InterpData, 
    #                                                    MovingDicomDir,
    #                                                    UseInterp,
    #                                                    MustBeOnLineSeg,
    #                                                    OnlyKeepClosestIntersPt)
    #
    ## Get the closest intersecting points:
    #InterpData = GetClosestIntersectionPoints(InterpData, MaxDistToImagePlane)
    #
    ## Group intersecting points by slice and contour number:
    #MovContourData = GroupIntersPtsBySliceIndAndContourNum(InterpData, 
    #                                                       MovingDicomDir)
    
    
    # Get the indices of the slices that contain contours in the Moving image:
    MovSlicesWithContours = GetIndsOfSlicesWithContours(ContourData=MovContourData,
                                                        ContourType=3)
    
    times.append(time.time())
    Dtime = round(times[-1] - times[0], 1)
    if LogToConsole:
        F = len(FixSlicesWithContours)
        M = len(MovSlicesWithContours)
        print(f'\nDone.\nTook {Dtime} s to copy {F} contours in the Fixed',
              f'image domain to {M} contours in the Moving image domain.')
    
    
    """ Plot various results: """
    if PlotResults:
        import RegUtilityFuncs as ruf
        import time
        
        SubPlots = True
        
        #""" Get additional data for plots: """
        #import copy
        
        # Get the bounding slice indices for the slice at InterpSliceInd:
        #BoundingSliceInds = GetBoundingSliceInds(FixContourData, PointData, InterpSliceInd)

        #Contour1 = copy.deepcopy(FixContourData['PointPCS'][BoundingSliceInds[0]][0])
        #Contour2 = copy.deepcopy(FixContourData['PointPCS'][BoundingSliceInds[1]][0])

        #if InterpSliceInd.is_integer():
        #    # The actual contour that exists at slice InterpSliceInd:
        #    ActualContour = copy.deepcopy(FixContourData['PointPCS'][InterpSliceInd][0])


        # Combine data into lists to plot:
        #Contours = [Contour1, Contour2, InterpContourPCS]
        #Labels = [f'Contour at slice {BoundingSliceInds[0]}', 
        #          f'Contour at slice {BoundingSliceInds[1]}', 
        #          f'Interpolated contour at {InterpSliceInd}']
        #Colours = ['b', 'g', 'r', 'y']
        ##Shifts = [0, 2, 4, 6] # to help visualise
        #Shifts = [0, 0, 0, 0] # no shift
        #if InterpSliceInd.is_integer():
        #    Contours.append(ActualContour)
        #    Labels.append(f'Actual contour at {InterpSliceInd}')

        # Plot the interpolated and original contours:
        if SubPlots:
            PlotInterpContours2DSubPlots(InterpData=InterpData, 
                                         FixedOrMoving='Fixed', 
                                         dP=dP, 
                                         AnnotatePtNums=False, 
                                         SubPlots=SubPlots, 
                                         ExportPlot=ExportResults)
        else:
            PlotInterpContours2D(InterpData=InterpData, 
                                 FixedOrMoving='Fixed', 
                                 dP=dP, 
                                 AnnotatePtNums=False, 
                                 SubPlots=SubPlots, 
                                 ExportPlot=ExportResults)
                             
        # Plot the transformed interpolated and original contours:
        #if SubPlots:
        #    PlotInterpContours2DSubPlots(InterpData=InterpData,
        #                                 FixedOrMoving='Moving', 
        #                                 dP=dP, 
        #                                 AnnotatePtNums=False, 
        #                                 SubPlots=SubPlots, 
        #                                 ExportPlot=ExportResults)
        #else:
        #    PlotInterpContours2D(InterpData=InterpData,
        #                         FixedOrMoving='Moving', 
        #                         dP=dP, 
        #                         AnnotatePtNums=False, 
        #                         SubPlots=SubPlots, 
        #                         ExportPlot=ExportResults)
                             
        # Plot the intersecting points of the transformed interpolated
        # and original contours with the image planes in the Moving
        # domain:
        if SubPlots:
            PlotIntersectingPts2DSubPlots(MovContourData=MovContourData, 
                                          dP=dP, UseInterp=UseInterp,
                                          AnnotatePtNums=False, 
                                          SubPlots=SubPlots, 
                                          ExportPlot=ExportResults)
        else:
            PlotIntersectingPts2D(MovContourData=MovContourData, 
                                  dP=dP, UseInterp=UseInterp,
                                  AnnotatePtNums=False, 
                                  SubPlots=SubPlots, 
                                  ExportPlot=ExportResults)
                
                
                
        """ Plot DICOM images containing contours overlaid: """        
        
        # Plot all slices containing contours in either image domains.
        # Concatenate the lists:
        FixOrMovSlicesWithContours = FixSlicesWithContours + MovSlicesWithContours
        
        # Reduce to set of unique indices:
        FixOrMovSlicesWithContours = list(set(FixOrMovSlicesWithContours))
        
        # Choose the perspective:
        Perspective = 'axial'
        #Perspective = 'sagittal'
        #Perspective = 'coronal'
        
        # Choose whether to plot contour points as lines or dots:
        ContoursAs = 'lines'
        #ContoursAs = 'dots'

        # Create filename for exported figure:
        ExportFname = time.strftime("%Y%m%d_%H%M%S", time.gmtime()) \
              + f'_Contour_interp_transf_and_inters__dP_{dP}__' \
              + f'UseInterp_{UseInterp}__' + Perspective + '.png'
        
        #ruf.display_all_sitk_images_and_reg_results_with_all_contours_v3(fix_im=FixIm, 
        #                                                                 mov_im=MovIm, 
        #                                                                 reg_im=RegIm,
        #                                                                 fix_pts=FixContourData['PointICS'], 
        #                                                                 mov_pts=MovContourData['PointICS'],
        #                                                                 export_fig=ExportResults,
        #                                                                 export_fname=FigFname,
        #                                                                 plot_slices=FixOrMovSlicesWithContours,
        #                                                                 perspective=Perspective,
        #                                                                 contours_as=ContoursAs,
        #                                                                 LogToConsole=False)
        
        

        ruf.PlotFixMovRegImagesAndContours(FixImage=FixIm, MovImage=MovIm, RegImage=RegIm, 
                                           FixContours=FixContourData['PointICS'], 
                                           MovContours=MovContourData['PointICS'],
                                           SlicesToPlot=FixOrMovSlicesWithContours, 
                                           Perspective=Perspective, ContoursAs=ContoursAs, 
                                           LogToConsole=False, ExportFig=ExportResults, 
                                           ExportFname=ExportFname)
    
    
    return PointData, FixContourData, InterpData, MovContourData, FixIm, MovIm, RegIm





def CopyRois(FixedDicomDir, MovingDicomDir, FixedRoiFpath, dP, 
             InterpolateAllPts, MustBeOnLineSeg, MaxDistToPts, UseInterp, 
             LogToConsole, PlotResults, AnnotatePtNums, ExportResults):
    """
    Copy ROIs from the Fixed to Moving image domain.  
    
    This is a main function that runs the following functions:
        1. InterpolateContours
        
        2. TransformInterpolatedContours
        
        3. GetIntersectingContoursInMovingPlanes
        
        
    Interpolation will be midway between all contours in a ROI collection for
    the Fixed image domain by running the main function InterpolateContours() 
    iteratively.
    
    The interpolated contours and the contours used to interpolate them (the
    over-sampled original contours) are then transformed from the Fixed to 
    Moving image domain.
    
    Then the intersecting points between the lines that link each point in the
    first over-sampled contour and the interpolated contour, and each point in
    the interpolated contour and the second over-sampled contour, with the 
    imaging planes is found. These points form contours that lie in the Moving
    image planes.
    
    
    Inputs:
        FixedDicomDir     - Directory containing the DICOMs for the Fixed 
                            image domain.
        
        MovingDicomDir    - Directory containing the DICOMs for the Moving 
                            image domain.
                             
        FixedRoiFpath     - Full path to the ROI Collection RT-STRUCT file.
                             
        dP                - A float denoting the desired inter-node spacing to 
                            use when super-sampling the contours used for 
                            interpolation.
                         
        InterpolateAllPts - A boolean that determines whether or not 
                            interpolation will be performed only between a pair
                            of contour points for which the corresponding node
                            in the longer of the original contours was an
                            original node.  See Note 4 in the function 
                            InterpolateBetweenContours.
                            
        UseInterp         - A boolean that determines whether or not 
                            interpolated contour points will be used when 
                            searching for intersection points between the line 
                            segments that join points on adjacent transformed 
                            contours and the image planes in the Moving domain. 
    
        LogToConsole      - Log some results to the console.
                            
        PlotResults       - Boolean that denotes whether or not results will be
                            plotted.
                            
        AnnotatePtNums     - Boolean value determines whether points are 
                             annotated with point numbers
        
        ExportResults     - Boolean that denotes whether or not plotted results
                            are to be exported.
        
    Returns:
        PointData         - Dictionary containing the data on all points in all
                            contours for the Fixed image and with added entries 
                            for interpolated points.
        
        FixContourData    - Dictionary containing the data on all points 
                            arranged slices, including the interpolated points.
        
        InterpData        - A dictionary containing interpolated data.
    
    """
    
    # Import packages and functions:
    import time
    from GetImageAttributes import GetImageAttributes
    import importlib
    import GetInputPoints
    importlib.reload(GetInputPoints)
    from GetInputPoints import GetInputPoints
    import PCStoICS
    importlib.reload(PCStoICS)
    from PCStoICS import PCStoICS
    import copy
    import numpy as np
    
    # Force ExportResults to False if PlotResults is False:
    if not PlotResults:
        ExportResults = False
    
    
    # Start timing:
    times = []
    times.append(time.time())
    
    # Chose which package to use to get the Image Plane Attributes:
    #package = 'sitk'
    package = 'pydicom'
    
    # Get the Image Attributes for the Fixed image:
    FixOrigin, FixDirs,\
    FixSpacings, FixDims = GetImageAttributes(DicomDir=FixedDicomDir, 
                                              Package=package)
    
    
    # Get contour points into necessary arrays:
    FixPtsPCS, FixPtsBySliceAndContourPCS,\
    FixPtsICS, FixPtsBySliceAndContourICS,\
    LUT, PointData, FixContourData,\
    ContourData = GetInputPoints(FixedDicomDir=FixedDicomDir, 
                                 FixedRoiFpath=FixedRoiFpath)
    
    #return ContourData

#if False:
    # Resample the fixed contours:
    if LogToConsole:
        print('\nResampling the Fixed contours...')
        
    # Resample all contours for the Fixed image domain:
    #ContourData = ResampleAllFixedContours(ContourData, dP, FixedDicomDir)
    ContourData = ResampleAllFixedContours(ContourData, dP)
    
    times.append(time.time())
    Dtime = round(times[-1] - times[-2], 1)
    if LogToConsole:
        # Get the indices of the slices that contain contours in the Fixed image:
        Cinds = GetIndsOfContourDataWithContourType(ContourData=ContourData, 
                                                    ContourTypeNo=1)
    
        print(f'\nTook {Dtime} s to re-sample {len(Cinds)} contours.\n')
        print('*************************************************************' \
              + '************************************************************')
    
    
    
    # Register the image stacks:
    if LogToConsole:
        print('\nRegistering image stacks...')
 
    FixIm, MovIm, RegIm,\
    ElastixImFilt = RegisterImageStacks(FixedDicomDir, MovingDicomDir)
    
    times.append(time.time())
    Dtime = round(times[-1] - times[-2], 1)
    if LogToConsole:
        print(f'\nTook {Dtime} s to register the Moving', 
              f'image stack to the Fixed image stack.\n')
        print('*************************************************************' \
              + '************************************************************')
        
        
    
    # Transform the fixed contours:
    if LogToConsole:
        print('\nTransforming points...')
 
    ContourData = TransformFixedContours(ContourData, ElastixImFilt, MovIm)
    
    times.append(time.time())
    Dtime = round(times[-1] - times[-2], 1)
    if LogToConsole:
        print(f'\nTook {Dtime} s to transform the Fixed contour points.\n\n')
        print('*************************************************************' \
              + '************************************************************')
        
        
        
    # Create the dictionary ContourSweepData:
    ContourSweepData = CreateContourSweepData(ContourData)
    
    
    return ContourData, ContourSweepData, FixIm, MovIm, RegIm

if False:
    # Find the intersection points:
    if LogToConsole:
        print('\nFinding intersection of transformed points with the Moving',
              'image planes...\n')
    

    # Choose whether or not the intersection points must lie on the line
    # segments:
    #MustBeOnLineSeg = True
    
    # Assign Method variable (not yet implemented in the function below):
    Method = ''
    
    # Get the intersecting points of the contours on the moving planes: 
    ContourData = GetIntersectingPtsFromContourSweepData(ContourSweepData, 
                                                         Method, 
                                                         MustBeOnLineSeg, 
                                                         MaxDistToPts,
                                                         MovingDicomDir, 
                                                         ContourData)
    
    times.append(time.time())
    Dtime = round(times[-1] - times[-2], 1)
    if LogToConsole:
        print(f'\nTook {Dtime} s to find the intersection points.\n\n')
        
        
    
    # Get the indices of the slices that contain contours for the Fixed and
    # Moving image stacks:
    FixSlicesWithContours = GetIndsOfNonEmptyItems(List=ContourData['FixPtsPCS'])
    
    MovSlicesWithContours = GetIndsOfNonEmptyItems(List=ContourData['MovSSPtsPCS'])
    
    times.append(time.time())
    Dtime = round(times[-1] - times[0], 1)
    if LogToConsole:
        F = len(FixSlicesWithContours)
        M = len(MovSlicesWithContours)
        print(f'\nDone.\nTook {Dtime} s to copy {F} contours in the Fixed',
              f'image domain to {M} contours in the Moving image domain.')
        
        
    
    
    
    """ Plot various results: """
    if PlotResults:
        import ContourPlottingFuncs as cpf
        import ImagePlottingFuncs as ipf
        import time
        
        SubPlots = True
             

        """ 11/09:
                The plotting functions below need to be modified for the new
                format of ContourData. 
        """          
        if False:
            # Plot the intersecting points of the transformed interpolated
            # and original contours with the image planes in the Moving
            # domain:
            if SubPlots:
                PlotIntersectingPts2DSubPlots(MovContourData=MovContourData, 
                                              dP=dP, UseInterp=UseInterp,
                                              AnnotatePtNums=False, 
                                              SubPlots=SubPlots, 
                                              ExportPlot=ExportResults)
            else:
                PlotIntersectingPts2D(MovContourData=MovContourData, 
                                      dP=dP, UseInterp=UseInterp,
                                      AnnotatePtNums=False, 
                                      SubPlots=SubPlots, 
                                      ExportPlot=ExportResults)
                
                
                
        """ Plot DICOM images containing contours overlaid: """    
        
        # Convert the Fixed points from PCS to ICS:
        FixPtsICS = PCStoICS(Pts_PCS=ContourData['FixPtsPCS'], Origin=FixOrigin, 
                             Directions=FixDirs, Spacings=FixSpacings)
        
        # Get the Image Attributes for the Moving image:
        MovOrigin, MovDirs,\
        MovSpacings, MovDims = GetImageAttributes(DicomDir=MovingDicomDir, 
                                                  Package=package)
        
        # Which set of Moving (intersection) points to plot:
        MovKey = 'MovSSPtsPCS' # super-sampled points
        #MovKey = 'MovOSPtsPCS' # over-sampled points
        
        # Convert the Moving points from PCS to ICS:
        MovPtsICS = PCStoICS(Pts_PCS=ContourData[MovKey], Origin=FixOrigin, 
                             Directions=FixDirs, Spacings=FixSpacings)
        
        # Plot all slices containing contours in either image domains.
        # Concatenate the lists:
        FixOrMovSlicesWithContours = FixSlicesWithContours + MovSlicesWithContours
        
        # Reduce to set of unique indices:
        FixOrMovSlicesWithContours = list(set(FixOrMovSlicesWithContours))
        
        # Choose the perspective:
        Perspective = 'axial'
        #Perspective = 'sagittal'
        #Perspective = 'coronal'
        
        # Choose whether to plot contour points as lines or dots:
        ContoursAs = 'lines'
        #ContoursAs = 'dots'

        # Create filename for exported figure:
        ExportFname = time.strftime("%Y%m%d_%H%M%S", time.gmtime()) \
              + f'_Contours_resamp_transf_and_inters__dP_{dP}__' \
              + f'UseInterp_{UseInterp}__' + Perspective + '.png'

        ipf.PlotFixMovRegImagesAndContours(FixImage=FixIm, MovImage=MovIm, RegImage=RegIm, 
                                           FixContours=FixPtsICS,
                                           MovContours=MovPtsICS,
                                           SlicesToPlot=FixOrMovSlicesWithContours, 
                                           Perspective=Perspective, ContoursAs=ContoursAs, 
                                           LogToConsole=False, ExportFig=ExportResults, 
                                           ExportFname=ExportFname)
        
        
        """ Plot Fixed contours and image planes in 3D: """ 
        
        # Key of contours to plot:
        key = 'FixPtsPCS'; PlotTitle='Fixed contours'
        
        PlotImagingPlanes=False
        PlotImagingPlanes=True
        
        PlotLineSegments = True
        #PlotLineSegments = False
        
        EveryNthSegment = 50
        EveryNthSegment = 25
        
        SegmentColoursRandom = True
        #SegmentColoursRandom = False # all gray
        
        cpf.PlotContoursAndPlanes3D(Contours=ContourData[key], 
                                    Convert2ICS=False, 
                                    PlotImagingPlanes=PlotImagingPlanes, 
                                    PlotJoiningSegments=PlotLineSegments,
                                    EveryNthSegment=EveryNthSegment,
                                    SegmentColoursRandom=SegmentColoursRandom,
                                    DicomDir=FixedDicomDir, 
                                    PlotTitle=PlotTitle, 
                                    ExportPlot=ExportResults)
        
        
        """ Plot Moving contours and image planes in 3D: """ 
        
        # Key of contours to plot:
        key = 'MovSSPtsPCS'; PlotTitle='Moving contours'
        #key = 'MovOSPtsPCS'; PlotTitle='Moving contours'
        
        PlotImagingPlanes=False
        PlotImagingPlanes=True
        
        PlotLineSegments = True
        #PlotLineSegments = False
        
        EveryNthSegment = 50
        EveryNthSegment = 25
        
        SegmentColoursRandom = True
        #SegmentColoursRandom = False # all gray
        
        cpf.PlotContoursAndPlanes3D(Contours=ContourData[key], 
                                    Convert2ICS=False, 
                                    PlotImagingPlanes=PlotImagingPlanes, 
                                    PlotJoiningSegments=PlotLineSegments,
                                    EveryNthSegment=EveryNthSegment,
                                    SegmentColoursRandom=SegmentColoursRandom,
                                    DicomDir=FixedDicomDir, 
                                    PlotTitle=PlotTitle, 
                                    ExportPlot=ExportResults)
        
    
    return ContourData, ContourSweepData, FixIm, MovIm, RegIm









"""
******************************************************************************
Supplementary functions : 
******************************************************************************
"""



def ReduceNodesOfContour(Contour, IndsToKeep):
    """
    Reduce the number of nodes in a list of contour points.
    
    Inputs:
        Contour        - A list of super-sampled contour points.
        
        IndsToKeep     - A list of booleans whose values denote whether the   
                         corresponding contour point in Contour is to remain
                         (True) or not (False).
        
    Returns:
        ReducedContour - A reduced list of contour points.
        
        
    Note:
        This function is similar to ReduceNodesOfContours() but it operates on
        a single set of contour points.
    """
    
    ReducedContour = []
    
    for i in range(len(Contour)):
        if IndsToKeep[i]:
            ReducedContour.append(Contour[i])
            
    return ReducedContour



def GetSegmentLengths(Contour):
    """
    Generate a list of segment lengths for each segment in a contour.
    
    Inputs:
        Contour   - A list of contour points.
        
    Returns:
        SegmentLs - A list of segment lengths.
    
    """
    
    # Initialise the list of segment lengths:
    SegmentLs = []
    
    # Loop through each point:
    for i in range(len(Contour) - 1):
        # The segment length between every two points:
        SegmentL = (\
                   (Contour[i+1][0] - Contour[i][0])**2 \
                   + (Contour[i+1][1] - Contour[i][1])**2 \
                   + (Contour[i+1][2] - Contour[i][2])**2 \
                   )**(1/2)
              
        SegmentLs.append(SegmentL)
        
    return SegmentLs





def GetIndsOfSliceNumsOfContourType(ContourData, ContourTypeNo):
    ContourTypes = ContourData['ContourType']
    
    inds = []
    
    for i in range(len(ContourTypes)):
        if ContourTypes[i] == ContourTypeNo: # 14/08
        #if ContourTypeNo in ContourTypes[i]: # 14/08
            inds.append(i)
            
    return inds




def GetIndsOfSliceNumsWithContours(Contours):
    
    inds = []
    
    for i in range(len(Contours)):
        # If Contours[i] is not empty:
        if Contours[i]:
            inds.append(i)
            
    return inds



 

def ExportContourPtsToCsv(ContourData, Label):
    """
    ContourData - e.g. FixContourData, MovContourData
    
    Label       - e.g. 'Fix', 'Mov'
    """
    
    import csv

    for i in range(len(ContourData['PointPCS'])):
        Points = ContourData['PointPCS'][i]
        
        if Points:
            Points = Points[0]
            
            SliceNo = ContourData['SliceNo'][i]
            
            with open(Label + f"ContourPts_slice{SliceNo}.csv", "w") as output:
                writer = csv.writer(output, lineterminator='\n')
                writer.writerows(Points)
                
                #for r in range(len(Points)):
                #    writer.writerow(Points[r])
                
    return
    

    






def GetMinMaxIndicesInList(ListOfIndices):
    

    xInds = []
    yInds = []
    zInds = []
    
    for xInd, yInd, zInd in ListOfIndices:
        xInds.append(xInd)
        yInds.append(yInd)
        zInds.append(zInd)
        
    return min(xInds), max(xInds), min(yInds), max(yInds), min(zInds), \
           max(zInds), list(set(zInds))