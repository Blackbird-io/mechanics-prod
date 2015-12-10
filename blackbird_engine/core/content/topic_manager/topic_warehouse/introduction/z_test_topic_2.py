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
from tools import for_messages as message_tools




#globals
topic_content = True
name = "Testing new question functionality"
topic_author = "Ilya Podolyako"
date_created = "2015-10-30"
extra_prep = False
#if extra_prep = True, TopicManager will run this module's prep() function
#after completing standard prep

#standard topic prep
user_outline_label = "Conditional & stepped questions."
requiredTags = []
optionalTags = ["test",
                "introduction",
                "pathfinder",
                "generic",
                "overview",
                "structure",
                "deterministic",
                "ready for path",
                "whales"]
#
applied_drivers = dict()
formula_names = []
scenarios = dict()
work_plan = dict()

formula_names = []
my_question = "did we fix the bool response processing?"

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

    Function asks question. 
    """
    #opening scenario, begins topic analysis, may ask q1. can configure
    #question based on model data.
    new_question = topic.questions[my_question]
    topic.wrap_scenario(new_question)

def scenario_2(topic):
    """


    scenario_2(topic) -> None


    **closing scenario**

    Scenario concludes with wrap_topic()

    Function pulls out user response and [. . . ]
    """
    #pull out user response, process as necessary; store in work_space, then
    #run apply_data(topic, adj_response). then wrap_topic.
    #
    #ALL SUBSTANTIVE WORK SHOULD TAKE PLACE IN apply_data()
    response = topic.MR.activeResponse

    for element in response:
        print(element)
        print("response: ")
        print(element["response"])
        if element["response"][0]:
            print("Yay.")
        else:
            print("Nay.")
        print()
        
    topic.wrap_topic()    

def end_scenario(topic):
    """


    end_scenario(topic) -> None

    **end scenario**

    Scenario concludes with wrap_to_end().
    
    [] 
    """
    pass

def apply_data(topic, datapoint):
    """


    apply_data(topic, datapoint) -> None


    [describe substantive work that topic does to model based on data]
    """
    #function performs substantive work on model in light of new data
    pass

scenarios[None] = scenario_1
scenarios[my_question] = scenario_2
scenarios[message_tools.USER_STOP] = end_scenario




