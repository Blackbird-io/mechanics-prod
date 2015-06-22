#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: TopicWarehouse.Financials.IS.Revenue.GenericRevenue
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
import BBGlobalVariables as Globals
import Managers.TopicManager.TopicWarehouse

from DataStructures.Modelling.Driver import Driver




#globals
name = "Generic Unit Revenue"
topic_author = "Ilya Podolyako"
date_created = "04-02-15"
topic_content = True
extra_prep = False
#if extra_prep = True, TopicManager will run this module's prep() function
#after completing standard prep
PrivateKnowledge = None

#standard topic prep
requiredTags = []
optionalTags = ["Revenue",
                "Default",
                "Generic",
                "Simple"]
#
applied_drivers = dict()
formula_names = []
question_names = []
scenarios = dict()
work_plan = dict()

formula_names = ["monthly unit revenue over lifecycle."]
question_names = ["annual unit revenue at maturity?",
                  "annual revenue at mature stores?"]
work_plan["Revenue"] = 1

##GK = GeneralKnowledge
##SK = SubjectKnowledge
##PK = PrivateKnowledge

D1 = Driver()
D1.setWorkConditions("Revenue")
applied_drivers["D1"] = D1


#custom prep
def prepare(new_topic):
    #always return the topic
    return new_topic

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

    Scenario wraps to new question. Asks about monthly revenue for mature
    business units
    """
    new_Q = topic.questions["annual unit revenue at maturity?"]
    #
    #see if we can use a custom question
    M = topic.MR.activeModel
    industry = M.interview.work_space.get("industry")
    retail_model = False
    if industry.casefold() == "retail":
        retail_model = True
    if "retail" in M.allTags:
        retail_model = True
    if retail_model:
        new_Q = topic.questions["annual revenue at mature stores?"]
    topic.wrap_scenario(new_Q)

def scenario_2(topic):
    M = topic.MR.activeModel
    Q = topic.MR.activeQuestion
    R = topic.MR.activeResponse
    annual_unit_rev = float(topic.get_first_answer())
    D1 = topic.applied_drivers["D1"]
    rev_formula = topic.formulas["monthly unit revenue over lifecycle."]
    data = {}
    data["annual_rev_per_mature_unit"] = annual_unit_rev
    D1.setData(data)
    D1.setFormula(rev_formula)
    for sub_bu in M.currentPeriod.selectBottomUnits():
        sub_d1 = D1.copy()
        sub_bu.addDriver(sub_d1)
    topic.wrap_topic()

def end_scenario(topic):
    #user pressed stop interview in middle of question
    pass

scenarios[None] = scenario_1
#
scenarios["annual unit revenue at maturity?"] = scenario_2
scenarios["annual revenue at mature stores?"] = scenario_2
#
scenarios[Globals.user_stop] = end_scenario
#


