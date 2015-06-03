 #PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: TW.Structure.Deterministic.SimpleStructure.Content.
"""

Content module for a topic that builds out the business unit structure of a
simple model.
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
import Tools

from DataStructures.Modelling.BusinessUnit import BusinessUnit

from . import PrivateKnowledge
from ... import SharedKnowledge as SubjectKnowledge


#globals
name = "retail expected future stores"
topic_author = "IOP"
date_created = "2015-06-02"
topic_content = True
extra_prep = False


#standard prep
requiredTags = ["ready for expected growth analysis"]
optionalTags = ["Simple","Deterministic","Structure","Generic"]
#<---------------------------------------------------------------------------------------------------
applied_drivers = dict()
scenarios = dict()
    #ks are question names, None, or user_stop
    #values are scenario functions
work_plan = dict()

formula_names = []
question_names = ["stores in progress - signed leases?",
                  "time to open a store after lease?",
                  "prep before lease?"]
work_plan["structure"] = 1

SK = SubjectKnowledge

#scenarios
#
#define scenario functions, then fill out scenarios dictionary
#scenarios must end with either:
    #scenarios that ask a question - topic.wrap_scenario()
    #scenarios that complete processing - topic.wrap_topic()
    #scenarios that respond to a user stop - topic.wrap_to_end()
#
def scenario_1(topic):
    """

    scenario_1(topic) -> None

    **opening**

    Ask user about any stores they have in the works. Max units capped
    at 1000 (one thousand). 
    """
    M = topic.MR.activeModel
    new_Q = topic.questions["stores in progress?"]
    new_Q.input_array[0].r_max = SK.unit_number_limit
        M.interview.work_space["unit label"] = unit_label
    topic.wrap_scenario(new_Q)

def scenario_2(topic):
    """

    scenario_2(topic) -> None

    Scenario concludes with wrap_scenario(Q).

    Scenario retrieves number of units in company, asks about unit lifespan.
    Scenario uses max and expected (shadow) lifespan values from
    Structure.SharedKnowledge. 
    """
    #
    M = topic.MR.activeModel
    Q = topic.MR.activeQuestion
    R = topic.MR.activeResponse
    number_of_units = int(topic.get_first_answer())
    M.interview.work_space["number of units"] = number_of_units
    #save answer for later processing
    #
    #prep follow up question
    new_Q = topic.questions["unit lifespan in years?"]
    unit_label = M.interview.work_space.get("unit label")
    #use dict.get() because model may not have a known unit label
    if unit_label:
        new_Q.context["unit_label_singular"] = unit_label["singular"]
    new_Q.input_array[0].r_max = max(30,
                                     max(SK.unit_life_spans.values()))
    #default max lifespan of 30 years, activated if general knowledge empty
    model_industry = M.interview.work_space.get("industry")
    if model_industry:
        model_industry = model_industry.casefold()
        #only do transform is model_industry is a string, not a None
        new_Q.input_array[0].shadow = SK.unit_life_spans.get(model_industry)
        #shadow serves as anchor, should be approximate mean
    else:
        new_Q.input_array[0].shadow = SK.unit_life_spans["default"]
    topic.wrap_scenario(new_Q)

#
#def a function that processes the stores in progress
    #will then wrap the function in either proces
        
def end_scenario(topic):
    #wrap the processing function in end_scenario
    #
    #user pressed stop interview in middle of question
    #if know number of units, good to go off GeneralKnowledge; otherwise, dont bother
    pass

scenarios[None] = scenario_1
#
scenarios["number of business units?"] = scenario_2
scenarios["unit lifespan in years?"] = scenario_3
scenarios["months to unit maturity?"] = scenario_4
#
scenarios[Globals.user_stop] = end_scenario

