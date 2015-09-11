#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: Controllers.controller
"""

Module defines GenericController class.  
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
GenericController     shell for mqr message processing
====================  ==========================================================
"""




#imports
from DataStructures.Platform.Messenger import Messenger




#globals
#n/a

#classes
class GenericController:
    """

    This class provides a basic shell for objects that select focal points.
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    MR                    instance of Messenger class

    FUNCTIONS:
    process()             takes MQR message, clears instance cache, unpacks msg
    ====================  ======================================================
    """
    def __init__(self):
        self.MR = Messenger()

    def process(self,msgIn):
        """

        GenericController.process(msgIn) -> None

        Method takes an mqr message and unpacks it
        """
        self.MR.clearMessageIn()
        self.MR.clearMessageOut()
        self.MR.clearMQR()
        self.MR.receive(msgIn)
        self.MR.unpackMessage()

