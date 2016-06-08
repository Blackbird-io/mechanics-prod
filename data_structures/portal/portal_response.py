# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL
# Blackbird Environment
# Module: Analysis.PortalResponse
"""

Module defines PortalResponse class.

====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
PortalResponse        An array (list) of 1 to 5 ResponseElement objects
====================  ==========================================================
"""




#imports
from .schema import Schema




class PortalResponse(list, Schema):
    """

    Class defines an array for holding ResponseElement objects, per Engine API.
    Class inherits the Schema attribute restrcition whitelist. By default, the
    PortalResponse class has no attributes and the whitelist is empty.     
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    n/a
    
    FUNCTIONS:
    n/a
    ====================  ======================================================
    """
    def __init__(self):
        list.__init__(self)
        Schema.__init__(self, [])
    
