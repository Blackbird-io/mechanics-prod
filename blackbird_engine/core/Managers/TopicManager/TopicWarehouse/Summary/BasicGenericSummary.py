#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: TW.Summary.BasicGenericSummary
"""

Topic that prepares a basic summary of the model's financials.

Description:
  -- take current top-level financials
  -- multiply by 12 to get annualized pro forma
  -- take out revenue, cost, opex, sga, ebitda, capex, ebitda
  -- package that into a BusinessSummary dictionary
  -- also include credit_capacity, which is 80% times max atx landscape
     [Globals.cc_haircut]

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

from DataStructures.Analysis.BusinessSummary import BusinessSummary




#globals
topic_content = True
name = "basic model summary, annualized current with capex"
topic_author = "Ilya Podolyako"
date_created = "2015-04-23"
extra_prep = False
#if extra_prep = True, TopicManager will run this module's prep() function
#after completing standard prep
PrivateKnowledge = None

#standard topic prep
user_outline_label = "Model summary."
requiredTags = []
optionalTags = []
#
applied_drivers = dict()
formula_names = []
question_names = []
scenarios = dict()
work_plan = dict()

work_plan["model summary"] = 1



#drivers:
#create each driver object used in Topic and place in applied_drivers to make
#sure they receive proper signatures and ids. Provide data and formulas
#during runtime through scenarios. At that point, topic will carry dictionaries
#that point to all relevant objects. 
#
#n/a, all work done at topic runtime

#scenarios
#
#define each scenario, then fill out scenarios dictionary at the bottom
#each scenario must conclude with either:
    #scenarios that ask a question - topic.wrap_scenario(Q)
    #scenarios that complete processing - topic.wrap_topic()
    #scenarios that respond to a user stop - topic.wrap_to_stop()

def scenario_1(topic):
    M = topic.MR.activeModel
    top_bu = M.currentPeriod.content
    top_fins = top_bu.financials
    summary = BusinessSummary()
    #
    names_to_add = ["revenue",
                    "cost",
                    "cogs",
                    "operating expense",
                    "sg&a",
                    "ebitda",
                    "adjusted ebitda",
                    "capex"]
    #financials will generally have only one of ``cogs`` vs ``cost``
    #
    #get appropriate lines out of financials
    for name in names_to_add:
        try:
            try:
                #try to find a summary first
                summary_name = top_fins.summaryPrefix.casefold() + " " + name
                spot = top_fins.indexByName(summary_name)
            except ValueError:
                #if no summary, look at the original
                spot = top_fins.indexByName(name)
            line = top_fins[spot]
            #annualize line values and put them into summary; use original names
            #here to avoid system prefix in output
            summary[name] = 12 * (line.value or 0)
        except ValueError:
            #line is missing completely
            continue
    #
    #manually add credit capacity
    landscape_summary = M.analytics.credit.combined.get_summary()
    print(landscape_summary)
    cc_raw = landscape_summary["size"]["hi"]
    cc_adj = cc_raw * (1 - Globals.cc_haircut)
    summary["credit_capacity"] = cc_adj
    M.summary = summary
    #
    #finish work, wrap topic()
    topic.wrap_topic()

scenarios[None] = scenario_1
scenarios[Globals.user_stop] = scenario_1
#

