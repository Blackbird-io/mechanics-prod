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
from data_structures.modelling.driver import Driver
from tools import for_messages as message_tools




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
    driver_ebitda.configure(data=dict(), formula=ebitda_formula)
    
    # Driver carries no instance data. Formula finds its own arguments.
    
    top_bu = M.time_line.current_period.content

    # Insert driver into model
    top_bu.addDriver(driver_ebitda, "EBITDA", "ebitda")
    
    # To make sure ebitda picks up any line items at the top level, we insert
    # the driver only at the company (top) level. Otherwise, ground-level
    # calculations will block top from deriving it with its own line items
    # taken into account.
    #
    #don't clear Model.interview cache (protocol, etc) because didnt add any
    #lineitems
    topic.wrap_topic()

scenarios[None] = scenario_1
scenarios[message_tools.USER_STOP] = scenario_1
#

