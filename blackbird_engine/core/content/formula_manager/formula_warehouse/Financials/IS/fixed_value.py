#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Engine
#Module: FW.Financials.IS.FixedValue
"""

Content module for a formula that sets the line to a fixed value from data.

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
name = "set line to fixed monthly value."

#FORMULA NAMES SHOULD DESCRIBE THEIR ACTION IN SIMPLE LANGUAGE
#simple names make it easier to reuse functions and avoid errors when creating
#drivers

formula_author = "Ilya Podolyako"
date_created = "2015-04-10"
required_data = ["fixed_monthly_value"]

def func(line, business_unit, data, driver_signature):
    """

    func(line, business_unit, parameters, driver_signature) -> None

    For a living unit, function sets line to the specified monthly expense.
    Function then applies descriptive tags and any new tags optionally
    included in data.

    No-op for units that are not alive.

    Data must include:

    -- "fixed_monthly_value"  |   line value

    Data can include:

    -- "new_optional_tags"    |   list of tags to add to line after value
    """
    #
    if business_unit.life.alive:
        expense = data["fixed_monthly_value"]
        line.setValue(expense, driver_signature)
        line.tag("fixed value")
        new_optional_tags = data.get("new_optional_tags")
        if new_optional_tags:
            line.tag(*new_optional_tags, field = "opt")
    #
    #always return None
    return None
