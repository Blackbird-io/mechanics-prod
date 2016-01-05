#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: TW.summary.basic_generic_summary
"""

Topic that prepares a basic summary of the model's financials.

Description:
  -- take current top-level financials
  -- multiply by 12 to get annualized pro forma
  -- take out revenue, cost, opex, sga, ebitda, capex, ebitda
  -- package that into a BusinessSummary dictionary
  -- also include credit_capacity, which is 80% times max atx landscape

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
import bb_settings

from tools import for_messages as message_tools




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
optionalTags = ["annual financials"]
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
    model = topic.MR.activeModel
    company = model.time_line.current_period.content
    top_fins = company.financials.income
    # New pointer, old name
    #
    names_to_add = ["revenue",
                    "cost",
                    "cogs",
                    "operating expense",
                    "sg&a",
                    "ebitda",
                    "adjusted ebitda",
                    "capex"]
    # Financials will generally have only one of ``cogs`` vs ``cost``
    
    # Get appropriate lines out of financials
    for name in names_to_add:

        line = top_fins.find_first(name)
        if line:
            if line.value is not None:  
                model.summary.data[name] = 12 * line.value
                # Annualize values and put them into summary
    
    # Manually add credit capacity
    landscape_summary = model.valuation.credit.combined.get_summary()
    print(landscape_summary)
    cc_raw = landscape_summary["size"]["hi"]
    cc_adj = cc_raw * (1 - bb_settings.HAIRCUT_TO_EXPECTED_VALUE)
    model.summary.data["credit_capacity"] = cc_adj
    
    # Finish work, wrap topic()
    topic.wrap_topic()

scenarios[None] = scenario_1
scenarios[message_tools.USER_STOP] = scenario_1
#

