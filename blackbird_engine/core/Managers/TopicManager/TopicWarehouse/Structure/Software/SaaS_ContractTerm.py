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

##from TopicWarehouse.ParentDirectory import SharedKnowledge as SubjectKnowledge




#globals
topic_content = True
name = "saas contract term"
topic_author = "Ilya Podolyako"
date_created = "2015-06-10"
extra_prep = False
#if extra_prep = True, TopicManager will run this module's prep() function
#after completing standard prep


#standard topic prep
user_outline_label = "Contract Term"
requiredTags = ["software",
                "structure"]
optionalTags = ["saas",
                "lifecycle",
                "contract term",
                "modifies path",
                "basic",
                "basic analysis depth"]
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


    [describe substantive work that topic does to model based on data] -------------------------------------------
    """
    model = topic.MR.activeModel
    subscriber_unit_template = BusinessUnit()
    #--------------------------------------------------------------------------------can add basic fins here?
    model.taxonomy["subscriber"] = dict()
    model.taxonomy["subscriber"]["standard"] = susbcriber_unit_template
    #
    term_in_months = datapoint
    term_in_days = datapoint * Globals.days_in_month
    subscriber_unit_template.life.segment = timedelta(term_in_days)
    #
    subscriber_life = LineItem(name = "subscriber_life")
    subscriber_life.guide.quality.setStandards(1,5)
    model.path.add_to("structure", subscriber_life)
    #
    model.tag("known subscription length")
    model.tag("subscriber unit template: definition in progress")
    model.tag("taxonomy content")    

scenarios[None] = scenario_1
scenarios["subscription term in months?"] = scenario_2
scenarios[Globals.user_stop] = end_scenario

