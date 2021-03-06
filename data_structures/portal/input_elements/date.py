# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL
# Blackbird Environment
# Module: data_structures.portal.input_elements.date
"""

Module defines DateInput class. Class descends from NumberInput and
accepts a single calendar date value in "YYYY-MM-DD" format. 

====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
DateInput             Describes field that collects a low and high date value
====================  ==========================================================
"""




#imports
import datetime

from tools import parsing as parsing_tools

from .number import NumberInput




#globals
#n/a

#classes
class DateInput(NumberInput):
    """

    The DateInput defines an input element where a user must specify a single
    calendar date.

    **A DateInput response is a list of 1 string in "YYYY-MM-DD" format**

    The DateInput class descends from NumberInput and uses the same
    ``_var_attrs`` whitelist.
    
    Class also stipulates default values for min (January 1, 1970) and max
    (January 1, 2036).
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    input_type            "date"
    r_max                 "2036-01-01" (January 1, 2036)
    r_min                 "1970-01-01" (January 1, 1970)

    FUNCTIONS:
    check_response()      checks that string can turn into date obj w/in range
    format_response()     splits string along commas
    ====================  ======================================================
    """
    def __init__(self):
        NumberInput.__init__(self)
        self.__dict__["input_type"] = "date"
        self.r_max = "2036-01-01"
        #January 1, 2036
        self.r_min = "1970-01-01"
        #January 1, 1970

    def check_response(self, proposed_response):
        """


        DateInput.check_response(proposed_response) -> None


        Method checks for response length (must be 1 unless user_can_add).
        Method then checks that each item in reponse can make a datetime.date()
        object and for the corresponding date objects, r_min <= item <= r_max.
        """

        result = True
        lo = datetime.date.fromordinal(1)
        hi = datetime.date.fromordinal(1000000)
        #Nov. 28, 2738
        if self.r_min:
            lo = parsing_tools.date_from_iso(self.r_min)
        if self.r_max:
            hi = parsing_tools.date_from_iso(self.r_max)
        entry_count = len(proposed_response)
        if entry_count < 1:
            result = False
        else:
            if entry_count > 1 and self.user_can_add is False:
                result = False            
        if result:            
            for entry in proposed_response:
                n = parsing_tools.date_from_iso(entry)
                if lo <= n <= hi:
                    continue
                else:
                    result = False
                    break
        return result

    def format_response(self, raw_response):
        """


        GenericInput.format_response(raw_response) -> list


        Method turns raw_response into an object that satisfies the Engine API
        specifications for a ResponseElement of the instance's input type and
        sub_type.

        The default, most-basic version of a ResponseElement-compatible object
        is a len-1 list of the raw_response.

        Descendant classes may customize the first step of the routine to
        include more complex processing. For example, a range class would split
        the string along a comma into two component strings.
        """
        if self.user_can_add:
            adj_response = raw_response
        else:
            adj_response = [raw_response]

        return adj_response
