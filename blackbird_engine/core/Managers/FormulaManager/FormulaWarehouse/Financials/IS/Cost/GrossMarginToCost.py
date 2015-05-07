#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Engine
#Module: FW.Financials.IS.Cost.GrossMarginToCost
"""

Template for a formula content module. Content modules define one (and only one)
formula function that allows a driver to modify a business unit. Drivers
retrieve a copy of the formula from the formula catalog whenever they have to
do work.

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
#n/a




#globals
formula_content = True
name = "compute cost from known gross margin."

#FORMULA NAMES SHOULD DESCRIBE THEIR ACTION IN SIMPLE LANGUAGE
#simple names make it easier to reuse functions and avoid errors when creating
#drivers

formula_author = "Ilya Podolyako"
date_created = "2015-04-10"
required_data = ["active_gross_margin"]

def func(line, business_unit, data, driver_signature):
    """

    func(line, business_unit, parameters, driver_signature) -> None

    Function performs simple cost computation. If business unit financials
    specify revenue and the business unit is alive, cost is
    rev * (1 - gross margin).

    Function performs no-op if business unit does not have a financials line
    item named 'revenue'.

    Data must include:

    -- "active_gross_margin"
    
    """
    gross_margin = float(data["active_gross_margin"])
    fins = business_unit.financials
    i_rev = None
    try:
        i_rev = fins.indexByName("revenue")
    except ValueError:
        pass
    if i_rev:
        rev = fins[i_rev].value
    if business_unit.lifeCycle.alive and rev:
        COGS = rev * (1 - gross_margin)
        line.setValue(COGS, driver_signature)
    #
    #always return None
    return None
