# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL
# Blackbird Environment
# Module: data_structures.portal.input_elements.time
"""

Module defines TimeInput class. Class descends from NumberInput and
accepts a single wall time value in "hh:mm:ss" format. 
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
TimeInput             Describes field that collects a wall time value string
====================  ==========================================================
"""




#imports
import datetime

from .number import NumberInput




#globals
#n/a

#classes
class TimeInput(NumberInput):
    """

    The TimeInput class defines an input element where a user must specify one
    point in wall time.

    **A TimeInput response is a list of 1 string in "hh:mm:ss" format**

    The TimeInput descends from NumberInput and uses the same ``_var_attrs``
    whitelist.
    
    Class also stipulates default values for min ("00:00:00") and max
    ("23:59:59").
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    input_type            "time"
    r_max                 "23:59:59" (one second before midnight)
    r_min                 "00:00:00" (midnight)

    FUNCTIONS:
    check_response        check length, time compatibility, fit in min-max range
    format_response()     split by comma, return list
    ====================  ======================================================
    """
    def __init__(self):
        NumberInput.__init__(self)
        self.__dict__["input_type"] = "time"
        self.r_max = "23:59:59"
        #one second before midnight
        self.r_min = "00:00:00"
        #midnight

    def check_response(self,proposed_response):
        """


        TimeInput.check_response(proposed_response) -> None


        Method checks for response length (must be 1 unless user_can_add).
        Method then checks that each item in reponse can make a datetime.time
        object and for the corresponding time objects, r_min <= item <= r_max.
        """
        result = True
        lo = datetime.time()
        hi = datetime.time(23,59,59,99999)
        if self.r_min:
            lo_pieces = [int(x) for x in r_min.split(":")]
            lo = datetime.time(*lo_pieces)
        if self.r_max:
            hi_pieces = [int(x) for x in r_max.split(":")]
            hi = datetime.time(*pieces)
        entry_count = len(proposed_response)
        if entry_count < 1:
            result = False
        else:
            if entry_count > 1 and self.user_can_add == False:
                result = False            
        if result:            
            for entry in proposed_response:
                entry_pieces = [int(x) for x in entry.split(":")]
                n = datetime.time(*entry_pieces)
                if lo <= n <= hi:
                    continue
                else:
                    result = False
                    break
        return result
    
    def format_response(self,raw_response):
        """


        TimeInput.format_response(raw_response) -> list

        
        Method splits raw_response by comma and returns list of entries. 
        """
        result = raw_response.split(",")
        return result




