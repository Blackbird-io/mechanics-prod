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
name = "saas customer life range"
topic_author = "Ilya Podolyako"
date_created = "2015-06-10"
extra_prep = False
#if extra_prep = True, TopicManager will run this module's prep() function
#after completing standard prep


#standard topic prep
user_outline_label = "Subscription Term"
requiredTags = ["software",
                "structure",
                "customer life"]
optionalTags = ["saas",
                "lifecycle",
                "contract term",
                "life range",
                "customer population"]
#
applied_drivers = dict()
formula_names = []
question_names = []
scenarios = dict()
work_plan = dict()

question_names = ["customer life range?"]
work_plan["customer life"] = 1
work_plan["structure"] = 1
work_plan["lifecycle"] = 1

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

    Function asks question about the range of an average customer life.
    """
    new_question = topic.questions["customer life range?"]
    
    main_element = new_question.input_array[0]
    main_element.r_min = 0
    main_element.r_max = 
    main_element.r_step = 1
    topic.wrap_scenario(new_question)
    
    #customize question:
        #min = 0
        #max = 30 * contract term
        #shadow = 1, 5
    #

def scenario_2(topic):
    """


    scenario_2(topic) -> None


    **closing scenario**

    Scenario concludes with wrap_topic()

    Function pulls out user response and [. . . ]
    """
    model = topic.MR.activeModel
    stated_range = topic.get_first_answer())
    model.interview.work_space["customer_life_range"] = stated_range
    apply_data(topic, stated_range)
    topic.wrap_topic()

def end_scenario(topic):
    """


    end_scenario(topic) -> None

    **end scenario**

    Scenario concludes with wrap_to_end().
    
    [] 
    """
    model = topic.MR.activeModel
    prod_unit = model.taxonomy["production"]["standard"]
    assumed_range = [prod_unit.life.segment.days/ Globals.days_in_month * 1,
                     prod_unit.life.segment.days/ Globals.days_in_month * 10]
    #express range in months. 
    apply_data(topic, assumed_range)
    topic.wrap_to_end()

def apply_data(topic, datapoint):
    """


    apply_data(topic, datapoint) -> None


    Function gets a len-2 list that describes the min and max. Stores
    range somewhere. Figures out standard deviation (assume 90% w/in 3 st devs), mean,
    max life, defined as 6 st deviations. 

    later, count topic will set ages over this distribution to match the stated avg. 
    """
    lo = datapoint[0]
    hi = datapoint[1]
    mean = (lo + hi)/2
    std_dev = (hi - lo)/4
    #assume range covers ~95% of the population, w/in 2sigma of the mean
    upper_limit = mean + std_dev * 3
    #upper limit is longest likely life, in months
    life_span_days = upper_limit * Globals.days_in_month
    model = topic.MR.activeModel
    prod_unit = model.taxonomy["product"]["standard"]
    prod_unit.life.span = timedelta(life_span_days)
    #
    #applies term as life.segment in timedelta
    #can then count how many segments a particular unit has been through
    #can assign expected termination dates? or can think in terms of half-life
    #as in, how long does it take for half of the population to die? 
    #going forward, when ref_date
    #
    #now, count can pull out the data and apply expected aging to 95% of the population
    #literally, 95% of the units should go in the range, in order. others should go equally
    #above and below.   

scenarios[None] = scenario_1
scenarios["subscription term in months?"] = scenario_2
scenarios[Globals.user_stop] = end_scenario

