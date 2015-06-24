#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: Header
"""

Module defines Header class. 

====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
Header

====================  ==========================================================
"""




#imports
import time
import BBExceptions

from .Equalities import Equalities




#globals
#n/a
###adding blah commentary

#classes
class Header(Equalities):
    """

    General header object for the Blackbird environment. Records identifying
    information about the object for use by both machine and human interpreters.
    Header also includes a blank "profile" dictionary that various processes may
    fill out at runtime.

    Timestamps used in the header and throughout the Blackbird environment are
    formatted as seconds since the Epoch. 

    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================
    
    DATA:
    dateCreated
    dateModified
    sessionAuthorName
    sessionAuthorID
    businessName
    businessID
    nickname
    profile               dict
    startDate
    endDate

    FUNCTIONS:
    setDateCreated()      sets date created
    
    ====================  ======================================================
    """

    keyAttributes = []    
    irrelevantAttributes = ["allTags","dateCreated", "dateModified",
                            "skipPrefixes","startDate", "endDate"]
    
    def __init__(self):
        self.dateCreated = time.time()
        self.dateModified = None
        self.sessionAuthorName = None
        self.sessionAuthorID = None
        self.businessName = None
        self.businessID = None
        self.nickname = None
        self.profile = {}
        self.startDate = None
        self.endDate = None

    def setDateCreated(self,newDate):
        """
        Use to establish uniform dateCreated in batch jobs. 
        """
        self.dateCreated = newDate
