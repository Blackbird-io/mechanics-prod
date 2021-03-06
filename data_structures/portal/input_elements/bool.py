# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL
# Blackbird Environment
# Module: data_structures.portal.input_elements.bool
"""

Module defines the BoolInput class. 
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
BoolInput             Describes a check-the-box input field
====================  ==========================================================
"""




#imports
from .generic import GenericInput




#globals
#n/a

#classes
class BoolInput(GenericInput):
    """

    The BoolInput defines a check-the-box input element. The user has to check
    the box if the statement is true.

    The Engine often uses this element to verify values for estimated line
    items. In such a case, the Engine user should specify the name of the line
    in ``main_caption`` and the value they would like to verify in
    ``line_value``.

    For example, if ``main_caption`` = "Revenue" and ``value`` = 500, Portal
    will display something like:

      Revenue ......... 500 [ x ]
      
    **A BoolInput response is a list of 1 boolean value**

    The BoolElement descends from GenericInput and tightens the ``_var_attrs``
    whitelist to the following attributes:
    
     -- main_caption
     -- line_value

    Class restricts modification of all other attributes.
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    input_type            "bool"

    FUNCTIONS:
    check_response()      checks that response is list of one bool obj
    format_response()     turns raw string into a list of one bool obj
    ====================  ======================================================
    """
    def __init__(self):
        var_attrs = ("line_value",
                     "main_caption")
        GenericInput.__init__(self,var_attrs)
        self.__dict__["input_type"] = "bool"

    def check_response(self, proposed_response):
        """


        BinaryInput.check_response(proposed_response) -> bool


        Method returns True if proposed_response is a list of one instance
        caption, False otherwise.

        Binary responses are lists of one caption value.
        """
        result = True
        acceptable = [True, False]
        if proposed_response[0] not in acceptable:
            result = False
        if result:
            if len(proposed_response) > 1:
                result = False
        return result

    def format_response(self, raw_response):
        """


        BinaryInput(raw_response) -> list


        Method returns a length-1 list of bool(raw_response).

        NOTE: For result[0] == False, input must be an empty string ('').
        All other strings have a True boolean value.
        """
        val = bool(raw_response)
        if raw_response == "False":
            val = False
        
        result = [val]
        
        return result
        



