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
    fins = bu.financials.income
    # Update pointer, keep legacy naming.
    fins.summarize()
    fins.build_tables()
    summaryPrefix = fins.SUMMARY_PREFIX
    rev = "revenue"
    cogs = "cogs"
    cost = "cost"
    opex = "operating expense"
    sga = "sg&a"
    da = "d&a"
    spots_rev = None
    spots_cogs = None
    spots_opex = None
    spots_sga = None
    spots_da = None
    def sN(name):
        result = summaryPrefix.casefold()+" "+name
        return result
    keys_dNames = list(fins.dNames.keys())
    #get keys once and freeze so dont compute on every check
    if sN(rev) in keys_dNames:
        spots_rev = fins.dNames[sN(rev)]
    else:
        spots_rev = fins.dNames[rev]
    if cogs in keys_dNames:
        if sN(cogs) in keys_dNames:
            spots_cogs = fins.dNames[sN(cogs)]
        else:
            spots_cogs = fins.dNames[cogs]
    else:
        if sN(cost) in keys_dNames:
            spots_cogs = fins.dNames[sN(cost)]
        else:
            spots_cogs = fins.dNames[cost]
    #if COGS not a line, use ``cost`` instead
    #can improve to run on tags and stuff
    if sN(opex) in keys_dNames:
        spots_opex = fins.dNames[sN(opex)]
    else:
        spots_opex = fins.dNames[opex]
    if sN(sga) in keys_dNames:
        spots_sga = fins.dNames[sN(sga)]
    else:
        spots_sga = fins.dNames[sga]
    if da in keys_dNames:
        if sN(da) in keys_dNames:
            spots_da = fins.dNames[sN(da)]
        else:
            spots_da = fins.dNames[da]
    spots_rev = list(spots_rev)
    spots_rev.sort()
    i_rev = spots_rev[0]
    spots_cogs = list(spots_cogs)
    spots_cogs.sort()
    i_cogs = spots_cogs[0]
    spots_opex = list(spots_opex)
    spots_opex.sort()
    i_opex = spots_opex[0]
    spots_sga = list(spots_sga)
    spots_sga.sort()
    i_sga = spots_sga[0]
    if spots_da:
        spots_da = list(spots_da)
        spots_da.sort()
        i_da = spots_da[0]
    else:
        i_da = None
    line_rev = fins[i_rev]
    line_cogs = fins[i_cogs]
    line_opex = fins[i_opex]
    line_sga = fins[i_sga]
    line_da = None
    if i_da:
        line_da = fins[i_da]
    def val(L):
        result = 0
        if L.value:
            result = L.value
        return result
    opProfit = val(line_rev)-val(line_cogs)-val(line_opex)-val(line_sga)
    #check if d&a is top-level; if it is, it is not in the other lines.
    #otherwise, add it back
    if line_da:
        if line_da.partOf not in fins.topLevelNames:
            ebitda = opProfit + val(line_da)
            line.tag("d&a added back")
        else:
            ebitda = opProfit
    else:
        ebitda = opProfit
    #set value to the line provided to driver
    line.setValue(ebitda, driver_signature)
    #always return None
    return None
