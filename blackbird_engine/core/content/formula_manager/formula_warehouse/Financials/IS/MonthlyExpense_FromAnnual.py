#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Engine
#Module: FW.Financials.IS.MonthlyExpense_FromAnnual
"""

Content module for a formula that computes monthly expense from an
annual number. 

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
name = "monthly expense from known annual start."

#FORMULA NAMES SHOULD DESCRIBE THEIR ACTION IN SIMPLE LANGUAGE
#simple names make it easier to reuse functions and avoid errors when creating
#drivers

formula_author = "Ilya Podolyako"
date_created = "2015-04-10"
required_data = ["base_annual_expense"]

def func(line, business_unit, data, driver_signature):
    """


    func(line, business_unit, parameters, driver_signature) -> None


    Function computes monthly expense from base_annual_expense provided in data.
    Function then sets line value to monthly result and tags the line with
    descriptive tags. 

    Data must include:

    -- "base_annual_expense"
    """
    #
    monthly_expense = data["base_annual_expense"]/12
    #
    line.setValue(monthly_expense, driver_signature)
    line.tag("run_rate")
    #always return None
    return None
