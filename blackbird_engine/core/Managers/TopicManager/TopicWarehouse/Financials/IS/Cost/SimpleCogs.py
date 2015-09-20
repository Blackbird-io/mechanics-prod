# PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: TW.Financials.IS.Cost.SimpleCogs
"""

Content module for a topic that performs simple cost analysis. 

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

import BBGlobalVariables as Globals
from DataStructures.Modelling.Driver import Driver
from . import SharedKnowledge as SubjectKnowledge





#globals
topic_content = True
name = "Simple Generic COGS"
topic_author = "Ilya Podolyako"
date_created = "2015-04-09"
extra_prep = False

#standard topic prep
user_outline_label = "Cost."
requiredTags = []
optionalTags = ["COGS",
                "Cost",
                "Cost of Sales",
                "Gross Margin",
                "Basic",
                "Default",
                "Retail"]
#
applied_drivers = dict()
formula_names = []
question_names = []
scenarios = dict()
work_plan = dict()

formula_names = ["compute cost from known gross margin."]

question_names = ["average gross margin at a mature unit?"]

work_plan["COGS"] = 1
work_plan["Cost"] = 1

SK = SubjectKnowledge

D1 = Driver()
D1.setName("D1")
D1.setWorkConditions(None, None, "cost")
applied_drivers["D1"] = D1


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

    Scenario concludes with sub-scenarios.
    
    Scenario checks if Model matches a known industry. If Model does, scenario
    applies a known, mid-case industry gross margin from SubjectKnowledge
    (sub-scenario 1a). If Model tags do not show a known industry, scenario
    asks user about theg gross margin (sub-scenario 1b).     
    """
    #opening scenario, begins topic analysis, may ask q1
    M = topic.MR.activeModel
    criteria = set(M.allTags) - {None}
    active_industry = criteria & set(SK.industry_gross_margin.keys())
    if active_industry != set():
        #a couple different options here
        #1) pick one industry
            #can select by looking at frequency but cant really narrow by
            #looking at higher levels (bu, model). tag inheritance flows up, so
            #not really great for restriction
        #2) apply an average of all matching industries
        #3) apply a weighted average of all matching industries
        active_industry = sorted(active_industry)
        to_blend = []
        go_through = copy.copy(active_industry)
        for industry in go_through:
            mid_case_gm = SK.industry_gross_margin[active_industry.pop()][1] 
            to_blend.append(mid_case_gm)
        avg_gm = sum(to_blend)/len(to_blend)
        M.interview.work_space["active_gross_margin"] = avg_gm
        sub_scenario_1a(topic)
    else:
        sub_scenario_1b(topic)

def sub_scenario_1a(topic):
    """


    sub_scenario_1a(topic) -> None


    **sub-scenario**

    Scenario exits topic through topic.wrap_topic()

    For Models that fall into known industries, pull gross margin data out of
    work space, put on driver, and insert driver into ground-level units. 
    """
    M = topic.MR.activeModel
    top_bu = M.time_line.current_period.content
    D1 = topic.applied_drivers["D1"]
    cost_formula = topic.formulas["compute cost from known gross margin."]
    data = {}
    data["active_gross_margin"] = M.interview.work_space["active_gross_margin"]
    D1.setData(data)
    D1.setFormula(cost_formula)
    for sub_bu in M.time_line.current_period.selectBottomUnits():
        sub_d1 = D1.copy()
        sub_bu.addDriver(sub_d1, "Cost", "COGS")
        fins = sub_bu.financials
        fins.buildDictionaries()
        cost = "cost"
        cogs = "cogs"
        if cost in fins.dNames.keys():
            spots_cost = list(fins.dNames[cost])
            spots_cost.sort()
            i_cost = spots_cost[0]
            line_cost = fins[i_cost]
            line_cost.tag("To Confirm","BB Estimate","Industry Standard")
        if cogs in fins.dNames.keys():
            spots_cogs = list(fins.dNames[cost])
            spots_cogs.sort()
            i_cogs = spots_cogs[0]
            line_cogs = fins[i_cogs]
            line_cogs.tag("To Confirm","BB Estimate","Industry Standard")
    topic.wrap_topic()

def sub_scenario_1b(topic):
    """


    sub_scenario_1b(topic) -> None


    **sub-scenario**

    Scenario asks question through topic.wrap_scenario(new_q)

    For Models that do not match a known industry, ask the user about average
    gross margin. 
    """
    M = topic.MR.activeModel
    unit_label = M.interview.work_space.get("unit label")
    #get will return None if key is missing
    new_q = topic.questions["average gross margin at a mature unit?"]
    if unit_label:
        new_q.context["unit_label_plural"] = unit_label["plural"]
    topic.wrap_scenario(new_q)
    
def scenario_2(topic):
    """


    scenario_2(topic) -> None


    Scenario exits topic through topic.wrap_topic()

    Scenario receives user's response about gross margin, puts it into
    driver data, and then inserts the driver into ground-level units.
    """
    M = topic.MR.activeModel
    Q = topic.MR.activeQuestion
    R = topic.get_first_answer()
    adjR = R/100
    #use percent
    top_bu = M.time_line.current_period.content
    D1 = topic.applied_drivers["D1"]
    cost_formula = topic.formulas["compute cost from known gross margin."]
    data = {}
    data["active_gross_margin"] = adjR
    D1.setData(data)
    D1.setFormula(cost_formula)
    for sub_bu in M.time_line.current_period.selectBottomUnits():
        sub_d1 = D1.copy()
        sub_bu.addDriver(sub_d1,"Cost")
    topic.wrap_topic()

def end_scenario(topic):
    #user pressed stop interview in middle of question
    pass

scenarios[None] = scenario_1
scenarios["average gross margin at a mature unit?"] = scenario_2
scenarios[Globals.user_stop] = end_scenario
