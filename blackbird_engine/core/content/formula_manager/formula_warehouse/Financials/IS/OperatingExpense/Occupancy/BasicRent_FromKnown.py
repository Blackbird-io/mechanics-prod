#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Engine
#Module: FW.Financials.IS.OpEx.Occupancy.BasicRent_FromKnown
"""

Content module for a formula that sets rent line item to a known value. 

====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
date_created          str in "YYYY-MM-DD"l; date when author wrote module
formula_content       bool; always True for content modules, else catalog skips
formula_author        str; name of person who wrote the module
name                  str; name of formula defined by module

FUNCTIONS:
func()                modifies line and /or business unit on behalf of driver

CLASSES:
n/a
====================  ==========================================================
"""




#imports
import datetime




#globals
formula_content = True
name = "set rent to known value."

#FORMULA NAMES SHOULD DESCRIBE THEIR ACTION IN SIMPLE LANGUAGE
#simple names make it easier to reuse functions and avoid errors when creating
#drivers

formula_author = "Ilya Podolyako"
date_created = "2015-04-10"
required_data = ["monthly_rent"]

def func(line, business_unit, data, driver_signature):
    """

    func(line, business_unit, parameters, driver_signature) -> None

    Function sets line value to monthly_rent from data and adds some descriptive
    tags. 

    Data must include:

    -- "monthly_rent"
    """
    #
    base_rent = data["monthly_rent"]
    line.setValue(base_rent, driver_signature)
    line.tag("run-rate")
    line.tag("cash rent")
    line.tag("non-straight-line")
    line.tag("non-GAAP")
    #
    #always return None
    return None
