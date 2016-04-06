#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: data_structures.portal.input_elements.time_range
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
TimeRangeInput        Describes field that collects a low and high date value
====================  ==========================================================
"""




#imports
import re

from .number_range import NumberRangeInput




#globals
#n/a

#classes
class TimeRangeInput(NumberRangeInput):
    """

    The TimeRangeInput defines an input element where a user must specify two
    points in wall time. 

    **A TimeRangeInput response is a list of 2 strings in "hh:mm:ss" format**

    The TimeRangeInput object descends from NumberRangeInput and uses the same
    ``_var_attrs`` whitelist.
    
    Class also stipulates default values for min (midnight) and max (one second
    before midnight). 
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    input_type            "time-range"
    r_max                 "23:59:59" (one second before midnight)
    r_min                 "00:00:00" (midnight)

    FUNCTIONS:
    check_response()      method checks that each range is within min and max
    format_response()     method uses regular expressions to select range lists
    ====================  ======================================================
    """
    def __init__(self):
        NumberRangeInput.__init__(self)
        self.__dict__["input_type"] = "time-range"
        self.r_max = "23:59:59"
        #one second before midnight
        self.r_min = "00:00:00"
        #midnight

    def check_response(self,proposed_response):
        """


        TimeRangeInput.check_response(proposed_response) -> None


        Method checks for response length (must be 1 unless user_can_add)
        and that for each (a,b) item in response, r_min <= a <= b <= r_max.
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
            for pair_of_entries in proposed_response:
                (a,b) = pair_of_entries.split(",")
                a = a.lstrip()
                b = b.lstrip()
                a_pieces = [int(x) for x in a.split(":")]
                b_pieces = [int(x) for x in b.split(":")]
                a_date = datetime.time(*a_pieces)
                b_date = datetime.time(*b_pieces)
                if lo <= a_date <= b_date <= hi:
                    continue
                else:
                    result = False
                    break
        return result
    
    def format_response(self,raw_response):
        """


        DateRangeInput.format_response(raw_response) -> list

        
        Method returns a list of len-2 (a,b) lists.
        Method expects raw response in "[HH:MM:SS, HH:MM:SS],[HH:MM:SS,
        HH:MM:SS] ..." format; method is indifferent to the type of bracket
        and whitespace separators. 
        """
        date_pattern = ""
        date_pattern += r"[\d]{2,2}:[\d]{1,2}:[\d]{1,2}"
        date_pattern += r"[\s]*,[\s]*"
        date_pattern += r"[\d]{2,2}:[\d]{1,2}:[\d]{1,2}"
        adj_response = re.findall(date_pattern,raw_response)
        result = []
        for pair_of_strings in adj_response:
            (a,b) = pair_of_strings.split(",")
            a = a.lstrip()
            b = b.lstrip()
            clean_strings = [a,b]
            result.append(clean_strings)
        return result


