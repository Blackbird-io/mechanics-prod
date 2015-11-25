#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: Analysis.Schema
"""

Module defines the Schema class. Scehma objects restrict attribute addition and
modification via a whitelist (``_var_attrs``). 

====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
Schema                Describes on-screen field where user can input a response 
====================  ==========================================================
"""




#imports
import copy

import bb_exceptions




#globals
#n/a

#classes
class Schema:
    """

    Schema objects restrict how Engine users may create or modify
    attributes. Standard assignment (``x.y = z``) syntax thus only works for
    those attributes listed in the ``_var_attrs`` whitelist.    
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    _var_attrs            tuple; names of attributes that accept new values

    FUNCTIONS:
    __setattr__()         whitelisted attrs set through superclass, else error
    ====================  ======================================================
    """
    def __init__(self,var_attrs):
        self.__dict__["_var_attrs"] = var_attrs
        
    def __setattr__(self, attr, value):
        """


        Schema.__setattr__(attr,value) -> None


        For attributes in whitelist, method delegates work to the
        ``object`` superclass (object.__setattr__()). Raises exception for
        others. 
        """
        if attr in self._var_attrs:
            object.__setattr__(self, attr, value)
        else:
            c = "\nCannot set attribute ``%s`` on %s.\n"
            c += "Schema objects do not allow new attributes."
            c = c % (attr, self)
            raise bb_exceptions.ManagedAttributeError(c)
