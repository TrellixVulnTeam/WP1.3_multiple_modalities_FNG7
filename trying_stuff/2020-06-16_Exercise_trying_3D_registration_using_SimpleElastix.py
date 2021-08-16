#!/usr/bin/env python
# coding: utf-8

# # Guidance
# 
# 
# ## Data
# 
# This is a stripped down version of previous version "2020-06-05_Exercise_trying_3D_registration_using_SimpleElastix.ipynb" to make it easier to follow.  For details of what was tried, why, what worked/failed, etc. refer to the May 22 version.
# 
# The data used is from Subject 011 from the ACRIN-FMISO-Brain data set obtained here:
# 
# https://wiki.cancerimagingarchive.net/pages/viewpage.action?pageId=33948305#a6b63241cb4843a291c45ef8a62d2073
# 
# You can selectively download data for that subject only.  Specifically two series from two sessions were used:
# 
# 8-T1 SE AXIAL POST FS FC-59362 (Series 8) within 04-10-1960-MRI Brain wwo Contrast-69626
# 
# and
# 
# 8-T1 SE AXIAL POST FC-81428 (Series 8) within 06-11-1961-MRI Brain wwo Contrast-79433
# 
# An ROI Collection was manually created within the OHIF-Viewer for the series from 1960.  The DICOM-RTSTRUCT file can be obtained here:
# 
# https://drive.google.com/drive/folders/1CDrwTYvlvBL6rpuyz29zxO6AU4Ancmd6?usp=sharing
# 
# Originally the 1960 series (with ROI Collection) was defined as the "fixed" image, and the 1961 series as "moving".  This is fine but requires the inverse transformation used to register moving to fixed to deform the fixed image's contour points to the moving image.
# 
# I'm sure this can be done but I don't yet know how, so in the meantime fixed will be defined as the 1961 series, and moving the 1960 one.
# 
# ## SimpleElastix
# 
# I recommend trying to install SimpleElastix using a pre-compiled Python module obtained here:
# 
# https://www.francescosantini.com/wp/2020/03/06/simpleelastix-precompiled-python-modules/
# 
# If it doesn't work you will have to compile it from source:
# 
# https://simpleelastix.readthedocs.io/GettingStarted.html
# 
# There's a "more official" wheel provided here:
# 
# https://sourceforge.net/projects/simpleelastix/
# 
# but it might be for an older version of SimpleElastix (and I think I had trouble with this wheel and ended up having to compile it - I hadn't yet discovered Francesco Santini's page).
# 
# ## Other packages
# 
# Most of the other packages can be pip installed straightforwardly.  
# 
# The other imports are functions that can be obtained here:
# 
# https://github.com/ncita-repository/WP1.3_multiple_modalities/tree/master/trying_stuff

# ### Import packages and functions

# In[3]:


import SimpleITK as sitk
print(sitk.Version())
import numpy as np
import time
import os
import copy
import importlib
import json
import pydicom
import pandas as pd
import matplotlib.pyplot as plt
get_ipython().run_line_magic('matplotlib', 'inline')
get_ipython().run_line_magic('matplotlib', 'notebook')
from ipywidgets import interact, fixed
from IPython.display import clear_output

from GetDicomFpaths import GetDicomFpaths
from GetDicoms import GetDicoms
import GetContourPtsForDicoms
importlib.reload(GetContourPtsForDicoms)
from GetContourPtsForDicoms import GetContourPtsForDicoms
from GetInputPoints import GetInputPoints
#import CreateInputFileForElastix
#importlib.reload(CreateInputFileForElastix)
from CreateInputFileForElastix import CreateInputFileForElastix
from ParseTransformixOutput import ParseTransformixOutput
from GetImageAttributes import GetImageAttributes
import PCStoICS
importlib.reload(PCStoICS)
from PCStoICS import PCStoICS
from RunSimpleElastixReg import RunSimpleElastixReg
from TransformPoints import TransformPoints
import RegUtilityFuncs
importlib.reload(RegUtilityFuncs)
import RegUtilityFuncs as ruf


# In[4]:


# Define FixedDicomDir and MovingDicomDir:
DicomDir = r'C:\Data\Cancer imaging archive\ACRIN-FMISO-Brain\ACRIN-FMISO-Brain-011'
FixDicomDir = os.path.join(DicomDir, r'04-10-1960-MRI Brain wwo Contrast-69626\8-T1 SE AXIAL POST FS FC-59362')
MovDicomDir = os.path.join(DicomDir, r'06-11-1961-MRI Brain wwo Contrast-79433\8-T1 SE AXIAL POST FS FC-81428')

# Define the filepath to the ROI Collection (for the fixed) image:
FixRoiDir = r'C:\Temp\2020-05-13 ACRIN MR_4 to MR_12\8 T1 SE AXIAL POST FS FC ROIs (source)'
FixRoiFname = r'AIM_20200511_073405.dcm'
FixRoiFpath = os.path.join(FixRoiDir, FixRoiFname)

# Chose which package to use to get the Image Plane Attributes:
#package = 'pydicom'
package = 'sitk'

# Get the Image Attributes:
Origin, Directions, Spacings, Dimensions = GetImageAttributes(DicomDir=MovDicomDir, 
                                                              Package=package)

# Get contour points into necessary arrays and dictionaries:
#FixPts_PCS, FixPtsArr_PCS, FixPtsDict_PCS = GetContourPtsForDicoms(DicomDir=FixDicomDir,
#                                                                   RoiFpath=FixRoiFpath)

InPts_PCS, InPtsArr_PCS, InPtsDict_PCS,InPts_ICS, InPtsArr_ICS, InPtsDict_ICS = GetInputPoints(DicomDir=FixDicomDir, 
                                                        RoiFpath=FixRoiFpath,
                                                        Origin=Origin,
                                                        Directions=Directions,
                                                        Spacings=Spacings)

# Read in the 3D stack of Fixed DICOMs:
FixReader = sitk.ImageSeriesReader()
FixNames = FixReader.GetGDCMSeriesFileNames(FixDicomDir)
FixReader.SetFileNames(FixNames)
FixIm = FixReader.Execute()
FixIm = sitk.Cast(FixIm, sitk.sitkFloat32)

# Read in the 3D stack of Moving DICOMs:
MovReader = sitk.ImageSeriesReader()
MovNames = MovReader.GetGDCMSeriesFileNames(MovDicomDir)
MovReader.SetFileNames(MovNames)
MovIm = MovReader.Execute()
MovIm = sitk.Cast(MovIm, sitk.sitkFloat32)

# Get some info on FixIm and MovIm:
ruf.ShowImagesInfo(FixIm, MovIm)


# In[3]:


#MovPtsArr_PCS


# In[3]:


# Convert InPts_PCS from PCS to ICS:
InPts_ICS = PCStoICS(Pts_PCS=InPts_PCS, Origin=Origin, Directions=Directions, Spacings=Spacings)
InPts_ICS


# In[4]:


InPtsArr_PCS


# In[5]:


InPtsArr_ICS


# ### Display images using interactive plot:

# gui.MultiImageDisplay(image_list = [FixedIm, MovingIm],                   
#                       title_list = ['Fixed', 'Moving'], figure_size=(8,4));

# if False:
#     interact(ruf.display_images,
#     fix_ind=(0,FixedIm.GetSize()[2]-1),
#     mov_ind=(0,MovingIm.GetSize()[2]-1),
#     fix_npa = fixed(sitk.GetArrayFromImage(FixedIm)),
#     mov_npa = fixed(sitk.GetArrayFromImage(MovingIm)),
#     fix_title = 'Fixed image',
#     mov_title = 'Moving image');
# 
# interact(ruf.display_images_with_contours,
#          fix_ind=(0,FixIm.GetSize()[2]-1),
#          mov_ind=(0,MovIm.GetSize()[2]-1),
#          fix_npa = fixed(sitk.GetArrayFromImage(FixIm)),
#          mov_npa = fixed(sitk.GetArrayFromImage(MovIm)),
#          fix_im = fixed(FixIm),
#          mov_im = fixed(MovIm),
#          mov_contour_pts = fixed(MovPtsArr_ICS),
#          fix_title = 'Fixed image',
#          mov_title = 'Moving image');

# ### Create inputpoints.txt for Elastix, containing the contour points to be transformed:

# In[6]:


import CreateInputFileForElastix
importlib.reload(CreateInputFileForElastix)
from CreateInputFileForElastix import CreateInputFileForElastix

CoordSys = 'PCS'
#CoordSys = 'ICS'

# Create inputpoints.txt for Elastix, containing the contour points to be
# transformed:
CreateInputFileForElastix(DicomDir=FixDicomDir, RoiFpath=FixRoiFpath, 
                          Origin=Origin, Directions=Directions, Spacings=Spacings,
                          CoordSys=CoordSys)


# ### View the created file inputpoints.pcs

# In[11]:


# Open the text file:
#TextFile = open('inputpoints.txt', 'r')

#for line in TextFile:
#    print(line)


# ### Register MovingIm to FixedIm using SimpleElastix:

# In[7]:


RegIm, ElastixImFilt = RunSimpleElastixReg(FixIm, MovIm)


# ### Get some info on FixIm, MovIm and RegIm:

# In[7]:


# Get some info on FixIm, MovIm and RegIm:

#ruf.ShowRegResults(FixIm, MovIm, RegIm)


# In[8]:


#print(FixedIm)


# In[9]:


#print(MovingIm)


# In[10]:


#print(RegIm)


# ### Plot the results:

# import RegUtilityFuncs
# importlib.reload(RegUtilityFuncs)
# import RegUtilityFuncs as ruf
# 
# 
# if False:
#     interact(ruf.display_sitk_images_and_reg_result,
#              fix_ind=(0,FixedIm.GetSize()[2]-1),
#              mov_ind=(0,MovingIm.GetSize()[2]-1),
#              reg_ind=(0,RegIm.GetSize()[2]-1),
#              fix_im = fixed(FixedIm),
#              mov_im = fixed(MovingIm),
#              reg_im = fixed(RegIm));
# 
# interact(ruf.display_sitk_images_and_reg_result_with_contours,
#          fix_ind = (0,FixIm.GetSize()[2]-1),
#          mov_ind = (0,MovIm.GetSize()[2]-1),
#          reg_ind = (0,RegIm.GetSize()[2]-1),
#          fix_im = fixed(FixIm),
#          mov_im = fixed(MovIm),
#          reg_im = fixed(RegIm),
#          mov_contour_pts = fixed(MovPtsArr_ICS));

# ImFilter.PrintParameterMap()

# ### Transform the contour points:
# 
# https://simpleelastix.readthedocs.io/PointBasedRegistration.html

# In[8]:


# Transform MovingContourPts:
TransformPoints(MovingImage=MovIm, TransformFilter=ElastixImFilt)


# In[9]:


# Parse outputpoints.txt:
PtNos, InInds, InPts_PCS, FixOutInds,OutPts_PCS, Defs_PCS, MovOutInds = ParseTransformixOutput()

"""
Note: The relationship between the above variable names and the items in outputpoints.txt are as follows:

PtNos      = Point
InInds     = InputIndex
InPts      = InputPoint
FixOutInds = OutputIndexFixed
OutPts     = OutputPoint
Defs       = Deformation
MovOutInds = OutputIndexMoving
"""

#[print(f'\nPoint {PtNos[i]}:\nInputIndex = {InInds[i]}\nFixedOutputIndex = {FixOutInds[i]}') for i in range(len(PtNos))]

print('\nParsed OutputPoints.txt:\n')
for i in range(len(PtNos)):
    print(f'\nPoint {PtNos[i]}:')
    print(f'InputIndex        = {InInds[i]}')
    print(f'InputPoint_PCS    = {InPts_PCS[i]}')
    print(f'FixedOutputIndex  = {FixOutInds[i]}')
    print(f'OutputPoint_PCS   = {OutPts_PCS[i]}')
    print(f'Deformation_PCS   = {Defs_PCS[i]}')
    print(f'MovingOutputIndex = {MovOutInds[i]}')


# ### Convert output points from PCS to ICS

# In[22]:


OutPts_PCS[0]


# In[23]:


[OutPts_PCS[0]]


# In[25]:


from PCStoICS import PCStoICS

PCStoICS(Pts_PCS=[OutPts_PCS[0]], SitkIm=MovIm)


# In[23]:


PCStoICS(Pts_PCS=[OutPts_PCS[0]], SitkIm=MovIm)[0]


# In[10]:


import GetOutputPoints
importlib.reload(GetOutputPoints)
from GetOutputPoints import GetOutputPoints

# Convert InPts_PCS, OutPts_PCS and Defs_PCS to ICS:
#InPts_ICS = ruf.PCStoICS(InPts_PCS, MovIm)
#OutPts_ICS = ruf.PCStoICS(OutPts_PCS, MovIm)
#
#P = len(PtNos)
#Defs_ICS = [[OutPts_ICS[p][i] - InPts_ICS[p][i] for i in range(3)] for p in range(P)]

PtNos, InInds, InPts_PCS, InPts_ICS,FixOutInds, OutPts_PCS, OutPts_ICS,Defs_PCS, Defs_ICS, MovOutInds,OutPtsArr_PCS, OutPtsArr_ICS = GetOutputPoints(Origin=Origin, Directions=Directions,
                                              Spacings=Spacings, Dimensions=Dimensions)

# Create a dictionary to store the output:
OutPtsDict = {'PtNo':PtNos,
              'InInd':InInds,
              'InPt_PCS':InPts_PCS,
              'InPt_ICS':InPts_ICS,
              'FixOutInd':FixOutInds,
              'OutPt_PCS':OutPts_PCS,
              'OutPt_ICS':OutPts_ICS,
              'Def_PCS':Defs_PCS,
              'Def_ICS':Defs_ICS,
              'MovOutInd':MovOutInds
             }

#OutPtsDict

# Convert the dictionary to a dataframe:
OutPtsDf = pd.DataFrame(data=OutPtsDict)

OutPtsDf[0:20]


# In[62]:


print(151.8/13.1)
print(130.3/11.7)
print(0.62/1.91)


# In[21]:


OutPtsArr_ICS


# In[17]:


### 15/06: Display result of:
# 1. Created inputpoints.txt in PCS (directly from ContourData)
# 2. Transformed points
# 3. Converted points given by OutputPoint from PCS to ICS (using 3D conversion)
# 4. Grouped converted points by z-index given by OutputIndexMoving

""" 
Although the points are not overlaying correctly, at least the contours were spread 
across a number of slices (compare to results obtained by deforming points in the ICS,
which resulted in most of the z-indices in OutputIndexMoving = 13, with some in 12 and 
some in 14).
This suggests that the points need to be transformed in the PCS.
But further work required to get the points overlayed properly.
"""

# Choose whether to export figure:
export_fig = True
export_fig = False


# Create filename for exported figure:
fig_fname = time.strftime("%Y%m%d_%H%M%S", time.gmtime()) + '_' + CoordSys             +'_reg_result_sitk.png'

ruf.display_all_sitk_images_and_reg_results_with_all_contours(fix_im=FixIm, mov_im=MovIm, reg_im=RegIm,
                                                              fix_pts=FixPtsArr_ICS, mov_pts=TxPtsArr_ICS,
                                                              export_fig=export_fig,
                                                              export_fname=fig_fname)


# In[53]:


import RegUtilityFuncs
importlib.reload(RegUtilityFuncs)
import RegUtilityFuncs as ruf

InputPoint_ICS = ruf.PCStoICS(InPts_PCS, MovIm)
OutputPoint_ICS = ruf.PCStoICS(OutPts_PCS, MovIm)

print(OutputPoint_ICS[0])
print(InputPoint_ICS[0])

[OutputPoint_ICS[0][i] - InputPoint_ICS[0][i] for i in range(3)]

[[OutputPoint_ICS[p][i] - InputPoint_ICS[p][i] for i in range(3)] for p in range(len(OutputPoint_ICS))]


# In[18]:


OutPtsArr_PCS


# In[26]:


OutPtsArr_ICS


# In[28]:


### 17/06: Display result of:
# 1. Created inputpoints.txt in PCS (directly from ContourData)
# 2. Transformed points
# 3. Converted points given by OutputPoint from PCS to ICS (using 3D conversion)
# 4. Grouped converted points by z-index given by OutputIndexMoving

### using latest equations derived on June 17 - Attempt #1.

""" 
Although the points are not overlaying correctly, at least the contours were spread 
across a number of slices (compare to results obtained by deforming points in the ICS,
which resulted in most of the z-indices in OutputIndexMoving = 13, with some in 12 and 
some in 14).
This suggests that the points need to be transformed in the PCS.
But further work required to get the points overlayed properly.
"""

import RegUtilityFuncs
importlib.reload(RegUtilityFuncs)
import RegUtilityFuncs as ruf

# Choose whether to export figure:
export_fig = True
#export_fig = False


# Create filename for exported figure:
fig_fname = time.strftime("%Y%m%d_%H%M%S", time.gmtime()) + '_' + CoordSys             +'_reg_result_sitk.png'

ruf.display_all_sitk_images_and_reg_results_with_all_contours(fix_im=FixIm, mov_im=MovIm, reg_im=RegIm,
                                                              fix_pts=InPtsArr_ICS, mov_pts=OutPtsArr_ICS,
                                                              export_fig=export_fig,
                                                              export_fname=fig_fname)


# In[11]:


### 18/06: Display result of:
# 1. Created inputpoints.txt in PCS (directly from ContourData)
# 2. Transformed points
# 3. Converted points given by OutputPoint from PCS to ICS (using 3D conversion)
# 4. Grouped converted points by z-index given by OutputIndexMoving

### using latest equations derived on June 17 - Attempt #2.

""" 
Although the points are not overlaying correctly, at least the contours were spread 
across a number of slices (compare to results obtained by deforming points in the ICS,
which resulted in most of the z-indices in OutputIndexMoving = 13, with some in 12 and 
some in 14).
This suggests that the points need to be transformed in the PCS.
But further work required to get the points overlayed properly.
"""

import RegUtilityFuncs
importlib.reload(RegUtilityFuncs)
import RegUtilityFuncs as ruf

# Choose whether to export figure:
export_fig = True
#export_fig = False


# Create filename for exported figure:
fig_fname = time.strftime("%Y%m%d_%H%M%S", time.gmtime()) + '_' + CoordSys             +'_reg_result_sitk.png'

ruf.display_all_sitk_images_and_reg_results_with_all_contours(fix_im=FixIm, mov_im=MovIm, reg_im=RegIm,
                                                              fix_pts=InPtsArr_ICS, mov_pts=OutPtsArr_ICS,
                                                              export_fig=export_fig,
                                                              export_fname=fig_fname)


# In[ ]:





# ### Compare the direction cosines from Pydicom and from SimpleITK:

# In[23]:


MovDicomFpaths, MovDicoms = GetDicoms(MovDicomDir, 'slices', Debug=False)

MovIPP = [float(item) for item in MovDicoms[0].ImagePositionPatient]
MovIOP = [float(item) for item in MovDicoms[0].ImageOrientationPatient]
MovPixSpacing = [float(item) for item in MovDicoms[0].PixelSpacing]
MovSliceThick = float(MovDicoms[0].SliceThickness)
MovPixSpacing.append(MovSliceThick)
MovCols = int(MovDicoms[0].Columns)
MovRows = int(MovDicoms[0].Rows)
MovSlices = len(MovDicoms)
MovDims = [MovCols, MovRows, MovSlices]

MovIOPx = MovIOP[0:3]
MovIOPy = MovIOP[3:]
MovIOPz = np.cross(MovIOPx,MovIOPy)

print(f'MovIPP        = {MovIPP}')
print(f'MovIOPx       = {MovIOPx}')
print(f'MovIOPy       = {MovIOPy}')
print(f'MovIOPz       = {MovIOPz}')
print(f'MovPixSpacing = {MovPixSpacing}')
print(f'MovDims       = {MovDims}')

print('')

MovOrig = MovIm.GetOrigin()
MovDirx = MovIm.GetDirection()[0:3]
MovDiry = MovIm.GetDirection()[3:6]
MovDirz = MovIm.GetDirection()[6:]
MovSpacing = MovIm.GetSpacing()
MovSize = MovIm.GetSize()
 

print(f'MovOrig    = {MovOrig}')
print(f'MovDirx    = {MovDirx}')
print(f'MovDiry    = {MovDiry}')
print(f'MovDirz    = {MovDirz}')
print(f'MovSpacing = {MovSpacing}')
print(f'MovSize    = {MovSize}')


# In[28]:


print(f'MovIOP        = {MovIOP}')
print(float(MovDicoms[0].SliceThickness))
print(np.cross(MovIOPx,MovIOPy))
print(f'Columns = {int(MovDicoms[0].Columns)}')
print(f'Rows = {int(MovDicoms[0].Rows)}')
print(f'Slices = {len(MovDicoms)}')
print(f'Dimensions = {[int(MovDicoms[0].Columns), int(MovDicoms[0].Rows), len(MovDicoms)]}')
print(np.shape(MovDicoms[0].pixel_array))


# In[32]:


np.shape(MovDicoms[0].pixel_array)


# In[26]:


MovIm.GetSize()


# ### sitk gives the number of columns first, then rows, then slices!

# In[ ]:


print('FixIm origin  =', FixIm.GetOrigin())
print('')
print('MovIm origin =', MovIm.GetOrigin())

fix_dz = FixIm.GetSpacing()[2]
mov_dz = MovIm.GetSpacing()[2]
reg_dz = RegIm.GetSpacing()[2]

fix_z0 = FixIm.GetOrigin()[2]
mov_z0 = MovIm.GetOrigin()[2]
reg_z0 = RegIm.GetOrigin()[2]

fix_npa = sitk.GetArrayFromImage(FixIm)
mov_npa = sitk.GetArrayFromImage(MovIm)
reg_npa = sitk.GetArrayFromImage(RegIm)

fix_N = len(fix_npa)
mov_N = len(mov_npa)
reg_N = len(reg_npa)

# Compute the z position:
fix_z = [fix_z0 + fix_dz*(s) for s in range(fix_N)]
mov_z = [mov_z0 + mov_dz*(s) for s in range(mov_N)]
reg_z = [reg_z0 + reg_dz*(s) for s in range(reg_N)]

print('\nfix_z =\n', fix_z)
print('\nmov_z =\n', mov_z)
print('\nreg_z =\n', reg_z)


# In[42]:


FixSize = FixIm.GetSize()
MovSize = MovIm.GetSize()

print(f'z at FixIm[0,0,0]     = {FixIm.TransformIndexToPhysicalPoint((0, 0, 0))[2]} mm')
print(f'z at FixIm[96,128,0]  = {FixIm.TransformIndexToPhysicalPoint((int(FixSize[0]/2), int(FixSize[1]/2), 0))[2]} mm')
print(f'z at FixIm[192,256,0] = {FixIm.TransformIndexToPhysicalPoint((FixSize[0], FixSize[1], 0))[2]} mm')
print('')
print(f'z at MovIm[0,0,0]     = {MovIm.TransformIndexToPhysicalPoint((0, 0, 0))[2]} mm')
print(f'z at MovIm[96,128,0]  = {MovIm.TransformIndexToPhysicalPoint((int(MovSize[0]/2), int(MovSize[1]/2), 0))[2]} mm')
print(f'z at MovIm[192,256,0] = {MovIm.TransformIndexToPhysicalPoint((MovSize[0], MovSize[1], 0))[2]} mm')
print('')
print('FixIm z-Direction =', FixIm.GetDirection()[6:])
print('')
print('MovIm z-Direction =', MovIm.GetDirection()[6:])


# In[43]:


MovSize = MovIm.GetSize()

for z_ind in range(MovSize[2]):
    print(f'z at MovIm[96,128,{z_ind}] = {MovIm.TransformIndexToPhysicalPoint((int(MovSize[0]/2), int(MovSize[2]/2), z_ind))[2]} mm')


# # 18/06:  Combine all necessary code into a single cell for efficiency:

# In[5]:


import SimpleITK as sitk
print(sitk.Version())
import numpy as np
import time
import os
import copy
import importlib
import json
import pydicom
import pandas as pd
import matplotlib.pyplot as plt
get_ipython().run_line_magic('matplotlib', 'inline')
get_ipython().run_line_magic('matplotlib', 'notebook')
from ipywidgets import interact, fixed
from IPython.display import clear_output

from GetDicomFpaths import GetDicomFpaths
from GetDicoms import GetDicoms
import GetContourPtsForDicoms
importlib.reload(GetContourPtsForDicoms)
from GetContourPtsForDicoms import GetContourPtsForDicoms
from GetInputPoints import GetInputPoints
#import CreateInputFileForElastix
#importlib.reload(CreateInputFileForElastix)
from CreateInputFileForElastix import CreateInputFileForElastix
from ParseTransformixOutput import ParseTransformixOutput
import GetImageAttributes
importlib.reload(GetImageAttributes)
from GetImageAttributes import GetImageAttributes
import PCStoICS
importlib.reload(PCStoICS)
from PCStoICS import PCStoICS
from RunSimpleElastixReg import RunSimpleElastixReg
from TransformPoints import TransformPoints
from GetOutputPoints import GetOutputPoints
import RegUtilityFuncs
importlib.reload(RegUtilityFuncs)
import RegUtilityFuncs as ruf

# Define FixedDicomDir and MovingDicomDir:
DicomDir = r'C:\Data\Cancer imaging archive\ACRIN-FMISO-Brain\ACRIN-FMISO-Brain-011'
FixDicomDir = os.path.join(DicomDir, r'04-10-1960-MRI Brain wwo Contrast-69626\8-T1 SE AXIAL POST FS FC-59362')
MovDicomDir = os.path.join(DicomDir, r'06-11-1961-MRI Brain wwo Contrast-79433\8-T1 SE AXIAL POST FS FC-81428')

# Define the filepath to the ROI Collection (for the fixed) image:
FixRoiDir = r'C:\Temp\2020-05-13 ACRIN MR_4 to MR_12\8 T1 SE AXIAL POST FS FC ROIs (source)'
FixRoiFname = r'AIM_20200511_073405.dcm'
FixRoiFpath = os.path.join(FixRoiDir, FixRoiFname)

# Chose which package to use to get the Image Plane Attributes:
package = 'sitk'
package = 'pydicom'


# Get the Image Attributes:
Origin, Directions, Spacings, Dimensions = GetImageAttributes(DicomDir=MovDicomDir, 
                                                              Package=package)

# Get contour points into necessary arrays and dictionaries:
#FixPts_PCS, FixPtsArr_PCS, FixPtsDict_PCS = GetContourPtsForDicoms(DicomDir=FixDicomDir,
#                                                                   RoiFpath=FixRoiFpath)

InPts_PCS, InPtsArr_PCS, InPtsDict_PCS,InPts_ICS, InPtsArr_ICS, InPtsDict_ICS = GetInputPoints(DicomDir=FixDicomDir, 
                                                        RoiFpath=FixRoiFpath,
                                                        Origin=Origin,
                                                        Directions=Directions,
                                                        Spacings=Spacings)

# Read in the 3D stack of Fixed DICOMs:
FixReader = sitk.ImageSeriesReader()
FixNames = FixReader.GetGDCMSeriesFileNames(FixDicomDir)
FixReader.SetFileNames(FixNames)
FixIm = FixReader.Execute()
FixIm = sitk.Cast(FixIm, sitk.sitkFloat32)

# Read in the 3D stack of Moving DICOMs:
MovReader = sitk.ImageSeriesReader()
MovNames = MovReader.GetGDCMSeriesFileNames(MovDicomDir)
MovReader.SetFileNames(MovNames)
MovIm = MovReader.Execute()
MovIm = sitk.Cast(MovIm, sitk.sitkFloat32)

# Get some info on FixIm and MovIm:
#ruf.ShowImagesInfo(FixIm, MovIm)

CoordSys = 'PCS'
#CoordSys = 'ICS'

# Create inputpoints.txt for Elastix, containing the contour points to be
# transformed:
CreateInputFileForElastix(DicomDir=FixDicomDir, RoiFpath=FixRoiFpath, 
                          Origin=Origin, Directions=Directions, Spacings=Spacings,
                          CoordSys=CoordSys)

# Register:
RegIm, ElastixImFilt = RunSimpleElastixReg(FixIm, MovIm)

# Transform MovingContourPts:
TransformPoints(MovingImage=MovIm, TransformFilter=ElastixImFilt)

# Parse outputpoints.txt:
#PtNos, InInds, InPts_PCS, FixOutInds,\
#OutPts_PCS, Defs_PCS, MovOutInds = ParseTransformixOutput()

PtNos, InInds, InPts_PCS, InPts_ICS,FixOutInds, OutPts_PCS, OutPts_ICS,Defs_PCS, Defs_ICS, MovOutInds,OutPtsArr_PCS, OutPtsArr_ICS = GetOutputPoints(Origin=Origin, Directions=Directions,
                                              Spacings=Spacings, Dimensions=Dimensions)

print('\nDone.')


# In[2]:


# Using package = sitk and equations from June 17 Attempt #2:

# Chose which slices to plot:
plot_slices = -1 # plot all
plot_slices = [14]

# Choose whether to export figure:
export_fig = True
export_fig = False


# Create filename for exported figure:
fig_fname = time.strftime("%Y%m%d_%H%M%S", time.gmtime()) + '_' + CoordSys             +'_reg_result_using_' + package + '.png'

ruf.display_all_sitk_images_and_reg_results_with_all_contours(fix_im=FixIm, mov_im=MovIm, reg_im=RegIm,
                                                              fix_pts=InPtsArr_ICS, mov_pts=OutPtsArr_ICS,
                                                              export_fig=export_fig,
                                                              export_fname=fig_fname,
                                                              plot_slices=plot_slices)


# In[2]:


# Using package = pydicom and equations from June 17 Attempt #2:

# Chose which slices to plot:
plot_slices = -1 # plot all
plot_slices = [14]

# Choose whether to export figure:
export_fig = True
export_fig = False


# Create filename for exported figure:
fig_fname = time.strftime("%Y%m%d_%H%M%S", time.gmtime()) + '_' + CoordSys             +'_reg_result_using_' + package + '_June17_Attempt2_eqs.png'

ruf.display_all_sitk_images_and_reg_results_with_all_contours(fix_im=FixIm, mov_im=MovIm, reg_im=RegIm,
                                                              fix_pts=InPtsArr_ICS, mov_pts=OutPtsArr_ICS,
                                                              export_fig=export_fig,
                                                              export_fname=fig_fname,
                                                              plot_slices=plot_slices)


# In[2]:


# Using package = pydicom from June 15 Attempt #3:

# Chose which slices to plot:
plot_slices = -1 # plot all
plot_slices = [14]

# Choose whether to export figure:
export_fig = True
export_fig = False


# Create filename for exported figure:
fig_fname = time.strftime("%Y%m%d_%H%M%S", time.gmtime()) + '_' + CoordSys             +'_reg_result_using_' + package + '_June15_Attempt3_eqs.png'

ruf.display_all_sitk_images_and_reg_results_with_all_contours(fix_im=FixIm, mov_im=MovIm, reg_im=RegIm,
                                                              fix_pts=InPtsArr_ICS, mov_pts=OutPtsArr_ICS,
                                                              export_fig=export_fig,
                                                              export_fname=fig_fname,
                                                              plot_slices=plot_slices)


# In[31]:


# Using package = pydicom from 2D equations (k approximation):

# Chose which slices to plot:
plot_slices = -1 # plot all
plot_slices = [14]

# Choose whether to export figure:
export_fig = True
export_fig = False


# Create filename for exported figure:
fig_fname = time.strftime("%Y%m%d_%H%M%S", time.gmtime()) + '_' + CoordSys             +'_reg_result_using_' + package + '_2D_eqs_with_k_approx.png'

ruf.display_all_sitk_images_and_reg_results_with_all_contours(fix_im=FixIm, mov_im=MovIm, reg_im=RegIm,
                                                              fix_pts=InPtsArr_ICS, mov_pts=OutPtsArr_ICS,
                                                              export_fig=export_fig,
                                                              export_fname=fig_fname,
                                                              plot_slices=plot_slices)


# In[3]:


# Using package = sitk from 2D equations (k approximation):

# Chose which slices to plot:
plot_slices = -1 # plot all
plot_slices = [14]

# Choose whether to export figure:
export_fig = True
export_fig = False


# Create filename for exported figure:
fig_fname = time.strftime("%Y%m%d_%H%M%S", time.gmtime()) + '_' + CoordSys             +'_reg_result_using_' + package + '_2D_eqs_with_k_approx.png'

ruf.display_all_sitk_images_and_reg_results_with_all_contours(fix_im=FixIm, mov_im=MovIm, reg_im=RegIm,
                                                              fix_pts=InPtsArr_ICS, mov_pts=OutPtsArr_ICS,
                                                              export_fig=export_fig,
                                                              export_fname=fig_fname,
                                                              plot_slices=plot_slices)


# In[7]:


print(isinstance(3, int))
print(isinstance([3,4], int))


# ### 19/06:  Try to figure out why input contour points not overlaid properly on fixed image:

# In[3]:


InPts_PCS


# In[4]:


InPtsArr_PCS


# In[6]:


InPts_ICS


# In[7]:


InPtsArr_ICS


# ### I think I know what the problem is - I used the image attributes (origin, direction, etc.) of the Moving image not only to convert the transformed points (belonging to the moving image) from PCS to ICS, but also for the conversion of the input points from PCS to ICS (belonging to the fixed image)!!!
# 
# ### Try above code but with two sets of image attributes - for fixed and for moving image:

# In[6]:


import SimpleITK as sitk
print(sitk.Version())
import numpy as np
import time
import os
import copy
import importlib
import json
import pydicom
import pandas as pd
import matplotlib.pyplot as plt
get_ipython().run_line_magic('matplotlib', 'inline')
get_ipython().run_line_magic('matplotlib', 'notebook')
from ipywidgets import interact, fixed
from IPython.display import clear_output

from GetDicomFpaths import GetDicomFpaths
from GetDicoms import GetDicoms
import GetContourPtsForDicoms
importlib.reload(GetContourPtsForDicoms)
from GetContourPtsForDicoms import GetContourPtsForDicoms
from GetInputPoints import GetInputPoints
#import CreateInputFileForElastix
#importlib.reload(CreateInputFileForElastix)
from CreateInputFileForElastix import CreateInputFileForElastix
from ParseTransformixOutput import ParseTransformixOutput
import GetImageAttributes
importlib.reload(GetImageAttributes)
from GetImageAttributes import GetImageAttributes
import PCStoICS
importlib.reload(PCStoICS)
from PCStoICS import PCStoICS
from RunSimpleElastixReg import RunSimpleElastixReg
from TransformPoints import TransformPoints
from GetOutputPoints import GetOutputPoints
import RegUtilityFuncs
importlib.reload(RegUtilityFuncs)
import RegUtilityFuncs as ruf

# Define FixedDicomDir and MovingDicomDir:
DicomDir = r'C:\Data\Cancer imaging archive\ACRIN-FMISO-Brain\ACRIN-FMISO-Brain-011'
FixDicomDir = os.path.join(DicomDir, r'04-10-1960-MRI Brain wwo Contrast-69626\8-T1 SE AXIAL POST FS FC-59362')
MovDicomDir = os.path.join(DicomDir, r'06-11-1961-MRI Brain wwo Contrast-79433\8-T1 SE AXIAL POST FS FC-81428')

# Define the filepath to the ROI Collection (for the fixed) image:
FixRoiDir = r'C:\Temp\2020-05-13 ACRIN MR_4 to MR_12\8 T1 SE AXIAL POST FS FC ROIs (source)'
FixRoiFname = r'AIM_20200511_073405.dcm'
FixRoiFpath = os.path.join(FixRoiDir, FixRoiFname)

# Chose which package to use to get the Image Plane Attributes:
package = 'sitk'
package = 'pydicom'


# Get the Image Attributes for the images:
FixOrigin, FixDirs, FixSpacings, FixDims = GetImageAttributes(DicomDir=FixDicomDir, 
                                                              Package=package)

MovOrigin, MovDirs, MovSpacings, MovDims = GetImageAttributes(DicomDir=MovDicomDir, 
                                                              Package=package)

# Get contour points into necessary arrays and dictionaries:
#FixPts_PCS, FixPtsArr_PCS, FixPtsDict_PCS = GetContourPtsForDicoms(DicomDir=FixDicomDir,
#                                                                   RoiFpath=FixRoiFpath)

InPts_PCS, InPtsArr_PCS, InPtsDict_PCS,InPts_ICS, InPtsArr_ICS, InPtsDict_ICS = GetInputPoints(DicomDir=FixDicomDir, 
                                                        RoiFpath=FixRoiFpath,
                                                        Origin=FixOrigin,
                                                        Directions=FixDirs,
                                                        Spacings=FixSpacings)

# Read in the 3D stack of Fixed DICOMs:
FixReader = sitk.ImageSeriesReader()
FixNames = FixReader.GetGDCMSeriesFileNames(FixDicomDir)
FixReader.SetFileNames(FixNames)
FixIm = FixReader.Execute()
FixIm = sitk.Cast(FixIm, sitk.sitkFloat32)

# Read in the 3D stack of Moving DICOMs:
MovReader = sitk.ImageSeriesReader()
MovNames = MovReader.GetGDCMSeriesFileNames(MovDicomDir)
MovReader.SetFileNames(MovNames)
MovIm = MovReader.Execute()
MovIm = sitk.Cast(MovIm, sitk.sitkFloat32)

# Get some info on FixIm and MovIm:
#ruf.ShowImagesInfo(FixIm, MovIm)

CoordSys = 'PCS'
#CoordSys = 'ICS'

# Create inputpoints.txt for Elastix, containing the contour points to be
# transformed:
CreateInputFileForElastix(DicomDir=FixDicomDir, RoiFpath=FixRoiFpath, 
                          Origin=FixOrigin, Directions=FixDirs, Spacings=FixSpacings,
                          CoordSys=CoordSys)

# Register:
RegIm, ElastixImFilt = RunSimpleElastixReg(FixIm, MovIm)

# Transform MovingContourPts:
TransformPoints(MovingImage=MovIm, TransformFilter=ElastixImFilt)

# Parse outputpoints.txt:
#PtNos, InInds, InPts_PCS, FixOutInds,\
#OutPts_PCS, Defs_PCS, MovOutInds = ParseTransformixOutput()

PtNos, InInds, InPts_PCS, InPts_ICS,FixOutInds, OutPts_PCS, OutPts_ICS,Defs_PCS, Defs_ICS, MovOutInds,OutPtsArr_PCS, OutPtsArr_ICS = GetOutputPoints(Origin=MovOrigin, Directions=MovDirs,
                                               Spacings=MovSpacings, Dimensions=MovDims)

print('\nDone.')


# In[22]:


# Chose which slices to plot:
plot_slices = -1 # plot all
plot_slices = [14]

# Choose whether to export figure:
export_fig = True
export_fig = False


# Create filename for exported figure:
fig_fname = time.strftime("%Y%m%d_%H%M%S", time.gmtime()) + '_' + CoordSys             +'_reg_result_using_' + package + '_June17_Attempt2_eqs.png'

ruf.display_all_sitk_images_and_reg_results_with_all_contours(fix_im=FixIm, mov_im=MovIm, reg_im=RegIm,
                                                              fix_pts=InPtsArr_ICS, mov_pts=OutPtsArr_ICS,
                                                              export_fig=export_fig,
                                                              export_fname=fig_fname,
                                                              plot_slices=plot_slices)


# ## Success!
# 
# ## Next steps:
# 
# ## 1) Store the transformed points into an RTSTRUCT file for importing into the OHIF-Viewer to see how they appear there.
# 
# ## 2) Tidy up the contours:
# 
# ### i.   Some/most/all contours require "closing"
# ### ii.  Some require removal of un-closed segments (e.g. 18th slice)
# ### iii. Some require avoiding segments crossing through the outer boundary (e.g. 15-17th slice)
# ### iv. Some require some awkward closing (e.g. 13th slice)

# ## Step 1:  Create ROI for Moving Image
# 
# ### This is a bit trickier than simply modifying a copy of the fixed ROI, since there are more contour sequences within the transformed points than in the original ROI.

# In[34]:


# Use the fixed ROI as a template for the moving image:
FixRoi = pydicom.dcmread(FixRoiFpath)

MovRoi = copy.deepcopy(FixRoi)

MovRoi
#MovRoi.PatientName


# In[131]:


#print(len(MovRoi.ReferencedFrameOfReferenceSequence[0].RTReferencedStudySequence[0].\
#RTReferencedSeriesSequence[0].ContourImageSequence))

#print(len(MovRoi.ROIContourSequence[0].ContourSequence))

MovRoi.ReferencedFrameOfReferenceSequence[0].RTReferencedStudySequence[0].RTReferencedSeriesSequence[0].ContourImageSequence


# In[181]:


print(len(OutPtsArr_ICS))
print(MovIm.GetSize()[2])
print(len(MovDicoms))
print()


# In[182]:


set(OutPtsArr_ICS)


# # Get the z-component of the indices of the transformed points:
# MovZinds = [MovOutInds[i][2] for i in range(len(MovOutInds))]
# 
# print('MovZinds =', MovZinds)
# 
# # Get the unique indices in ascending order:
# MovZindsSet = list(set(MovZinds))
# MovN = len(MovZindsSet)
# 
# print('\nMovZindsSet =', MovZindsSet)
# 
# # Get the number of unique values in MovInds:
# 

# ordering = []
# MovZinds_ordered = []
# 
# 
# for Zind in MovZindsSet:
#     for ind, zind in enumerate(MovZinds):
#         print(f'ind = {ind}, zind = {zind}')
#         if zind == Zind:
#             ordering.append(ind)
#             
#             MovZinds_ordered.append(zind)
#             
#             
#             
#     

# In[18]:


# Get the indices of the non-empty arrays in OutPtsArr_ICS:
MovInds = []

for i in range(len(OutPtsArr_ICS)):
    if OutPtsArr_ICS[i]:
        MovInds.append(i)
        
MovN = len(MovInds)
        
print(f'MovInds = {MovInds}')
print(f'MovN = {MovN}')

# Create a new array of contour points in the format required for the ROI object:
ContourData = []
Npts = []
#MovZindsSet = []

for i in range(len(OutPtsArr_ICS)):
    if OutPtsArr_ICS[i]:
        points = OutPtsArr_ICS[i]

        Npts.append(len(points))

        #print(f'Number of points = {len(points)}')

        PtsFlat = []

        for point in points:
            # Convert coordinates of point to strings:
            PtsFlat.extend([str(point[p]) for p in range(3)])

        ContourData.append(PtsFlat)
        #MovZindsSet.append(i)
        
    else:
        ContourData.append([])
        
        Npts.append(0)
        

print('Npts =', Npts)
ContourData


# # June 22: It seems that appending to the sequences results in the assigning of the 5th sequence the same values as that for the 6th! 

# In[223]:


# Get the z-component of the indices of the transformed points:
#MovZinds = [MovOutInds[i][2] for i in range(len(MovOutInds))]

#print(set(MovZinds))

# Get the number of unique values in MovInds:
#MovN = len(set(MovZinds))

# Get the indices of the non-empty arrays in OutPtsArr_ICS:
#MovInds = []

#for i in range(len(OutPtsArr_ICS)):
#    if OutPtsArr_ICS[i]:
#        MovInds.append(i)
        
#MovN = len(MovInds)
        
#print(f'MovInds = {MovInds}')
#print(f'MovN = {MovN}')

# Get the number of contour image sequences in the copied ROI:
#FixN = len(MovRoi.ReferencedFrameOfReferenceSequence[0].RTReferencedStudySequence[0].\
#RTReferencedSeriesSequence[0].ContourImageSequence)
FixN = len(MovRoi.ROIContourSequence[0].ContourSequence)

print(f'Number of contour sequences in the original ROI  = {FixN}')
print(f'Number of contour sequences required for new ROI = {MovN}')

# Add/remove contour image sequences and contour sequences by 
# appending/popping the last sequence N times, where N is the difference
# between MovN and FixN:
if FixN != MovN:
    if MovN > FixN:
        print(f'There are {MovN - FixN} more contour sequences required in the ROI. ')
        for i in range(MovN - FixN):
            MovRoi.ReferencedFrameOfReferenceSequence[0]            .RTReferencedStudySequence[0].RTReferencedSeriesSequence[0]            .ContourImageSequence            .append(MovRoi.ReferencedFrameOfReferenceSequence[0]            .RTReferencedStudySequence[0].RTReferencedSeriesSequence[0]            .ContourImageSequence[-1])

            MovRoi.ROIContourSequence[0].ContourSequence            .append(MovRoi.ROIContourSequence[0].ContourSequence[-1])
            
    else:
        print(f'There are {FixN - MovN} excess contour sequences in the ROI. ')
        for i in range(FixN - MovN):
            MovRoi.ReferencedFrameOfReferenceSequence[0].RTReferencedStudySequence[0].            RTReferencedSeriesSequence[0].ContourImageSequence.pop()
            
            MovRoi.ROIContourSequence[0].ContourSequence.pop()
            
#MovN = len(MovRoi.ReferencedFrameOfReferenceSequence[0].RTReferencedStudySequence[0].\
#RTReferencedSeriesSequence[0].ContourImageSequence)
MovN = len(MovRoi.ROIContourSequence[0].ContourSequence)

print(f'Number of contour sequences in new ROI           = {MovN}')


# In[37]:


#temp[5].ContourData


# In[41]:


if False:
    i = 0

    for item in MovRoi.ROIContourSequence[0].ContourSequence:
        print(f'\ni = {i}:\n', item)
        i += 1
    
temp = copy.deepcopy(FixRoi.ROIContourSequence[0].ContourSequence)

print('\n\nLast item before append:\n\n', temp[-1])

#temp.append(temp[-1])
temp.append(copy.deepcopy(temp[-1]))

print('\n\nLast two items after append:\n\n', temp[-2:])

temp[5].NumberOfContourPoints = "1"
temp[5].ContourNumber = "6"
temp[5].ContourData = ["0", "0", "0"]

print('\n\nLast two items after modification:\n\n', temp[-2:])


# In[31]:


list = [1, 2, 3]

print('List before appending:', list)

list.append(list[-1])

print('\nList after appending:', list)

for i in range(len(list)):
    list[i] = (i+1)*10
    
print('\nList after modifying:', list)
    


# In[189]:


#MovZinds


# In[169]:


list(set(MovZinds))


# In[ ]:


""" MovDicoms needs to be indexed by MovZinds after re-ordering... """


# In[224]:


MovRoi


# In[87]:


print(len(MovRoi.ReferencedFrameOfReferenceSequence[0].RTReferencedStudySequence[0].RTReferencedSeriesSequence[0].ContourImageSequence))

print(len(MovRoi.ROIContourSequence[0].ContourSequence))


# In[13]:


# Read in the DICOMs:
FixDicomFpaths, FixDicoms = GetDicoms(DirPath=FixDicomDir, SortMethod='slices', Debug=False)

MovDicomFpaths, MovDicoms = GetDicoms(DirPath=MovDicomDir, SortMethod='slices', Debug=False)

FixDicoms[0]


# In[39]:


MovDicoms[0]


# # Create a new array of arrays of transformed points,
# # similar to OutPtsArr_ICS but without empty arrays:
# OutPtsArr_ICS_nonempty = [OutPtsArr_ICS[i] for i in range(len(OutPtsArr_ICS)) if OutPtsArr_ICS[i]!=[]]
# 
# print(f'Number of arrays in OutPtsArr_ICS_nonempty = {len(OutPtsArr_ICS_nonempty)}')
# 
# #OutPtsArr_ICS_nonempty[0]
# 
# # Flatten each array in OutPtsArr_ICS_nonempty as required for ContourData array:
# ContourData = []
# Npts = []
# 
# for i in range(len(OutPtsArr_ICS_nonempty)):
#     points = OutPtsArr_ICS_nonempty[i]
#     
#     Npts.append(len(points))
#     
#     print(f'Number of points = {len(points)}')
#           
#     PtsFlat = []
#     
#     for point in points:
#         # Convert coordinates of point to strings:
#         PtsFlat.extend([str(point[p]) for p in range(3)])
#     
#     ContourData.append(PtsFlat)
#     
# print(f'Number of arrays in ContourData = {len(ContourData)}')
# 
# #ContourData[0]
# 

# In[16]:


""" This will need to be tested for cases where there's more than one contour in an image! """

if False:
    # Create a new array of arrays of transformed points,
    # similar to OutPtsArr_ICS but without empty arrays:
    OutPtsArr_ICS_nonempty = [OutPtsArr_ICS[i] for i in range(len(OutPtsArr_ICS)) if OutPtsArr_ICS[i]!=[]]

    #print(f'Number of arrays in OutPtsArr_ICS_nonempty = {len(OutPtsArr_ICS_nonempty)}')

    #OutPtsArr_ICS_nonempty[0]

    # Flatten each array in OutPtsArr_ICS_nonempty as required for ContourData array:
    ContourData = []
    Npts = []

    for i in range(len(OutPtsArr_ICS_nonempty)):
        points = OutPtsArr_ICS_nonempty[i]

        Npts.append(len(points))

        #print(f'Number of points = {len(points)}')

        PtsFlat = []

        for point in points:
            # Convert coordinates of point to strings:
            PtsFlat.extend([str(point[p]) for p in range(3)])

        ContourData.append(PtsFlat)

    #print(f'Number of arrays in ContourData = {len(ContourData)}')

    #ContourData[0]



# Start modfying MovRoi:

# Generate a new SOP Instance UID:
MovRoi.SOPInstanceUID = pydicom.uid.generate_uid()

# Modify the Study Date and Time:
MovRoi.StudyDate = MovDicoms[0].StudyDate
""" 
For current data, the Series Time and Instance Creation Time in the DICOM 
both match the Study Time in the ROI, whereas the DICOM's Study Time does not.
"""
#MovRoi.StudyTime = MovDicoms[0].StudyTime 
MovRoi.StudyTime = MovDicoms[0].SeriesTime

# Modify the Patient's Name and ID:
MovRoi.PatientName = MovDicoms[0].PatientName
MovRoi.PatientID = MovDicoms[0].PatientID

""" Skipping other non-critical tags... """

# Modify the Study Instance UID:
MovRoi.StudyInstanceUID = MovDicoms[0].StudyInstanceUID

# Generate a new Series Instance UID:
MovRoi.SeriesInstanceUID = pydicom.uid.generate_uid()

# Modify the Frame of Reference UID:
MovRoi.FrameOfReferenceUID = MovDicoms[0].FrameOfReferenceUID

# Modify the Structure Set Label:
MovRoi.StructureSetLabel = 'Copy_of_' + MovRoi.StructureSetLabel

# Modify the Structure Set Date and Time to the present:
NewDate = time.strftime("%Y%m%d", time.gmtime())
NewTime = time.strftime("%H%M%S", time.gmtime())
MovRoi.StructureSetDate = NewDate
MovRoi.StructureSetTime = NewTime

# Modify the Referenced Frame of Reference Sequence:
MovRoi.ReferencedFrameOfReferenceSequence[0].FrameOfReferenceUID = MovDicoms[0].FrameOfReferenceUID

# Modify the Referenced SOP Instance UID in the RT Referenced Study Sequence:
MovRoi.ReferencedFrameOfReferenceSequence[0].RTReferencedStudySequence[0].ReferencedSOPInstanceUID = MovDicoms[0].StudyInstanceUID

# Modify the Series Instance UID in the RT Referenced Series Sequence:
MovRoi.ReferencedFrameOfReferenceSequence[0].RTReferencedStudySequence[0].RTReferencedSeriesSequence[0].SeriesInstanceUID = MovDicoms[0].SeriesInstanceUID

# Modify the Referenced Frame of Reference UID and ROI Name for the 
# Structure Set ROI Sequence:
MovRoi.StructureSetROISequence[0].ReferencedFrameOfReferenceUID = MovDicoms[0].FrameOfReferenceUID
MovRoi.StructureSetROISequence[0].ROIName = MovRoi.StructureSetLabel

# Modify the RT ROI Observations Sequence:
""" Not sure if these need to be changed """
#MovRoi.RTROIObservationsSequence[0].ObservationNumber = 
#MovRoi.RTROIObservationsSequence[0].ReferencedROINumber = 
#MovRoi.RTROIObservationsSequence[0].RTROIInterpretedType = 
#MovRoi.RTROIObservationsSequence[0].ROIInterpreter = 


# Modify the Contour Image Sequences in the Referenced Frame of Reference Sequence: 

# Get the number of Contour Image Sequences:
#N_CIS = MovRoi.ReferencedFrameOfReferenceSequence[0].RTReferencedStudySequence[0]\
#.RTReferencedSeriesSequence[0].ContourImageSequence

# Cycle through each Contour Image Sequence and modify the Referenced SOP Class UID
# and Referenced SOP Instance UID with those of MovDicoms[0]:
#for i in range(len(N_CIS)):
#for i in range(len(ContourData)):
for i in range(len(MovInds)):
    print(f'i = {i}, MovInds[i] = {MovInds[i]}')
    
    # Modify the Referenced SOP Class UID:
    MovRoi.ReferencedFrameOfReferenceSequence[0].RTReferencedStudySequence[0]    .RTReferencedSeriesSequence[0].ContourImageSequence[i]    .ReferencedSOPClassUID = MovDicoms[MovInds[i]].SOPClassUID
    
    # Modify the SOP Instance UID:
    MovRoi.ReferencedFrameOfReferenceSequence[0].RTReferencedStudySequence[0]    .RTReferencedSeriesSequence[0].ContourImageSequence[i]    .ReferencedSOPInstanceUID = MovDicoms[MovInds[i]].SOPInstanceUID
    

# Modify the Contour Sequences in the ROI Contour Sequence: 

# Get the number of Contour Sequences:
#N_CS = MovRoi.ROIContourSequence[0].ContourSequence

# Cycle through each Contour Sequence and modify the Referenced SOP Class UID and
# Referenced SOP Instance UID in the Contour Image Sequence with those of MovDicoms[0],
# and modify the Contour Geometric Type, Number of Contour Points, Contour Number and
# Contour Data:
#for i in range(len(N_CS)):
#for i in range(len(ContourData)):
for i in range(len(MovInds)):
    print(f'i = {i}, MovInds[{i}] = {MovInds[i]}')
    
    # Modify the Referenced SOP Class UID:
    MovRoi.ROIContourSequence[0].ContourSequence[i]    .ContourImageSequence[0].ReferencedSOPClassUID = MovDicoms[MovInds[i]].SOPClassUID
    
    # Modify the SOP Instance UID:
    MovRoi.ROIContourSequence[0].ContourSequence[i]    .ContourImageSequence[0].ReferencedSOPInstanceUID = MovDicoms[MovInds[i]].SOPInstanceUID
    
    # Modify the Contour Geometric Type:
    """ Since the contours are not closed change from 'CLOSED_PLANAR' to 'OPEN_PLANAR' """
    #print('\nBefore:', MovRoi.ROIContourSequence[0].ContourSequence[s].ContourImageSequence[0].ReferencedSOPClassUID)
    MovRoi.ROIContourSequence[0].ContourSequence[i]    .ContourGeometricType = 'OPEN_PLANAR'
    #print('\nAfter:', MovRoi.ROIContourSequence[0].ContourSequence[s].ContourGeometricType)
    
    #print(MovRoi.ROIContourSequence[0].ContourSequence[s].ContourGeometricType)
    
    # Modify the Number of Contour Points:
    MovRoi.ROIContourSequence[0].ContourSequence[i]    .NumberOfContourPoints = f"{Npts[MovInds[i]]}"  
    
    
    # Modify the Contour Number:
    MovRoi.ROIContourSequence[0].ContourSequence[i]    .ContourNumber = f"{i+1}" 
    
    # Modify the Contour Data:
    MovRoi.ROIContourSequence[0].ContourSequence[i]    .ContourData = ContourData[MovInds[i]]
    
       
# Get the filename of the original RT-Struct file:
FixRoiFname = os.path.split(FixRoiFpath)[1]

# Create a new filename:
MovRoiFname = 'AIM_' + NewDate + '_' + NewTime + '_transformed_from_' + FixRoiFname

# Get the current working directory:
CWD = os.getcwd()

# Save the new DICOM-RTSTRUCT file:
#MovRoi.save_as(os.path.join(CWD, MovRoiFname))


# In[226]:


ContourData
Npts


# In[210]:


for i in range(len(MovInds)):
    print(f'i = {i}, MovInds[i] = {MovInds[i]}')
    
    print(ContourData[i])


# In[162]:


MovRoiFname


# In[164]:


os.getcwd()


# In[161]:


MovRoiFname = 'AIM_' + NewDate + '_' + NewTime + '_copied_from_' + FixRoiFname


# In[122]:


print('FixRoi:')
FixRoi


# In[232]:


print('MovRoi:')
MovRoi


# In[221]:


print(f'Npts = {Npts}')
print(f'3*Npts = {[3*Npts[i] for i in range(len(Npts))]}')
print('MovInds =', MovInds)


# In[154]:


print(MovRoi.StructureSetLabel)
print(MovRoi.StructureSetROISequence[0].ROIName)
print(MovRoi.StructureSetDate)
print(MovRoi.StructureSetTime)


# In[89]:


print(MovRoi.ROIContourSequence[0].ContourSequence[0])
print('*************************************************************************************************************')
print('*************************************************************************************************************')
print(MovRoi.ROIContourSequence[0].ContourSequence[0].ContourImageSequence[0])
print('*************************************************************************************************************')
print('*************************************************************************************************************')
#print(MovRoi.ROIContourSequence[0].ContourSequence[0].ContourImageSequence[0].ReferencedSOPClassUID)
#print('*************************************************************************************************************')
#print('*************************************************************************************************************')
#print(MovRoi.ROIContourSequence[0].ContourSequence[0].ContourImageSequence[0].ReferencedSOPInstanceUID)


# ### Test function that wraps up the above code:

# In[42]:


import CreateMovRoi
importlib.reload(CreateMovRoi)
from CreateMovRoi import CreateMovRoi

MovRoi = CreateMovRoi(FixRoiFpath=FixRoiFpath, MovDicomDir=MovDicomDir, 
                      MovPtsArr_ICS=OutPtsArr_ICS, Debug=False)


# In[43]:


MovRoi


# In[17]:


print(f'Npts = {Npts}')
print(f'3*Npts = {[3*Npts[i] for i in range(len(Npts))]}')
print('MovInds =', MovInds)


# # Sagittal views of Fixed and Moving Images

# In[189]:


FixOrigin, FixDirs, FixSpacings, FixDims = GetImageAttributes(DicomDir=FixDicomDir, Package='pydicom')
MovOrigin, MovDirs, MovSpacings, MovDims = GetImageAttributes(DicomDir=MovDicomDir, Package='pydicom')

print('FixDims:', FixDims)
print('\nMovDims:', MovDims)

print('\nFixDirs:\n', FixDirs[0:3], '\n', FixDirs[3:6], '\n', FixDirs[6:])
print('\nMovDirs:\n', MovDirs[0:3], '\n', MovDirs[3:6], '\n', MovDirs[6:])

# Check the aspect ratios in different views:
FixAxAR = FixSpacings[1]/FixSpacings[0]
MovAxAR = MovSpacings[1]/MovSpacings[0]

FixSagAR = FixSpacings[1]/FixSpacings[2]
MovSagAR = MovSpacings[1]/MovSpacings[2]
#FixSagAR = FixSpacings[2]/FixSpacings[1]
#MovSagAR = MovSpacings[2]/MovSpacings[1]

FixCorAR = FixSpacings[2]/FixSpacings[0]
MovCorAR = MovSpacings[2]/MovSpacings[0]

print('\nFixAxAR =', FixAxAR)
print('FixSagAR =', FixSagAR)
print('FixCorAR =', FixCorAR)
print('\nMovAxAR =', MovAxAR)
print('MovSagAR =', MovSagAR)
print('MovCorAR =', MovCorAR)

# Create 3D array of DICOM images:
Fix3D = np.zeros(FixDims)
Mov3D = np.zeros(MovDims)

for i in range(len(FixDicoms)):
    Fix3D[:, :, i] = FixDicoms[i].pixel_array

for i in range(len(MovDicoms)):
    Mov3D[:, :, i] = MovDicoms[i].pixel_array
    


# In[73]:


# plot 3 orthogonal slices
plt.subplots(1, 3, figsize=(14, 5))

a1 = plt.subplot(1, 3, 1)
plt.imshow(Fix3D[:, :, FixDims[2]//2])
a1.set_aspect(FixAxAR)

a2 = plt.subplot(1, 3, 2)
plt.imshow(Fix3D[:, FixDims[1]//2, :])
a2.set_aspect(FixSagAR)

a3 = plt.subplot(1, 3, 3)
plt.imshow(Fix3D[FixDims[0]//2, :, :].T)
a3.set_aspect(FixCorAR)

plt.show()


# In[114]:


print(FixDims[1]/FixDims[2])
print(FixDims[1]//FixDims[2])
print(int(np.floor(FixDims[1]/FixDims[2])))


# In[116]:


np.arange(0, FixDims[1]+1, dSag)


# In[109]:


np.arange(0, 10, 10/5)


# In[119]:


np.arange(0, FixDims[1], FixDims[1]/FixDims[2])


# In[121]:


np.arange(0, FixDims[1]+0.01, FixDims[1]//FixDims[2])


# In[125]:


np.linspace(0, FixDims[1]-1, num=FixDims[2], endpoint=True)


# In[126]:


np.linspace(0, FixDims[1]-1, num=FixDims[2], endpoint=True, retstep=False, dtype=int)


# In[131]:


# Sagittal plots:

Nrows = FixDims[2] # same as the number of slices
Nrows = FixDims[2]//2
Ncols = 1

# Define the slice thickness along sagital cuts:
#dSag = int(np.floor(FixDims[0]/FixDims[2])) # same as below
dSag = FixDims[0]//FixDims[2] # same as above

# Create list of indices for the sagittal slices:
#yInds = np.arange(0, FixDims[0]+1, dSag) # better to use linspace..
yInds = np.linspace(0, FixDims[1]-1, num=Nrows, endpoint=True, retstep=False, dtype=int)


Rotate = False
Rotate = True

plt.subplots(Nrows, Ncols, figsize=(5, 5*Nrows))
#plt.subplots(Nrows, Ncols, figsize=(5, 50))

i = 0

for s in range(Nrows):
    i = i + 1 # increment sub-plot number
    
    #print(f'\nyInd = {yInds[s]}')
    
    if Rotate:
        arr = np.rot90(Fix3D[:, yInds[s], :])
    else:
        arr = Fix3D[:, yInds[s], :]
    
    ax1 = plt.subplot(Nrows, Ncols, i)
    plt.imshow(arr, cmap=plt.cm.Greys_r);
    plt.title(f'Fixed slice {s+1}/{Nrows}')
    plt.axis('off')
    if Rotate:
        ax1.set_aspect(1/FixSagAR)
    else:
        ax1.set_aspect(FixSagAR)


# In[219]:


FixNda = sitk.GetArrayFromImage(FixIm)

print('FixDims         =', FixDims)
print('FixNda.shape    =', FixNda.shape)
print('FixIm.GetSize() =', FixIm.GetSize())
print('')
print('FixDirs              =\n', FixDirs)
print('\nFixIm.GetDirection() =\n', FixIm.GetDirection())
print('')
print(FixDirs[0:2])
print([FixDirs[0], FixDirs[2]])
print(FixDirs[1:3])

print('\n', type(FixIm.GetDirection()))
#print('\n', type(list(FixIm.GetDirection())))
print('\n', type(FixDirs))

if False:
    #FixDirs = FixIm.GetDirection()
    #FixDirs = list(FixIm.GetDirection())
    FixDirs = [FixIm.GetDirection()[i] for i in range(len(FixIm.GetDirection()))]

    print('\nFixDirs =\n', FixDirs)

    a = [1, 2, 3, 5, 6, 7]
    #a = list([1, 2, 3, 5, 6, 7])

    for i in range(len(a)):
        ind = a[i]

        #print(ind)

        FixDirs[ind] = - FixDirs[ind]

    print('\nFixDirs =\n', FixDirs)
    
if True:
    #FixDirs = FixIm.GetDirection()
    #FixDirs = list(FixIm.GetDirection())
    FixDirs = [FixIm.GetDirection()[i] for i in range(len(FixIm.GetDirection()))]

    print('\nFixDirs =\n', FixDirs)

    a = [1, 2, 3, 5, 6, 7]
    #a = list([1, 2, 3, 5, 6, 7])

    for i in a:
        FixDirs[i] = - FixDirs[i]

    print('\nFixDirs =\n', FixDirs)


# In[223]:


import RegUtilityFuncs
importlib.reload(RegUtilityFuncs)
import RegUtilityFuncs as ruf

# Chose which slices to plot:
plot_slices = -1 # plot all
#plot_slices = [14]
#plot_slices = [128]

# Choose the perspective:
perspective = 'axial'
perspective = 'sagittal'
perspective = 'coronal'

# Choose whether to export figure:
export_fig = True
#export_fig = False


# Create filename for exported figure:
fig_fname = time.strftime("%Y%m%d_%H%M%S", time.gmtime()) + '_' + CoordSys             +'_reg_result_using_' + package + '_' + perspective + '.png'

ruf.display_all_sitk_images_and_reg_results_with_all_contours_v2(fix_im=FixIm, mov_im=MovIm, reg_im=RegIm,
                                                                 fix_pts=InPtsArr_ICS, mov_pts=OutPtsArr_ICS,
                                                                 export_fig=export_fig,
                                                                 export_fname=fig_fname,
                                                                 plot_slices=plot_slices,
                                                                 perspective=perspective)


# In[167]:


( (14 + 1)/30 )*(256)
( (29 + 1)/30 )*(256)


# ## Older stuff below...

# In[ ]:


# Compute the deformation field:
""" Running this in Anaconda Jupyter will probably kill the kernel.  If so, run in PyCharm. """
#DefField = ruf.ComputeDeformationField(MovingImage=MovingIm, TransformFilter=ElastixImFilt)

