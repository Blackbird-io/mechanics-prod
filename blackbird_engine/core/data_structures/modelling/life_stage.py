#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: data_structures.modelling.life_stage
"""

Module defines LifeStage class. 
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
LifeStage             objects that provide descriptions of a stage of life

====================  ==========================================================
"""




#imports
#n/a




#globals
#n/a

#classes
class LifeStage(dict):
    """

    Class defines a dictionary with two keys set at __init__: ``name`` and
    ``start``. Start should be an integer or float expressing the percentage of
    object life where the stage starts.

    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    n/a
   
    FUNCTIONS:
    n/a
    ====================  ======================================================
    """    
    def __init__(self, name, start):
        dict.__init__(self)
        self["name"] = name
        self["start"] = start
        
