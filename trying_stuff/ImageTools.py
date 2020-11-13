# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 11:56:14 2020

@author: ctorti
"""




# Import packages and functions:
#import os
import SimpleITK as sitk
import numpy as np
from GeneralTools import ItemsUniqueToWithin
from DicomTools import ImportDicoms



"""
******************************************************************************
******************************************************************************
DICOM IMAGE FUNCTIONS
******************************************************************************
******************************************************************************
"""




def ImportImage(DicomDir):
    """
    Import a DICOM series as a SimpleITK multi-dimensional image.
    
    Inputs:
        DicomDir - (String) Directory containing the Source DICOMs
        
    Returns:
        Image    - (SimpleITK object) SimpleITK image
    
    """
    
    
    
    SitkReader = sitk.ImageSeriesReader()
    SitkNames = SitkReader.GetGDCMSeriesFileNames(DicomDir)
    
    SitkReader.SetFileNames(SitkNames)
    Image = SitkReader.Execute()
    Image = sitk.Cast(Image, sitk.sitkFloat32)
    
    
    """
    Above code reads the DICOMs in a random order of filename for some reason.
    https://stackoverflow.com/questions/41037407/itk-simpleitk-dicom-series-loaded-in-wrong-order-slice-spacing-incorrect#41037408
    """
    
    
    
    """
    FileList = sitk.ImageSeriesReader().GetGDCMSeriesFileNames(DicomDir)
    
    Image = sitk.ReadImage(FileList)
    
    Image = sitk.Cast(Image, sitk.sitkFloat32)
    
    The above code didn't work. Try using GetDicomFpaths:
    """
    
    
    
    """
    SortedFilePaths = GetDicomFpaths(DicomDir, 'slices', False)

    SitkReader = sitk.ImageSeriesReader()
    SitkReader.SetFileNames(SortedFilePaths)
    
    Image = SitkReader.Execute()
    Image = sitk.Cast(Image, sitk.sitkFloat32)
    
    
    I think the reason why the images were loaded in the wrong order for a 
    particular series was that there were repeated IPPs and SimpleITK mis-
    interpretted the data (?):
    
    https://github.com/SimpleITK/SimpleITK/issues/1245
    
    So commenting out the section above which uses GetDicomFpaths to provide
    a list of sorted filepaths to SimpleITK.  It's probably fine to keep but
    possibly unnecessary and redundant.
    """
    
    return Image





def GetImageAttributes(DicomDir, Package='pydicom', LogToConsole=False):
    """
    Get image size, voxel spacings, image positions (IPPs), and direction 
    cosines either using one of two packages: Pydicom or SimpleITK.
    
    
    Inputs:
        DicomDir   - (String) Directory containing DICOMs  
        
        Package    - (String) Package to use; acceptable inputs are:
                     - 'pydicom' (default)
                     - 'sitk' (SimpleITK)
        
    Returns:
        Size       - (List of integers) The size/dimensions of the 3D image 
                     along x, y and z, e.g. [Columns, Rows, NumOfSlices]
                     
        Spacings   - (List of floats) The pixel spacings along x, y and z 
                     (= SliceThickness appended to PixelSpacing), 
                     e.g. [di, dj, dk]
                     
        Positions  - (List of list of floats) The ImagePositionPatient of all 
                     slices in the DICOM series, 
                     e.g. [[x0_0, y0_0, z0_0], [x1_0, y1_0, z1_0], ...]
        
        Directions - (List of floats) The direction cosine along x (rows), 
                     y (columns) and z (slices) 
                     
                     Notes:
                         1) When using Pydicom the cross product of the x and y
                         direction cosines from ImageOrientationPatient is
                         used to obtain the direction cosine along x.
                         
                         2) There is a sign difference between the cross-terms
                         obtained from Pydicom and SimpleITK. If the Directions
                         obtained from Pydicom are:
                         
                         [Xx, Xy, Xz, Yx, Yy, Yz, Zx, Zy, Zz],
                         
                         the Directions obtained from SimpleITK would be:
                         
                         [Xx, -Xy, -Xz, -Yx, Yy, -Yz, -Zx, -Zy, Zz].
                         
                         3) When using Pydicom the Directions will not be 
                         correct for coronal or sagittal image stacks.
        
    """

    if Package=='sitk':
        # Import the image:
        SitkIm = ImportImage(DicomDir)
        
        Size = SitkIm.GetSize()
        
        Spacings = SitkIm.GetSpacing()
        
        #Origin = SitkIm.GetOrigin() 
        
        Positions = []
        
        for i in range(Size[2]):
            Positions.append(SitkIm.TransformIndexToPhysicalPoint((0, 0, i)))
        
        Directions = SitkIm.GetDirection() 
        
        SliceThick = None
        
        
        
    elif Package=='pydicom':
        """
        NOTE:
            This only gives the correct Directions for an axial stack.
            The components need to be switched around the coronal or sagittal.
        """
        
        # Import the DICOMs:
        Dicoms = ImportDicoms(DicomDir=DicomDir, 
                              SortMethod='slices', 
                              LogToConsole=False)
        
        Size = [int(Dicoms[0].Columns), int(Dicoms[0].Rows), len(Dicoms)]
        
        
        #Origin = [float(item) for item in Dicoms[0].ImagePositionPatient]
        
        Positions = []
    
        for dicom in Dicoms:
            Positions.append([float(item) for item in dicom.ImagePositionPatient])
        
        
        # Check if all IPPs are unique.
        """
        Some scans ("ep2ddiff3scantracep2") have repeated IPPs.
        """
        
        # Get unique positions:
        #UniquePositions = list(set(Positions))
        #UniquePositions = np.unique(np.array(Positions))
        UniquePositions = np.array(list(set(tuple(p) for p in Positions)))
        
        P = len(Positions)
        U = len(UniquePositions)
        
        if U != P:
            print(f'\nWarning:  There are only {U} unique IPPs within the',
                  f'list of {P} IPPs.\n')
        
        
        IOP = [float(item) for item in Dicoms[0].ImageOrientationPatient]
        
        # Get the direction vector along z using the cross product of the x and 
        # y vectors:
        zDir = np.cross(IOP[0:3], IOP[3:])
        
        # Append zDir to IOP:
        Directions = IOP
        Directions.extend(zDir)
        
        
        
        Spacings = [float(item) for item in Dicoms[0].PixelSpacing]
        
        SliceThick = float(Dicoms[0].SliceThickness)
        
        """ 
        Don't use SliceThickness for the z-component of the voxel spacing. 
        Instead use the difference between slices from the IPP.
        """
        # Append SliceThick to Spacings:
        #Spacings.append(SliceThick)
        
        # Compute the slice spacings along the z-direction:
        #Dz = np.diff(np.array(Positions), axis=0)[:,2] # <-- WRONG since it doesn't account for IOP
        
        ##UniqueDz = list(set(Dz))
        #UniqueDz = ItemsUniqueToWithin(Dz)
        
        # Compute the vector lengths of the IPP differences:
        Vlengths = []

        for i in range(len(Positions) - 1):
            vector = np.array(Positions[i + 1]) - np.array(Positions[i])
            
            vectorL = (vector[0]**2 + vector[1]**2 + vector[2]**2)**0.5
            
            Vlengths.append(vectorL)
            
        UniqueVlengths = ItemsUniqueToWithin(Vlengths)
        
        # Append UniqueVlengths to Spacings:
        Spacings.append(UniqueVlengths[0])
        
        if len(UniqueVlengths) > 1:
            print('\nWarning:')
            print('    The voxel spacings along the scan direction are',
                  'non-uniform with the following unique values:\n')
            print('   ', UniqueVlengths, '\n')
        
        
        # Compare UniqueDz to SliceThickness:    
        #epsilon = 1e-5
        #
        #if abs(SliceThick - UniqueDz[0]) > epsilon:
        #    print('\nNote:')
        #    print('    The slice thickness obtained from the IPPs do not',
        #          'agree with the DICOM tag SliceThickness:')
        #    print(f'      d(IPP[2])      = {UniqueDz[0]}')
        #    print(f'      SliceThickness = {SliceThick}')
        
    
        
    if LogToConsole:
        print(f'Size = {Size} \n\nSpacings = {Spacings} \n\n',
              f'SliceThickness = {SliceThick} \n\n',
              f'Positions = {Positions} \n\nDirections = {Directions}')
    
    
    return Size, Spacings, SliceThick, Positions, Directions







def CompareSourceTargetImageAttributes(SrcDcmDir, TrgDcmDir):
#def CompareSrTrgImAttrs(SrcDcmDir, TrgDcmDir):    
    # Get the image attributes using Pydicom:
    SrcPydiSize, SrcPydiSpacing, SrcPydiST,\
    SrcPydiIPP, SrcPydiDir = GetImageAttributes(SrcDcmDir)
    
    TrgPydiSize, TrgPydiSpacing, TrgPydiST,\
    TrgPydiIPP, TrgPydiDir = GetImageAttributes(TrgDcmDir)
    
    # Get the Image Attributes for Source and Target using SimpleITK:
    SrcSitkSize, SrcSitkSpacing, SrcSitkST,\
    SrcSitkIPP, SrcSitkDir = GetImageAttributes(DicomDir=SrcDcmDir,
                                                Package='sitk')
    
    TrgSitkSize, TrgSitkSpacing, TrgSitkST,\
    TrgSitkIPP, TrgSitkDir = GetImageAttributes(DicomDir=TrgDcmDir,
                                                Package='sitk')
    
    
    title = 'Select image attributes for *Source* DICOMs from Pydicom and' \
            + 'SimpleITK:'
    ul = '*' * len(title)
    
    print('\n' + title)
    print(ul + '\n')
    print(f'Pydi Size           = {SrcPydiSize}')
    print(f'Sitk Size           = {list(SrcSitkSize)}\n')
    print(f'Pydi Spacing        = {SrcPydiSpacing}')
    print(f'Sitk Spacing        = {list(SrcSitkSpacing)}\n')
    print(f'Pydi SliceThickness = {SrcPydiST}')
    print(f'Pydi Origin         = {SrcPydiIPP[0]}')
    print(f'Sitk Origin         = {list(SrcSitkIPP[0])}\n\n')
    
    title = 'Select image attributes for *Target* DICOMs from Pydicom and SimpleITK:'
    ul = '*' * len(title)
    
    print('\n' + title)
    print(ul + '\n')
    print(f'Pydi Size           = {TrgPydiSize}')
    print(f'Sitk Size           = {list(TrgSitkSize)}\n')
    print(f'Pydi Spacing        = {TrgPydiSpacing}')
    print(f'Sitk Spacing        = {list(TrgSitkSpacing)}\n')
    print(f'Pydi SliceThickness = {TrgPydiST}')
    print(f'Pydi Origin         = {TrgPydiIPP[0]}')
    print(f'Sitk Origin         = {list(TrgSitkIPP[0])}\n\n')
    
    
    return







def InitialiseImage(RefImage):
    """
    Initialise an empty SimpleITK image with the same size, spacing, origin and
    direction as another image.  
    
    Inputs:
        RefImage - (SimpleITK image) Reference image whose attributes will be 
                   used for NewIm)
        
    Returns:
        NewImage - (SimpleITK image) Empty image with same PixelID, Size, 
                   Spacing, Origin and Direction as RefIm

    """
    NewImage = sitk.Image(RefImage.GetSize(), RefImage.GetPixelID())
    
    NewImage.SetOrigin(RefImage.GetOrigin())
    
    NewImage.SetDirection(RefImage.GetDirection())
    
    NewImage.SetSpacing(RefImage.GetSpacing())
    
    return NewImage





def ImageMax(Image):
    """
    Find maximum of an SimpleITK image.  
    
    Inputs:
        Image   - A SimpleITK image
        
    Returns:
        Maximum - Maximum value of Image

    """
            
    MaxImFilt = sitk.MinimumMaximumImageFilter()
    MaxImFilt.Execute(Image)
    
    return MaxImFilt.GetMaximum()




def ImageMin(Image):
    """
    Find minimum of an SimpleITK image.  
    
    Inputs:
        Image   - A SimpleITK image
        
    Returns:
        Minimum - Maximum value of Image

    """
    
    MaxImFilt = sitk.MinimumMaximumImageFilter()
    MaxImFilt.Execute(Image)
    
    return MaxImFilt.GetMinimum()





def OrImages(Image0, Image1):
    """
    Perform pixel-wise OR operation on two SimpleITK images.  
    
    Inputs:
        Image0   - A SimpleITK image
        
        Image1   - A SimpleITK image
        
    Returns:
        ImageOr - Pixel-wise Image0 OR Image1

    """
            
    OrImageFilt = sitk.OrImageFilter()
    ImageOr = OrImageFilt.Execute(Image0, Image1)
    
    return ImageOr




def AddImages(Image0, Image1):
    """
    Perform pixel-wise addition of two SimpleITK images.  
    
    Inputs:
        Image0   - A SimpleITK image
        
        Image1   - A SimpleITK image
        
    Returns:
        ImageSum - Pixel-wise sum of Image0 and Image1

    """
            
    AddImFilt = sitk.AddImageFilter()
    ImageSum = AddImFilt.Execute(Image0, Image1)
    
    return ImageSum








def ResampleImage(Image, RefImage, Interpolation):
    """
    Resample a 3D SimpleITK image.  The image can be a 3D DICOM image or a
    3D labelmap image.
    
    Inputs:                      
        Image         - (SimpleITK image) The 3D image to be resampled
                           
        RefImage      - (SimpleITK image) The 3D image reference image
        
        Interpolation - (String) The type of interpolation to be used;
                        acceptable inputs are:
                            - 'Linear' (or 'linear') 
                            - 'BSpline' (or 'Bspline' or 'bspline')
                            - 'NearestNeighbor' (or 'NearestNeighbour' or
                            'nearestneighbor' or 'nearestneighbour')
        
    Returns:
        ResImage      - (SimpleITK image) The resampled 3D image

    
    Note:
        While a linear (or BSpline) interpolator is appropriate for intensity 
        images, only a NearestNeighbor interpolator is appropriate for binary 
        images (e.g. segmentations) so that no new labels are introduced.
    """

    
    # Define which interpolator to use:
    if 'inear' in Interpolation:
        Interpolator = sitk.sitkLinear
    if 'pline' in Interpolation:
        Interpolator = sitk.sitkBSpline
    if ('earest' and 'eighbo' or 'nn' or 'NN') in Interpolation:    
        Interpolator = sitk.sitkNearestNeighbor
            
        
    #print('\nUsing', Interpolation, 'interpolation\n')
    
    #Dimension = Image.GetDimension()
    
    Resampler = sitk.ResampleImageFilter()
    
    Resampler.SetReferenceImage(RefImage)
    
    Resampler.SetInterpolator(Interpolator)
    
    # Use the Identity transform:
    Resampler.SetTransform(sitk.Transform())
    
    # Use the Affine transform:
    #Resampler.SetTransform(sitk.AffineTransform(Dimension))
    
    #print(f'\nImage.GetPixelIDValue() = {Image.GetPixelIDValue()}')
    
    Resampler.SetOutputSpacing(RefImage.GetSpacing())
    Resampler.SetSize(RefImage.GetSize())
    Resampler.SetOutputDirection(RefImage.GetDirection())
    Resampler.SetOutputOrigin(RefImage.GetOrigin())
    #Resampler.SetDefaultPixelValue(Image.GetPixelIDValue())
    Resampler.SetDefaultPixelValue(0)
    
    #print('\n')
    #Resampler.AddCommand(sitk.sitkProgressEvent, lambda: print("\rProgress: {0:03.1f}%...".format(100*Resampler.GetProgress()),end=''))
    #Resampler.AddCommand(sitk.sitkProgressEvent, lambda: sys.stdout.flush())
    
    ResImage = Resampler.Execute(Image)
    
    #sitk.Show(ResImage)

    return ResImage