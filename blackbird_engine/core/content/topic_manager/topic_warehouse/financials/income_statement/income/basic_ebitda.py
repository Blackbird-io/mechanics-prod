#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: TW.Financials.IS.Income.BasicEBITDA
"""

A topic that calculates EBITDA. 

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
import BBGlobalVariables as Globals

from data_structures.modelling.driver import Driver




#globals
topic_content = True
name = "Basic EBITDA Analysis"
topic_author = "Ilya Podolyako"
date_created = "2015-04-11"
extra_prep = False
#if extra_prep = True, TopicManager will run this module's prep() function
#after completing standard prep

#standard topic prep
user_outline_label = "Internal EBITDA Analysis"
requiredTags = []
optionalTags = ["Calculation",
                "Operations",
                "Basic",
                "Default",
                "Performance Metrics",
                "Non-GAAP"]
                
#
applied_drivers = dict()
formula_names = []
question_names = []
scenarios = dict()
work_plan = dict()

formula_names = ["basic ebitda calculator"]
#question names intentionally left blank here

work_plan["EBITDA"] = 1

#drivers:
#create each driver object used in Topic and place in applied_drivers to make
#sure they receive proper signatures and ids. Provide data and formulas
#during runtime through scenarios. At that point, topic will carry dictionaries
#that point to all relevant objects. 
#
#Driver for Car Expense:
driver_ebitda = Driver()
driver_ebitda.setName("Basic EBITDA Calculator")
driver_ebitda.setWorkConditions(None, None, "EBITDA")
driver_ebitda.mustBeFirst = True
applied_drivers["EBITDA Driver"] = driver_ebitda

#scenarios
#
#define each scenario, then fill out scenarios dictionary at the bottom
#each scenario must conclude with either:
    #scenarios that ask a question - topic.wrap_scenario(Q)
    #scenarios that complete processing - topic.wrap_topic()
    #scenarios that respond to a user stop - topic.wrap_to_stop()

def scenario_1(topic):
    M = topic.MR.activeModel
    driver_ebitda = topic.applied_drivers["EBITDA Driver"]
    ebitda_formula = topic.formulas["basic ebitda calculator"]
    driver_ebitda.setFormula(ebitda_formula)
    #
    #insert driver into model
    #to make sure ebitda picks up any line items at the top level, insert
    #into top unit only; otherwise ground-level calculations will block top
    #from deriving it with its own line items taken into account
    #
    top_bu = M.time_line.current_period.content
    top_bu.addDriver(driver_ebitda, "EBITDA", "ebitda")
    #
    #don't clear Model.interview cache (protocol, etc) because didnt add any
    #lineitems
    topic.wrap_topic()

scenarios[None] = scenario_1
scenarios[Globals.user_stop] = scenario_1
#

