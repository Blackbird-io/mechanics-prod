#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Engine
#Module: FW.Financials.IS.OpEx.Occupancy.Security_EstimatedFromRent
"""

Content module for a formula that sets security to a percentage of rent.

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
name = "estimate security expense from known rent value."

#FORMULA NAMES SHOULD DESCRIBE THEIR ACTION IN SIMPLE LANGUAGE
#simple names make it easier to reuse functions and avoid errors when creating
#drivers

formula_author = "Ilya Podolyako"
date_created = "2015-04-10"
required_data = ["min_monthly_security",
                 "percent_of_rent"]

def func(line, business_unit, data, driver_signature):
    """

    func(line, business_unit, parameters, driver_signature) -> None

    Function sets line to the larger of min or specified percent of rent.
    Function also applies descriptive tags. 

    Data must include:

    -- "min_monthly_security"
    -- "percent_of_rent"
    """
    #
    fins = business_unit.financials
    i_rent = fins.indexByName("Rent")
    rent = fins[iRent].value
    security = rent * data["percent_of_rent"]
    security = max(util, data["min_monthly_security"])
    line.setValue(util, driver_signature)
    line.tag("percent of rent")
    line.tag("estimated")
    #
    #always return None
    return None
