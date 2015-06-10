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
import BBGlobalVariables as Globals




#globals
topic_content = True
name = "software functionality"
topic_author = "Ilya Podolyako"
date_created = "2015-06-10"
extra_prep = False

#standard topic prep
user_outline_label = "Product"
requiredTags = ["software",
                "introduction"]
optionalTags = ["functionality",
                "for transcript",
                "free-form entry",
                "no machine parsing"]
#
applied_drivers = dict()
formula_names = []
question_names = []
scenarios = dict()
work_plan = dict()

question_names = ["software function?"]
work_plan["introduction"] = 1

#custom prep
def prepare(new_topic):
    #always return the topic
    return new_topic

#drivers:
#n/a

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

    Scenario concludes with wrap_scenario(question).

    Function asks question about software function. 
    """
    model = topic.MR.activeModel
    new_question = topic.questions["software function?"]
    if model.name:
        new_question.context["company_name"] = model.name
    topic.wrap_scenario(new_question)

def scenario_2(topic):
    """


    scenario_2(topic) -> None


    **closing scenario**

    Scenario concludes with wrap_topic()

    Function pulls out user response and stores it in model's interview
    workspace. 
    """
    product_description = topic.get_first_answer()
    model = topic.MR.activeModel
    model.interview.work_space["product description"] = product_description
    topic.wrap_topic()

def end_scenario(topic):
    """


    end_scenario(topic) -> None

    **end scenario**

    Scenario concludes with wrap_to_end().
    
    Call topic.wrap_to_end(), no substantive processing.
    """
    #user pressed stop interview in middle of question
    #do nothing here
    topic.wrap_to_end()

def apply_data(topic, datapoint):
    """


    apply_data(topic, datapoint) -> None


    No-op in this topic. 
    """
    pass

scenarios[None] = scenario_1
scenarios["software function?"] = scenario_2
scenarios[Globals.user_stop] = end_scenario


