#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: DataStructures.Analysis.Inputs.DateInput
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
from .Number import NumberInput




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

    def check_response(self,proposed_response):
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
            lo = datetime.date(r_min.split("-"))
        if self.r_max:
            hi = datetime.date(r_max.split("_"))
        entry_count = len(proposed_response)
        if entry_count < 1:
            result = False
        else:
            if entry_count > 1 and self.user_can_add == False:
                result = False            
        if result:            
            for entry in proposed_response:
                n = datetime.date(entry.split("-"))
                if lo <= n <= hi:
                    continue
                else:
                    result = False
                    break
        return result
    
    def format_response(self,raw_response):
        """


        DateInput.format_response(raw_response) -> list

        
        Method splits raw_response by comma and returns list of entries. 
        """
        result = raw_response.split(",")
        return result
