#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: Managers.TopicManager.TopicWarehouse.TopicTemplate
"""

A template for topic content modules. Includes all parameters available for
customization. 

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

import bb_settings

from data_structures.modelling.driver import Driver
from data_structures.modelling.line_item import LineItem

from tools import for_messages as message_tools




#globals
topic_content = True
name = "Simple SGA - Retail"
topic_author = "Ilya Podolyako"
date_created = "2015-04-10"
extra_prep = False

#standard topic prep
user_outline_label = "G & A"
requiredTags = []
optionalTags = ["Retail",
                "Basic",
                "Default",
                "Expense"]
#
applied_drivers = dict()
formula_names = []
question_names = []
scenarios = dict()
work_plan = dict()

formula_names = ["inflation-adjusted monthly expense from known annual start.",
                 "monthly expense from known annual start."]

question_names = ["ltm whole company marketing spend?",
                  "ltm whole company overhead, excluding marketing?"]

work_plan["Marketing"] = 1
work_plan["Overhead"] = 1
work_plan["General & Administrative"] = 1
work_plan["G&A"] = 1
work_plan["SG&A"] = 1
work_plan["Selling, General & Administrative"] = 1

#drivers:
#create each driver object used in Topic and place in applied_drivers to make
#sure they receive proper signatures and ids. Provide data and formulas
#during runtime through scenarios. At that point, topic will carry dictionaries
#that point to all relevant objects. 
#
#Driver for Marketing
driver_marketing = Driver()
driver_marketing.setName("Simple Marketing Driver")
driver_marketing.setWorkConditions(None, None, "Marketing")
driver_marketing.mustBeFirst = True
applied_drivers["Marketing Driver"] = driver_marketing
#
#Driver for Rent
driver_ga = Driver()
driver_ga.setName("Simple G&A Driver")
driver_ga.setWorkConditions(None,None,"G&A")
driver_ga.mustBeFirst = True
applied_drivers["GA Driver"] = driver_ga

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

    Scenario asks question about marketing spend through topic.wrap_scenario() 
    """
    M = topic.MR.activeModel
    new_q = topic.questions["ltm whole company marketing spend?"]
    topic.wrap_scenario(new_q)

def scenario_2(topic):
    """


    scenario_2(topic) -> None


    Scenario asks question about other corporate overhead through
    topic.wrap_scenario() 
    """
    M = topic.MR.activeModel
    Q = topic.MR.activeQuestion
    R = float(topic.get_first_answer())
    M.interview.work_space["ltm marketing"] = R
    new_q = topic.questions["ltm whole company overhead, excluding marketing?"]
    topic.wrap_scenario(new_q)

def scenario_3(topic):
    """
    """
    M = topic.MR.activeModel
    time_line = M.time_line
    
    ltm_ga = float(topic.get_first_answer())
    M.interview.work_space["ltm ga"] = ltm_ga

    #Make lines    
    l_marketing = LineItem("Marketing")
    l_ga = LineItem("G&A")
    lines = [l_marketing, l_ga]
    for L in lines[::-1]:
        L.guide.priority.increment(1)
        L.tag("LTM-driven","Annualized")

    #Configure drivers (data and formulas)
    #
    ##Marketing Driver
    driver_marketing = topic.applied_drivers["Marketing Driver"]
    marketing_data = dict()
    marketing_fn = "inflation-adjusted monthly expense from known annual start."
    marketing_formula = topic.formulas[marketing_fn]
    #
    m_ref_date = M.time_line.current_period.end
    if bb_settings.fix_ref_date:
        m_ref_date = bb_settings.t0
    m_ref_year = m_ref_date.year
    #
    marketing_data["ref_year"] = m_ref_year
    #
    market_conditions = topic.CM.get_color(m_ref_date)
    inflation = market_conditions.inflation.annual
    if "annual_inflation" not in time_line.parameters:
        time_line.parameters.add({"annual_inflation" : inflation})
    
    ltm_marketing_spend = M.interview.work_space["ltm marketing"]
    expected_user_understatement = market_conditions.corrections.understatement
    adj_marketing_spend = (ltm_marketing_spend * (1 + expected_user_understatement))
    time_line.parameters.add({"ltm marketing" : adj_marketing_spend})
    
    driver_marketing.conversion_table["ltm marketing"] = "base_annual_expense"
    driver_marketing.configure(data=marketing_data, formula=marketing_formula)
    
    del marketing_data, marketing_formula
    
    #
    ##G&A Driver
    driver_ga = topic.applied_drivers["GA Driver"]
    ga_formula = topic.formulas["monthly expense from known annual start."]
    
    time_line.parameters.add(
        {
            "ltm ga" : M.interview.work_space["ltm ga"]
            }
        )
    driver_ga.conversion_table["ltm ga"] = "base_annual_expense"
    driver_ga.configure(data=dict(), formula=ga_formula)
    # Driver runs on shared data. 
    
    del ga_formula
    
    #insert lines and drivers into model
    #
    #make a other_key : driver dictionary for easy insertion into BUs
    #
    #this setup is redundant with the indexing that bu.add_driver() now performs
    #automatically on each call for work conditions and other keys supplied by
    #caller; preserve here for legacy comparability.
    #
    local_drivers = dict()
    local_drivers["Marketing"] = driver_marketing
    local_drivers["G&A"] = driver_ga
    
    # Insert lines and drivers into top unit only, because this is ``Selling,
    # **General** and Administrative`` expense. Unit SGA can be a different
    # topic.
    
    topBU = M.time_line.current_period.content
    activeBUs = [topBU]
    for bu in activeBUs:

        sga = bu.financials.income.find("SG&A") 
        for detail in lines[::-1]:
            local_detail = detail.copy()
            sga.add_line(local_detail)
        
##        fins = bu.financials.income
##        # Point directly to income statement to preserve legacy naming.
##        i_sga = fins.indexByName("SG&A")
##        line_sga = fins[i_sga]
##        for L in lines[::-1]:
##            if L.name in fins.table_by_name.keys():
##                continue
##            localL = copy.deepcopy(L)
##            fins.insert(i_sga+1,localL)
##            localL.setPartOf(line_sga)

        for (k, tDriver) in local_drivers.items():
            clean_dr = tDriver.copy()
            bu.add_driver(clean_dr,k)
    #
    topic.wrap_topic()    

def end_scenario(topic):
    #user pressed stop interview in middle of question
    pass

scenarios[None] = scenario_1
#
scenarios["ltm whole company marketing spend?"] = scenario_2
scenarios["ltm whole company overhead, excluding marketing?"] = scenario_3
#
scenarios[message_tools.USER_STOP] = end_scenario
#




