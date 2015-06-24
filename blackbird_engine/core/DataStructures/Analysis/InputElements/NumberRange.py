#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: DataStructures.Analysis.Inputs.NumberRangeInput
"""

Module defines NumberRangeInput class. Class descends from GenericInput and
accepts a pair of numeric values specified by user.

====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
NumberRangeInput      Describes field that takes a low and high numeric value 
====================  ==========================================================
"""




#imports
import re

from .Generic import GenericInput




#globals
#n/a

#classes
class NumberRangeInput(GenericInput):
    """

    The NumberRangeInput defines an input element where a user must specify a
    low and a high value.

    **A RangeInput response is a list of 2 numerical values**

    The NumberRangeElement descends from GenericInput and tightens the
    ``_var_attrs`` whitelist to the following attributes:
    
     -- main_caption
     -- r_max
     -- r_min
     -- shadow
     -- shadow_2
     -- user_can_add

    Class restricts modification of all other attributes.
    
    Class also stipulates default values for min (zero) and max (one billion).
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    input_type            "date-range"
    r_max                 1,000,000,000 (one billion)
    r_min                 0 (zero)

    FUNCTIONS:
    check_response()      method checks that each range is within min and max
    format_response()     method uses regular expressions to select range lists
    ====================  ======================================================
    """
    def __init__(self):
        var_attrs = ("main_caption",
                     "r_max",
                     "r_min",
                     "shadow",
                     "shadow_2",
                     "user_can_add")
        GenericInput.__init__(self,var_attrs)
        self.__dict__["input_type"] = "number-range"
        self.r_max = 1000000000
        #one billion
        self.r_min = 0
        #zero

    def check_response(self,proposed_response):
        """


        NumberInput.check_response(proposed_response) -> None


        Method checks for response length (must be 1 unless user_can_add)
        and that for each (a,b) item in response, r_min <= a <= b <= r_max.
        """
        result = True
        lo = decimal.Decimal("-Infinity")
        hi = decimal.Decimal("Infinity")
        if self.r_min:
            lo = decimal.Decimal(r_min)
        if self.r_max:
            hi = decimal.Decimal(r_max)
        entry_count = len(proposed_response)
        if entry_count < 1:
            result = False
        else:
            if self.user_can_add == False and entry_count > 1:
                result = False            
        if result:            
            for (a,b) in proposed_response:
                if lo <= a <= b <= hi:
                    continue
                else:
                    result = False
                    break
        return result
    
    def format_response(self,raw_response):
        """


        NumberInput.format_response(raw_response) -> list

        
        Method returns a list of len-2 (a,b) lists.
        Method expects raw response in "[a0,b0],[a1,b1] ..." format; method
        is indifferent to the type of bracket and whitespace separators. 
        """
        number_pattern = r"[\d.]+[\s,]+[\d.]+"
        adj_response = re.findall(number_pattern,raw_response)
        result = []
        for pair_of_strings in adj_response:
            (a,b) = pair_of_strings.split(",")
            pair_of_decimals = [decimal.Decimal(a), decimal.Decimal(b)]
            #decimal ignores white space
            result.append(pair_of_decimals)
        return result


