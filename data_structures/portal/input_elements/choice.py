# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL
# Blackbird Environment
# Module: data_structures.portal.input_elements.choice
"""

Module defines the ChoiceInput class. Portal displays ChoiceInput objects as
multiple choice questions or drop-down menus, depending on context. 

====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
ChoiceInput           Describes a field where user selects response from menu
====================  ==========================================================
"""




#imports
from .generic import GenericInput




#globals
#n/a

#classes
class ChoiceInput(GenericInput):
    """

    The ChoiceInput defines an input element that forces user to select a
    response from a menu of options. 

    **A ChoiceInput response is a list of 1 or more items from ``entries``**

    The ChoiceInput descends from GenericInput and tightens the ``_var_attrs``
    whitelist to the following attributes:

     -- allow_other
     -- entries
     -- main_caption
     -- multi
     -- shadow

    Class restricts modification of all other attributes.

    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    allow_other           bool; False by default, can user input freeform text
    input_type            "number"
    entries               list; options that user can select
    main_caption          string; appears above drop or radio widget 
    multi                 bool; False by default, can user select 2+ options
    shadow                string; light text in widget before user action

    FUNCTIONS:
    check_response()      checks whether response is in entries and correct len
    format_response()     splits string along commas
    ====================  ======================================================
    """
    def __init__(self):
        var_attrs = ("allow_other",
                     "entries",
                     "main_caption",
                     "multi",
                     "shadow")
        GenericInput.__init__(self,var_attrs)
        self.__dict__["input_type"] = "choice"
        self.entries = ["None","None"]
        self.multi = False

    def check_response(self, proposed_response):
        """


        ChoiceElement.check_response(proposed_response) -> bool


        When instance.multi == False, method returns True when proposed_response
        has one item; item must be in entries unless instance.allow_other ==
        True.

        When instance.multi == True, method allows proposed_response to be any
        non-zero length. If instance.allow_other is True, the last item in
        proposed_response can be external, otherwise all items must be in
        entries.
        """
        result = True
        entry_count = len(proposed_response)
        if entry_count == 0:
            result = False
        else:
            if self.multi:
                pass
                #result can be any length greater than 0
            else:
                if not entry_count == 1:
                    result = False
        if result:
            if self.allow_other:
                selections = proposed_response[:-1]
                #if allow_other, last item can be freeform
            else:
                selections = proposed_response
            external = set(selections) - set(self.entries)
            if external:
                result = False
                #selections must be items from entries
        return result
        
    def format_response(self, raw_response):
        """


        ChoiceElement.format_response(raw_response) -> list


        Method splits string along commas (assumes input of "a,b,c ..."
        indicates [a,b,c ... ]). 
        """
        result = raw_response.split(",")
        return result
        




        




