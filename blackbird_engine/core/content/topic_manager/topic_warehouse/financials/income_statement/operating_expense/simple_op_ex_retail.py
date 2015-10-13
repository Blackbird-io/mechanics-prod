#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: TW.Financials.IS.OperatingExpense.SimpleOpEx_Retail
"""

Content module that creates and inserts drivers for labor, rent, utility,
security, and it expenses at the ground unit level.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:

name
topic_content
extra_prep
requiredTags
optionalTags
applied_drivers
formula_names
question_names
scenarios

FUNCTIONS:
prepare
scenario_1
scenario_2

CLASSES:
n/a
====================  ==========================================================
"""




#imports
import copy
import datetime

import BBGlobalVariables as Globals

from data_structures.modelling.driver import Driver
from data_structures.modelling.line_item import LineItem



#globals
topic_content = True
name = "Simple Opex - Retail"
topic_author = "Ilya Podolyako"
date_created = "2015-04-10"
extra_prep = False

#standard topic prep
user_outline_label = "Operating Expense"
requiredTags = []
optionalTags = ["Technology Expense",
                "Retail",
                "EE",
                "Basic",
                "Default"]
#
applied_drivers = dict()
formula_names = []
question_names = []
scenarios = dict()
work_plan = dict()

formula_names = ["inflation-adjusted monthly expense from known annual start.",
                 "set line based on source value and multiplier.",
                 "set line to fixed monthly value."]

question_names = ["average monthly rent for a unit?",
                  "unit employee expense per year?"]

work_plan["Communications"] = 1
work_plan["Employee Expense"] = 1
work_plan["Compensation"] = 1
work_plan["IT"] = 1
work_plan["Miscellanious"] = 1
work_plan["Occupancy"] = 1
work_plan["Occupancy Expense"] = 1
work_plan["OPEX"] = 1
work_plan["Operating Expense"] = 1
work_plan["Rent"] = 1
work_plan["Rent Expense"] = 1
work_plan["Utilities"] = 1
work_plan["Security"] = 1 

#drivers:
#create each driver object used in Topic and place in applied_drivers to make
#sure they receive proper signatures and ids. Provide data and formulas
#during runtime through scenarios. At that point, topic will carry dictionaries
#that point to all relevant objects. 

#
#Driver for Employee Expense
driver_ee = Driver()
driver_ee.setName("Simple Employee Expense Driver")
driver_ee.setWorkConditions(None, None, "employee expense")
driver_ee.mustBeFirst = True
applied_drivers["EE Driver"] = driver_ee

#
#Driver for Rent
driver_rent = Driver()
driver_rent.setName("Simple Rent Driver")
driver_rent.setWorkConditions(None,None,"Rent")
driver_rent.mustBeFirst = True
applied_drivers["Rent Driver"] = driver_rent

#
#Driver for Utilities
driver_util = Driver()
driver_util.setName("Simple Utilities Driver")
driver_util.setWorkConditions(None, None, "Utilities")
driver_util.mustBeFirst = True
applied_drivers["Utilities Driver"] = driver_util

#
#Security Driver
driver_security = Driver()
driver_security.setName("Simple Security Driver")
driver_security.setWorkConditions(None, None, "Security")
driver_security.mustBeFirst = True
applied_drivers["Security Driver"] = driver_security
#
#IT Driver
driver_it = Driver()
driver_it.setName("Simple IT Driver")
driver_it.setWorkConditions(None, None, "IT")
driver_it.mustBeFirst = True
applied_drivers["IT Driver"] = driver_it

#scenarios
#
#define each scenario, then fill out scenarios dictionary at the bottom
#each scenario must conclude with either:
    #scenarios that ask a question - topic.wrap_scenario(Q)
    #scenarios that complete processing - topic.wrap_topic()
    #scenarios that respond to a user stop - topic.wrap_to_stop()

def scenario_1(topic):
    """


    scenario_1(topic) -> None


    **opening scenario**

    Scenario asks question about rent through topic.wrap_scenario() 
    """
    M = topic.MR.activeModel
    new_q = topic.questions["average monthly rent for a unit?"]
    unit_label = M.interview.work_space.get("unit label")
    if unit_label:
        new_q.context["unit_label_singular"] = unit_label["singular"]
    topic.wrap_scenario(new_q)

def scenario_2(topic):
    """


    scenario_2(topic) -> None


    Scenario asks question about employee expense through topic.wrap_scenario() 
    """
    M = topic.MR.activeModel
    Q = topic.MR.activeQuestion
    R = float(topic.get_first_answer())
    M.interview.work_space["monthly rent"] = R
    new_q = topic.questions["unit employee expense per year?"]
    unit_label = M.interview.work_space.get("unit label")
    if unit_label:
        new_q.context["unit_label_singular"] = unit_label["singular"]
    topic.wrap_scenario(new_q)

def scenario_3(topic):
    """
    """
    M = topic.MR.activeModel
    annual_unit_comp = float(topic.get_first_answer())
    M.interview.work_space["annual unit comp"] = annual_unit_comp

    #Make lines    
    l_comp = LineItem("Employee Expense")
    l_comp.tag("Adjust for Inflation")
    l_rent = LineItem("Rent")
    l_util = LineItem("Utilities")
    l_misc = LineItem("Miscellanious")
    l_security = LineItem("Security")
    l_security.setPartOf(l_misc)
    l_it = LineItem("IT")
    l_it.setPartOf(l_misc)
    lines = [l_comp,l_rent,l_util,l_misc,l_security,l_it]
    for L in lines[::-1]:
        L.guide.priority.increment(1)
    l_misc.guide.priority.reset()

    #Configure drivers (data and formulas)
    
    #
    ##Employee Expense Driver
    driver_ee = topic.applied_drivers["EE Driver"]
    employee_data = dict()
    ee_formula_name = "inflation-adjusted monthly expense from known annual start."
    employee_formula = topic.formulas[ee_formula_name]
    #
    m_ref_date = M.time_line.current_period.end
    if Globals.fix_ref_date:
        m_ref_date = Globals.t0
    m_ref_year = m_ref_date.year
    #
    market_conditions = topic.CM.get_color(m_ref_date)
    #
    inflation = market_conditions.inflation.annual
    employee_data["annual_inflation"] = inflation
    employee_data["base_annual_expense"] = annual_unit_comp
    #
    #
    employee_data["ref_year"] = m_ref_year  
    #
    driver_ee.setData(employee_data)
    driver_ee.setFormula(employee_formula)
    del employee_data, employee_formula
    
    #
    ##Rent Driver
    driver_rent = topic.applied_drivers["Rent Driver"]
    rent_data = dict()
    rent_formula = topic.formulas["set line to fixed monthly value."]
    #
    rent_data["fixed_monthly_value"] = M.interview.work_space["monthly rent"]
    rent_data["new_optional_tags"] = ["run-rate",
                                      "cash rent",
                                      "non-straight-line",
                                      "non-GAAP"]
    #
    driver_rent.setData(rent_data)
    driver_rent.setFormula(rent_formula)
    del rent_data, rent_formula

    #
    ##Utilities Driver
    driver_util = topic.applied_drivers["Utilities Driver"]
    util_data = dict()
    f_source_name = "set line based on source value and multiplier."
    util_formula = topic.formulas[f_source_name]
    #
    util_data["min"] = 100
    util_data["max"] = 2000
    util_data["source_multiplier"] = 0.05
    util_data["source_line_name"] = "Rent"
    #
    driver_util.setData(util_data)
    driver_util.setFormula(util_formula)
    del util_data, util_formula

    #
    ##Security Driver
    driver_security = topic.applied_drivers["Security Driver"]
    security_data = dict()
    f_source_name = "set line based on source value and multiplier."
    security_formula = topic.formulas[f_source_name]
    #
    security_data["min"] = 100
    security_data["source_multiplier"] = 0.02
    security_data["source_line_name"] = "Rent"
    #
    driver_security.setData(security_data)
    driver_security.setFormula(security_formula)
    del security_data, security_formula

    #
    ##IT Driver
    driver_it = topic.applied_drivers["IT Driver"]
    it_data = dict()
    it_formula = topic.formulas["set line to fixed monthly value."]
    #
    it_data["fixed_monthly_value"] = 500
    it_data["new_optional_tags"] = ["it",
                                    "internet expense",
                                    "telephony expense",
                                    "cell phone",
                                    "land line"]
    #
    driver_it.setData(it_data)
    driver_it.setFormula(it_formula)
    del it_data, it_formula
    
    #insert lines and drivers into model
    #
    #make a other_key : driver dictionary for easy insertion into BUs
    #
    #this setup is redundant with the indexing that bu.addDriver() now performs
    #automatically on each call for work conditions and other keys supplied by
    #caller; preserve here for legacy comparability.
    #
    local_drivers = dict()
    local_drivers["Employee Expense"] = local_drivers["employee expense"] = driver_ee
    local_drivers["Rent"] = local_drivers["rent"] = driver_rent
    local_drivers["Utilities"] = local_drivers["utilities"] = driver_util
    local_drivers["Security"] = local_drivers["security"] = driver_security
    local_drivers["IT"] = local_drivers["it"] = driver_it
    
    #
    #
    #a) template fins: lines only
    template_fins = M.defaultFinancials
    i_opex = template_fins.indexByName("Operating Expense")
    line_opex = template_fins[i_opex]
    for line in lines[::-1]:
        if line.name in template_fins.dNames.keys():
            continue
        local_line = copy.deepcopy(line)
        template_fins.insert(i_opex+1,local_line)
        if not local_line.partOf:
            local_line.setPartOf(line_opex)
    #b) bottom units: lines and drivers
    top_bu = M.time_line.current_period.content
    bottom_bus = M.time_line.current_period.selectBottomUnits()
    for bu in bottom_bus:
        fins = bu.financials
        i_opex = fins.indexByName("Operating Expense")
        line_opex = fins[i_opex]
        for L in lines[::-1]:
            if L.name in fins.dNames.keys():
                continue
            localL = copy.deepcopy(L)
            fins.insert(i_opex+1,localL)
            if not localL.partOf:
                localL.setPartOf(line_opex)
        for (k,tDriver) in local_drivers.items():
            clean_dr = tDriver.copy()
            bu.addDriver(clean_dr,k)
    #
    topic.wrap_topic()

def end_scenario(topic):
    #user pressed stop interview in middle of question
    pass

scenarios[None] = scenario_1
#
scenarios["average monthly rent for a unit?"] = scenario_2
scenarios["unit employee expense per year?"] = scenario_3
#
scenarios[Globals.user_stop] = end_scenario
#




