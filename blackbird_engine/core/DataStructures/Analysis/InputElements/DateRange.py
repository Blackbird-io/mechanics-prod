#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: DataStructures.Analysis.Inputs.DateRangeInput
"""

Module defines DateRangeInput class. Class descends from NumberRangeInput and
accepts a pair of strings in "YYYY-MM-DD" format from the user. 

====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
DateRangeInput        Describes field that collects a low and high date value
====================  ==========================================================
"""




#imports
import re

from .NumberRange import NumberRangeInput




#globals
#n/a

#classes
class DateRangeInput(NumberRangeInput):
    """

    The DateRangeInput defines an input element where a user must specify a
    low and a high date.

    **A DateRangeInput response is a list of 2 strings in "YYYY-MM-DD" format**

    The DateRangeInput object descends from NumberRangeInput and uses the same
    ``_var_attrs`` whitelist.
    
    Class also stipulates default values for min (January 1, 1970) and max
    (January 1, 2036).
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    input_type            "date-range"
    r_max                 "2036-01-01" (January 1, 2036)
    r_min                 "1970-01-01" (January 1, 1970)

    FUNCTIONS:
    check_response()      method checks that each range is within min and max
    format_response()     method uses regular expressions to select range lists
    ====================  ======================================================
    """
    def __init__(self):
        NumberRangeInput.__init__(self)
        self.__dict__["input_type"] = "date-range"
        self.r_max = "2036-01-01"
        #January 1, 2036
        self.r_min = "1970-01-01"
        #January 1, 1970

    def check_response(self,proposed_response):
        """


        DateRangeInput.check_response(proposed_response) -> None


        Method checks for response length (must be 1 unless user_can_add)
        and that for each (a,b) item in response, r_min <= a <= b <= r_max.
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
                #entry is "YYYY-MM-DD, YYYY-MM-DD" 
                (a, b) = entry.split(",")
                a = a.lstrip()
                date_a = datetime.date(a.split("-"))
                b = b.lstrip()
                date_b = datetime.date(b.split("-"))
                if lo <= date_a <= date_b <= hi:
                    continue
                else:
                    result = False
                    break
        return result
    
    def format_response(self,raw_response):
        """


        DateRangeInput.format_response(raw_response) -> list

        
        Method returns a list of len-2 (a,b) lists.
        Method expects raw response in "[YYYY-MM-DD, YYYY-MM-DD],[YYYY-MM-DD,
        YYYY-MM-DD] ..." format; method is indifferent to the type of bracket
        and whitespace separators. 
        """
        date_pattern = ""
        date_pattern += r"[\d]{4,4}-[\d]{1,2}-[\d]{1,2}"
        date_pattern += r"[\s]*,[\s]*"
        date_pattern += r"[\d]{4,4}-[\d]{1,2}-[\d]{1,2}"
        adj_response = re.findall(date_pattern,raw_response)
        result = []
        for pair_of_strings in adj_response:
            (a,b) = pair_of_strings.split(",")
            a = a.lstrip()
            b = b.lstrip()
            clean_strings = [a,b]
            result.append(clean_strings)
        return result
