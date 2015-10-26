#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: data_structures.portal.input_elements.number
"""

Module defines the NumberInput class. 
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
NumberInput           Describes an input field that accepts a single number.
====================  ==========================================================
"""




#imports
import decimal

from .generic import GenericInput




#globals
#n/a

#classes
class NumberInput(GenericInput):
    """

    The NumberInput defines an input element that accepts a single numeric value
    from the user. 

    **A NumberInput response is a list of 1 numerical value**

    The NumberElement descends from GenericInput and tightens the ``_var_attrs``
    whitelist to the following attributes:
    
     -- main_caption
     -- r_max
     -- r_min
     -- r_steps
     -- shadow
     -- user_can_add

    Class restricts modification of all other attributes.
    Class also stipulates default values for min (zero) and max (one billion).
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    _sub_types            subtypes permitted under the API
    input_type            "number"
    r_max                 1,000,000,000 (one billion)
    r_min                 0 (zero)
    r_steps               None

    FUNCTIONS:
    check_response()      check length and fit in min-max range
    format_response()     split by comma, turn into decimals, return list
    round_to_step()       round to nearest step if ``r_steps`` is specified
    ====================  ======================================================
    """
    _sub_types = {"percent",
                  "currency",
                  "days",
                  "weeks",
                  "months",
                  "years"}
    
    def __init__(self):
        var_attrs = ("main_caption",
                     "r_max",
                     "r_min",
                     "r_steps",
                     "shadow",
                     "user_can_add")
        GenericInput.__init__(self,var_attrs)
        self.__dict__["input_type"] = "number"
        self.r_max = 1000000000
        #one billion
        self.r_min = 0
        #zero
        self.r_steps = None

    def check_response(self,proposed_response):
        """


        NumberInput.check_response(proposed_response) -> None


        Method checks for response length (must be 1 unless user_can_add)
        and that for each item in response, r_min <= item <= r_max.
        """
        result = True
        lo = decimal.Decimal("-Infinity")
        hi = decimal.Decimal("Infinity")
        if self.r_min:
            lo = decimal.Decimal(self.r_min)
        if self.r_max:
            hi = decimal.Decimal(self.r_max)
        entry_count = len(proposed_response)
        if entry_count < 1:
            result = False
        else:
            if self.user_can_add == False and entry_count > 1:
                result = False            
        if result:            
            for n in proposed_response:
                if lo <= n <= hi:
                    continue
                else:
                    result = False
                    break
        return result
    
    def format_response(self,raw_response):
        """


        NumberInput.format_response(raw_response) -> list

        
        Method returns a list of the decimal.Decimal objects that corresponds to
        the comma-separated values in the raw_response. 
        """
        
        result = [decimal.Decimal(n) for n in raw_response.split(",")]
        result = [self.round_to_step(n) for n in result]
        #
        return result
    
    def round_to_step(self, value):
        """


        NumberInput.round_to_step(value) -> number


        Method returns the value rounded to the nearest step.

        NOTE: Logic matches WebPortal roundToStep function
        (see Portal/blackbird_web/static/js/angular_slider.js)
        """
        rounded_value = None
        #
        if not self.r_steps:
            rounded_value = value
        else:
            lo = self.r_min
            hi = self.r_max
            #
            step = (hi - lo) / self.r_steps
            step = decimal.Decimal(step)
            remainder = value % step
            #
            if remainder > (step / 2):
                rounded_value = value + step - remainder
            else:
                rounded_value = value - remainder
        #
        return rounded_value
        
        
        

