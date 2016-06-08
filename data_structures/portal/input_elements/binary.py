# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL
# Blackbird Environment
# Module: data_structures.portal.input_elements.binary
"""

Module defines the BinaryInput class. 
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
BinaryInput           Describes an input field that forces user to toggle
====================  ==========================================================
"""




#imports
from .generic import GenericInput



#globals
#n/a

#classes
class BinaryInput(GenericInput):
    """

    The BinaryInput defines an input element that forces a user to toggle
    between a "True" and a "False" choice, each of which has a custom label. 

    **A BinaryInput response is a list of 1 boolean value**

    The BinaryElement descends from GenericInput and tightens the ``_var_attrs``
    whitelist to the following attributes:
    
     -- main_caption
     -- toggle_caption_false
     -- toggle_caption_true

    Class restricts modification of all other attributes.
    
    Class also stipulates default values for the true and false captions ("Yes"
    and "No", respectively).
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    input_type            "binary"
    toggle_caption_false  "No"
    toggle_caption_true   "Yes"

    FUNCTIONS:
    check_response()      check if response is a list of one caption value
    ====================  ======================================================
    """
    def __init__(self):
        var_attrs = ("main_caption",
                     "toggle_caption_false",
                     "toggle_caption_true")
        GenericInput.__init__(self,var_attrs)
        self.__dict__["input_type"] = "binary"
        self.toggle_caption_false = "No"
        self.toggle_caption_true = "Yes"

    def check_response(self, proposed_response):
        """


        BinaryInput.check_response(proposed_response) -> bool


        Method returns True if proposed_response is a list of one instance
        caption, False otherwise.

        Binary responses are lists of one caption value.
        """
        result = True
        acceptable = [self.toggle_caption_false, self.toggle_caption_true]
        if proposed_response[0] not in acceptable:
            result = False
        if result:
            if len(proposed_response) > 1:
                result = False
        return result


