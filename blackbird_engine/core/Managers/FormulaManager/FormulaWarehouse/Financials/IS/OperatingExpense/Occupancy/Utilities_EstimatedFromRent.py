#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Engine
#Module: FW.Financials.IS.OpEx.Occupancy.Utilities_EstimatedFromRent
"""

Content module for a formula that sets utilities to a percentage of rent.

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
name = "estimate utilities from known rent value."

#FORMULA NAMES SHOULD DESCRIBE THEIR ACTION IN SIMPLE LANGUAGE
#simple names make it easier to reuse functions and avoid errors when creating
#drivers

formula_author = "Ilya Podolyako"
date_created = "2015-04-10"
required_data = ["min_monthly_utilities",
                 "max_monthly_utilities",
                 "percent_of_rent"]

def func(line, business_unit, data, driver_signature):
    """

    func(line, business_unit, parameters, driver_signature) -> None

    Function sets line to the specified percent of rent, provided result is
    within [min,max] range, otherwise sets line to bound. Function also applies
    descriptive tags. 

    Data must include:

    -- "min_monthly_utilities"
    -- "max_monthly_utilities"
    -- "percent_of_rent"
    """
    #
    fins = business_unit.financials
    i_rent = fins.indexByName("Rent")
    rent = fins[iRent].value
    util = rent * data["percent_of_rent"]
    util = max(util, data["min_monthly_utilities"])
    util = min(util, data["max_monthly_utilities"])
    line.setValue(util, driver_signature)
    line.tag("percent of rent")
    line.tag("estimated")
    #
    #always return None
    return None
