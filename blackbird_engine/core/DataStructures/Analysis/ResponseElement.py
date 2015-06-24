#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: Analysis.ResponseElement
"""

Module defines ResponseElement class that uses Schema whitelisting to restrict
attributes to those in the Engine API.

====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
ResponseElement       An array (list) of 1 to 5 ResponseElement objects
====================  ==========================================================
"""




#imports
from .Schema import Schema




class ResponseElement(Schema):
    """

    Class defines an array for holding ResponseElement objects, per Engine API.
    Class inherits the Schema attribute restrcition whitelist. By default, the
    PortalResponse class has no attributes and the whitelist is empty.     
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    input_type
    input_sub_type
    response
    
    FUNCTIONS:
    n/a
    ====================  ======================================================
    """
    def __init__(self):
        whitelist = ["input_type",
                     "input_sub_type",
                     "response"]
        Schema.__init__(self, whitelist)
        self.input_type = None
        self.input_sub_type = None
        self.response = None
    
