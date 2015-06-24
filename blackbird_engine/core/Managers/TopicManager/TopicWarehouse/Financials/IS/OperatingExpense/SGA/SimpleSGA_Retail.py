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

import BBGlobalVariables as Globals
import MarketColor

from DataStructures.Modelling.Driver import Driver
from DataStructures.Modelling.LineItem import LineItem




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
    inflation = copy.copy(MarketColor.annualInflation)
    marketing_data["annual_inflation"] = inflation
    #
    m_ref_date = M.currentPeriod.end
    if Globals.fix_ref_date:
        m_ref_date = Globals.t0
    m_ref_year = m_ref_date.year
    #
    marketing_data["ref_year"] = m_ref_year
    #
    ltm_marketing_spend = M.interview.work_space["ltm marketing"]
    expected_user_understatement = MarketColor.standardUnderstatement
    adj_marketing_spend = (ltm_marketing_spend *
                           (1 + expected_user_understatement))
    marketing_data["base_annual_expense"] = adj_marketing_spend
    #
    driver_marketing.setData(marketing_data)
    driver_marketing.setFormula(marketing_formula)
    del marketing_data, marketing_formula
    
    #
    ##G&A Driver
    driver_ga = topic.applied_drivers["GA Driver"]
    ga_data = dict()
    ga_formula = topic.formulas["monthly expense from known annual start."]
    #
    ga_data["base_annual_expense"] = M.interview.work_space["ltm ga"]
    #
    driver_ga.setData(ga_data)
    driver_ga.setFormula(ga_formula)
    del ga_data, ga_formula
    
    #insert lines and drivers into model
    #
    #make a other_key : driver dictionary for easy insertion into BUs
    #
    #this setup is redundant with the indexing that bu.addDriver() now performs
    #automatically on each call for work conditions and other keys supplied by
    #caller; preserve here for legacy comparability.
    #
    local_drivers = dict()
    local_drivers["Marketing"] = local_drivers["marketing"] = driver_marketing
    local_drivers["G&A"] = local_drivers["g&a"] = driver_ga
    
    #insert lines and drivers into model
    #a) template fins: lines only
    templateFins = M.defaultFinancials
    i_sga = templateFins.indexByName("SG&A")
    line_sga = templateFins[i_sga]
    for L in lines[::-1]:
        if L.name in templateFins.dNames.keys():
            continue
        localL = copy.deepcopy(L)
        templateFins.insert(i_sga+1,localL)
        localL.setPartOf(line_sga)
    #b) lines and drivers into top unit only (because this is SGA)
    #Unit SGA can be a different topic
    topBU = M.currentPeriod.content
    activeBUs = [topBU]
    for bu in activeBUs:
        fins = bu.financials
        i_sga = fins.indexByName("SG&A")
        line_sga = fins[i_sga]
        for L in lines[::-1]:
            if L.name in fins.dNames.keys():
                continue
            localL = copy.deepcopy(L)
            fins.insert(i_sga+1,localL)
            localL.setPartOf(line_sga)
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
scenarios["ltm whole company marketing spend?"] = scenario_2
scenarios["ltm whole company overhead, excluding marketing?"] = scenario_3
#
scenarios[Globals.user_stop] = end_scenario
#




