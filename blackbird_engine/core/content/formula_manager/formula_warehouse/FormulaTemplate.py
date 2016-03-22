#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Engine
#Module: FormulaWarehouse.FormulaTemplate
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
name = "Template content module for formula that does nothing."

#FORMULA NAMES SHOULD DESCRIBE THEIR ACTION IN SIMPLE LANGUAGE
#simple names make it easier to reuse functions and avoid errors when creating
#drivers

formula_author = "Annie Hall"
date_created = "2015-04-02"
required_data = ["important_parameter_1",
                 "favorite_vegetable",
                 "length_of_standard_shoelace"]

def func(line, business_unit, data, driver_signature):
    """

    func(line, business_unit, parameters, driver_signature) -> None

    [Function description]

    Data must include:

    -- "important_parameter_1"
    -- "favorite_vegetable"
    -- "length_of_standard_shoelace"
    
    """
    excel_template = None
    bb_value = None
    cell_comment = ""
    lines = dict()
    # Excel template should be a string compatible with the 3.x str.format()
    # method. The template will receive three dictionary arguments for
    # formatting: lines, parameters, and life. Each will point to Excel
    # coordinates that represent the line, parameter, or life attribute/event
    # applicable to the business_unit.
    #
    # bb_value should be set to the BB engine value for the line item this
    # formula is working on. this value is used for testing -- to compare the
    # calculated Excel value to the value in the Engine and make sure they are
    # the same.
    #
    # cell_comment is a string that will be added as an Excel comment for this
    # cell. The string can be empty, but it MUST be passed.
    #
    # At runtime, the function can locate whatever lines it deems significant
    # and drop them into the ``lines`` dictionary. Our Chef module will then
    # map these lines to their Excel coordinates at export time and build
    # links that reflect the relationship. 
    
    # Always return Excel calculation package
    return excel_template, bb_value, cell_comment, lines
