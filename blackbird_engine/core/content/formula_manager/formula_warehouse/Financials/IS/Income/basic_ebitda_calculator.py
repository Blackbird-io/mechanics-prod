#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Engine
#Module: FW.Financials.IS.Income.BasicEBITDACalculator
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
name = "basic ebitda calculator"

#FORMULA NAMES SHOULD DESCRIBE THEIR ACTION IN SIMPLE LANGUAGE
#simple names make it easier to reuse functions and avoid errors when creating
#drivers

formula_author = "Ilya Podolyako"
date_created = "2015-04-02"
required_data = []

def func(line, business_unit, data, driver_signature):
    """

    func(line, business_unit, parameters, driver_signature) -> None

    Function calculates unit EBITDA based on stated financials. Function
    automatically finds lines necessary for calculation: revenue, cogs, opex
    and sga. Checks if summaries for these lines are available, otherwise
    uses the top-level versions. Also checks if the financials include d&a
    and adds that item back if it's included in the four main components.

    Data must include:

    [no external data necessary]    
    """
    bu = business_unit
    line_rev = bu.financials.income.find_first("revenue")
    line_cogs = bu.financials.income.find_first("cogs")
    line_cost = bu.financials.income.find_first("cost")

    line_cost = line_cogs or line_cost
    
    line_opex = bu.financials.income.find_first("operating expense")
    line_sga = bu.financials.income.find_first("sg&a")
    line_da = bu.financials.income.find_first("d&a")

    def val(line):
        result = 0
        if line:
            result = line.value or 0
        return result

    ebitda = val(line_rev) - val(line_cost) - val(line_opex) - val(line_sga)
    if line_da:
        ebitda = val(line_da)
        line.tag("d&a added back")
        # We should really make EBITDA a function of net income to make sure we
        # are not double-counting addbacks.
    
    line.set_value(ebitda, driver_signature)

    # Always return None
    return None
