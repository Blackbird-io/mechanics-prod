#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Engine
#Module: FW.Financials.IS.MonthlyExpense_FromAnnual_Inflation
"""

Content module for a formula that computes monthly expense from an
annual number and then adjusts it by inflation, indexed annually. 

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
name = "inflation-adjusted monthly expense from known annual start."

#FORMULA NAMES SHOULD DESCRIBE THEIR ACTION IN SIMPLE LANGUAGE
#simple names make it easier to reuse functions and avoid errors when creating
#drivers

formula_author = "Ilya Podolyako"
date_created = "2015-04-10"
required_data = ["base_annual_expense",
                 "annual_inflation",
                 "ref_year"]

def func(line, business_unit, data, driver_signature):
    """

    func(line, business_unit, parameters, driver_signature) -> None

    Function computes monthly expense from base_annual_expense and inflation
    provided in data. Function then sets line value to monthly result and tags
    the line with descriptive tags. 

    Data must include:

    -- "base_annual_expense"
    -- "annual_inflation"
    -- "ref_year"    
    """
    #
    calc_year = business_unit.life.ref_date.year
    years_from_base = calc_year - data["ref_year"]
    years_from_base = max(0, years_from_base)
    inflation_multiplier = (1 + data["annual_inflation"])** years_from_base
    #
    monthly_expense = data["base_annual_expense"]/12 * inflation_multiplier
    #
    line.setValue(monthly_expense, driver_signature)
    line.tag("inflation adjusted")
    im_tag = "inflation multiplier: %s" % round(inflation_multiplier,4)
    line.tag(im_tag)
    #always return None
    return None
