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

##from Managers.TopicManager import SharedKnowledge as GeneralKnowledge
##from TopicWarehouse.ParentDirectory import SharedKnowledge as SubjectKnowledge
##from DataStructures.Modelling.Model import Model
##from DataStructures.Modelling.BusinessUnit import BusinessUnit
##from DataStructures.Modelling.Driver import Driver




#globals
topic_content = True
name = "saas contract term"
topic_author = "Ilya Podolyako"
date_created = "2015-06-10"
extra_prep = False
#if extra_prep = True, TopicManager will run this module's prep() function
#after completing standard prep


#standard topic prep
user_outline_label = "Subscription Term"
requiredTags = ["software",
                "structure"]
optionalTags = ["saas",
                "lifecycle",
                "contract term"]
#
applied_drivers = dict()
formula_names = []
question_names = []
scenarios = dict()
work_plan = dict()

question_names = ["subscription term in months?"]
work_plan["subscription term"] = 1

SK = SubjectKnowledge

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

    Function asks question. 
    """
    new_question = topic.questions["subscription term in months?"]
    topic.wrap_scenario(new_question)

def scenario_2(topic):
    """


    scenario_2(topic) -> None


    **closing scenario**

    Scenario concludes with wrap_topic()

    Function pulls out user response and [. . . ]
    """
    model = topic.MR.activeModel
    stated_term = topic.get_first_answer()
    model.interview.work_space["subscription_term_months"] = months
    apply_data(topic, stated_term)
    topic.wrap_topic()

def end_scenario(topic):
    """


    end_scenario(topic) -> None

    **end scenario**

    Scenario concludes with wrap_to_end().
    
    [] 
    """
    assumed_term = 12
    apply_data(topic, assumed_term)
    topic.wrap_to_end()

def apply_data(topic, datapoint):
    """


    apply_data(topic, datapoint) -> None


    [describe substantive work that topic does to model based on data]
    """
    #function performs substantive work on model in light of new data
    term_in_months = datapoint
    term_in_days = datapoint * Globals.days_in_month
    model = topic.MR.activeModel
    prod_unit = model.taxonomy["product"]["standard"]
    prod_unit.life.segment = timedelta(term_in_days)
    #TO DO-------------------------------------------------------------------------------------------
        #create prod unit
        #add customer life to path (min q  = 1)
            #
    #
    #
    #applies term as life.segment in timedelta
    #can then count how many segments a particular unit has been through
    #can assign expected termination dates? or can think in terms of half-life
    #as in, how long does it take for half of the population to die? 
    #going forward, when ref_date
    
    

scenarios[None] = scenario_1
scenarios["subscription term in months?"] = scenario_2
scenarios[Globals.user_stop] = end_scenario

