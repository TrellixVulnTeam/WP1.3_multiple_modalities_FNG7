# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 13:57:32 2020

@author: ctorti
"""



def GetOutputPoints(MovingIm):
    """ Convert OutputPts generated by Transformix into an array of an array
    of points for each slice in MovingIm, using the z index from 
    MovingOutputIndex and the (x,y) points from OutputPoint. """
    from ParseTransformixOutput import ParseTransformixOutput
    from PCStoICS import PCStoICS
    
    PtNos, InInds, InPts_PCS,\
    FixOutInds, OutPts_PCS,\
    Defs_PCS, MovOutInds = ParseTransformixOutput()
    
    """ 12/06/20: 
        I've yet to make sense of the indices and points generated by 
        Transformix - especially the negative z-indices.  For example, if the 
        first contour is located in the 14th slice (13th counting from 0), the 
        following z-indices are found in outputpoints.txt:
            InputIndex[2] = 3 
            FixedOutputIndex[2] = -8
            MovingOutputIndex[2] = 2
            
        So I've added an argument 'ShiftZind' to allow for adding an arbitrary
        shift to the z-index used to create the array of output points.
    """
    
    
    # Convert InPts_PCS and OutPts_PCS to ICS:
    InPts_ICS = PCStoICS(Pts_PCS=InPts_PCS, SitkIm=MovingIm)
    OutPts_ICS = PCStoICS(Pts_PCS=OutPts_PCS, SitkIm=MovingIm)
    
    
    # Initialise OutPtsArr_PCS and OutPtsArr_ICS by creating an array of empty 
    # arrays with length equal to the number of slices in MovingIm:
    OutPtsArr_PCS = []
    [OutPtsArr_PCS.append([]) for i in range(MovingIm.GetSize()[2])]
    
    OutPtsArr_ICS = []
    [OutPtsArr_ICS.append([]) for i in range(MovingIm.GetSize()[2])]
    
    P = len(PtNos)
    
    for p in range(P):
        # Get the slice index for this point:
        s = MovOutInds[p][2]
        
        OutPtsArr_PCS[s].append(OutPts_PCS[p])
        
        """ Note: The input Pts_PCS for PCStoICS() needs to be an array of 
        points, so if only converting a single point, the Pts_PCS must have 
        square brackets around it to turn it into an array of length 1.
        And the output must also be indexed by [0] to get point in form [x,y,z]
        rather than [[x,y,z]].
        """
        OutPtsArr_ICS[s].append(PCStoICS(Pts_PCS=[OutPts_PCS[p]], SitkIm=MovingIm)[0])
        
    
    Defs_ICS = [[OutPts_ICS[p][i] - InPts_ICS[p][i] for i in range(3)] for p in range(P)]
        
        
    return PtNos, InInds, InPts_PCS, InPts_ICS,\
           FixOutInds, OutPts_PCS, OutPts_ICS,\
           Defs_PCS, Defs_ICS, MovOutInds,\
           OutPtsArr_PCS, OutPtsArr_ICS
