#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Engine
#Module: FormulaWarehouse.Financials.IS.Revenue.MonthlyUnitRevenue.__init__
"""

Content module that defines a formula function that allows a driver to modify
a business unit. 

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
name = "monthly unit revenue over lifecycle."

#FORMULA NAMES SHOULD DESCRIBE THEIR ACTION IN SIMPLE LANGUAGE
#simple names make it easier to reuse functions and avoid errors when creating
#drivers

formula_author = "Ilya Podolyako"
date_created = "2015-04-02"
required_data = ["annual_rev_per_mature_unit"]

def func(line, business_unit, data, driver_signature):
    """

    func(line, business_unit, parameters, driver_signature) -> None

    Function sets line value to 1/12th the annual unit revenue, adjusted for
    life stage. Function assumes that during growth stage, revenue ratably
    scales from 0 to mature amount, and that during decline stage, revenue
    ratably scales from mature amount to 0.

    Data must include:

    "annual_rev_per_mature_unit" 
    
    """
    stage_number = business_unit.lifeCycle.currentLifeStageNumber
    stage = business_unit.lifeCycle.allLifeStages[stage_number]
    annual_revenue = data["annual_rev_per_mature_unit"]
    monthly_revenue = annual_revenue/12
    if stage.name == "maturity":
        line.setValue(monthly_revenue, driver_signature)
        #
    elif stage.name == "growth":
        growth_adjustment = (business_unit.lifeCycle.percentDone / 
                             (stage.ends - stage.starts))
        adj_growth_revenue = growth_adjustment * monthly_revenue
        line.setValue(adj_growth_revenue, driver_signature)
        #
    elif stage.name == "decline":
        decline_adjustment = ((100 - business_unit.lifeCycle.percentDone) / 
                              (stage.ends - stage.starts))
        adj_decline_revenue = decline_adjustment * monthly_revenue
        line.setValue(adj_decline_revenue, driver_signature)
        #
    #always return None
    return None
