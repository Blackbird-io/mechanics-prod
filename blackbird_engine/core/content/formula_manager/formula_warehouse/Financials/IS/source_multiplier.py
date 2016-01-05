#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Engine
#Module: FW.Financials.IS.SourceMultiplier
"""

Content module for a formula that sets the line to a product of source value
and multiplier. 

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
name = "set line based on source value and multiplier."


#FORMULA NAMES SHOULD DESCRIBE THEIR ACTION IN SIMPLE LANGUAGE
#simple names make it easier to reuse functions and avoid errors when creating
#drivers

formula_author = "Ilya Podolyako"
date_created = "2015-04-10"
required_data = ["source_line_name",
                 "source_multiplier"]

def func(line, business_unit, data, driver_signature):
    """

    func(line, business_unit, parameters, driver_signature) -> None

    Function sets line value to product of source and multiplier. If min or max
    specified, function cuts off line.value to fit in the [min,max] range.
    Function then applies descriptive tags and any new tags optionally included in
    data.

    No-op if source line value is None

    Data must include:

    -- "source_multiplier"    |   line.value == source.value * source_multiplier
    -- "source_line_name"     |   name of line that provides source value

    Data can include:

    -- "new_optional_tags"    |   list of tags to add to line after value set
    -- "min"                  |   floor value for line
    -- "max"                  |   ceiling value for line
    """
    #
    fins = business_unit.financials.income
    source_line = fins.find_first(data["source_line_name"])

    if source_line.value is not None:
        
        new_val = source_line.value * data["source_multiplier"]

        floor = data.get("min")
        ceiling = data.get("max")
        if floor:
            new_val = max(new_val, floor)
        if ceiling:
            new_val = min(new_val, ceiling)

        line.setValue(new_val, driver_signature)

        line.tag("fixed expense")
        line.tag("estimated")

        new_optional_tags = data.get("new_optional_tags")
        if new_optional_tags:
            line.tag(*new_optional_tags, field = "opt")
    #
    # Always return None
    return None
