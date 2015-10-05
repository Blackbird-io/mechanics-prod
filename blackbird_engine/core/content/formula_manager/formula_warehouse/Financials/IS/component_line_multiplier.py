#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Engine
#Module: FW.Financials.IS.component_line_multiplier
"""

Content module for a formula that sets object value to product of a multiplier
and a line from a particular component. 

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
name = "product of line from named component."


#FORMULA NAMES SHOULD DESCRIBE THEIR ACTION IN SIMPLE LANGUAGE
#simple names make it easier to reuse functions and avoid errors when creating
#drivers

formula_author = "Ilya Podolyako"
date_created = "2015-06-22"
required_data = ["component_name",
                 "source_line_name",
                 "source_multiplier"]

def func(line, business_unit, data, driver_signature):
    """

    func(line, business_unit, parameters, driver_signature) -> None

    Function sets line value to product of source and multiplier. Function pulls
    source line from component with the specified name. If data includes type,
    function pulls source only if source type matches.
    
    If min or max specified, function cuts off line.value to fit in the
    [min,max] range. Function then applies descriptive tags and any new tags
    optionally included in data.

    Data must include:

    -- "component_name"       |   name of component that provides source line
    -- "source_multiplier"    |   line.value == source.value * source_multiplier
    -- "source_line_name"     |   name of line that provides source value

    Data can include:

    -- "max"                  |   ceiling value for line
    -- "min"                  |   floor value for line
    -- "new_optional_tags"    |   list of tags to add to line after value set
    -- "required_type"        |   only pull line value if component type matches
    """
    #
    source_name = data["component_name"]
    source_bbid = business_unit.components.by_name[source_name]
    #<------------------------------------------------------------------should make no-op if component doesnt exist
    source_unit = business_unit.components[source_bbid]
    fins = source_unit.financials
    #
    type_req = data.get("required_type")
    if type_req:
        source_type = getattr(source_unit, "type")
        if source_type != type_req:
            raise AnalyticalError
            #or do nothing? return?
    #
    i = fins.indexByName(data["source_line_name"])
    source_line = fins[i]
    new_val = source_line.value * data["source_multiplier"]
    floor = data.get("min")
    ceiling = data.get("max")
    if floor:
        new_val = max(new_val, floor)
    if ceiling:
        new_val = min(new_val, ceiling)
    line.setValue(new_val, driver_signature)
    line.tag("estimated")
    new_optional_tags = data.get("new_optional_tags")
    if new_optional_tags:
        line.tag(*new_optional_tags, field = "opt")
    #
    #always return None
    return None
