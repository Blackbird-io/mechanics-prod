#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: Controllers.Protocol
"""

Module defines Protocol class.  
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
class Protocol        standard shell for a function that selects a focal point
====================  ==========================================================
"""




#imports
import time




#globals
#n/a

#classes
class Protocol:
    """

    This class provides storage and status attributes for selection functions.
    Class takes ``name`` and ``efficiency`` constructor arguments.

    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    name                  descriptive name of protocol
    efficiency            qualitative efficiency rating
    complete              bool, is the protocol complete for the model
    focalPoint            current focal point state
    pointStandard         current completion standard for focal point
    modStructure          list that shows protocol's logical steps. elaboration
                          on a traditional structure list: ``modStructure`` can
                          contain duplicative priorityLevels for protocols that
                          revisit certain areas.
                          
    select()              Abstract Method; identifies a focal point on a model
    markComplete()        Sets complete to a time stamp

    ====================  ======================================================
    """

    def __init__(self, name = None, efficiency = 1):
        self.name = name
        self.efficiency = efficiency
        self.complete = False
        self.focalPoint = None
        self.pointStandard = None
        self.modStructure = None

    def select(self):
        pass
        #abstract method, should raise an error here

    def markComplete(self):
        """

        Protocol.markComplete() -> None

        Sets self.complete to a timestamp of call
        """
        self.complete = time.time()    
