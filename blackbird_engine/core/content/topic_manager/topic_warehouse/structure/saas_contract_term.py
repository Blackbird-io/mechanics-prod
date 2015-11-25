#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: TW.structure.contract_term_saas
"""

Topic that asks about the standard contract term and configures life segments
accordingly. 
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
from datetime import timedelta

import BBGlobalVariables as Globals

from data_structures.modelling.business_unit import BusinessUnit
from data_structures.modelling.line_item import LineItem
from tools import for_messages as message_tools

from . import knowledge_re_software
from .standard_financials import basic_fins




#globals
topic_content = True
name = "contract term saas"
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
                "deterministic",
                "life cycle",
                "contract term",
                "expands taxonomy",
                "defines new unit type",
                "modifies path",
                "basic",
                "basic analysis depth",
                "subscriber life",
                "life segment",
                "subscription term",
                "standard subscription term",
                "standard term",
                "term"]
#
applied_drivers = dict()
formula_names = []
question_names = []
scenarios = dict()
work_plan = dict()

question_names = ["subscription term in months?"]
work_plan["subscription term"] = 1
work_plan["structure"] = 1
work_plan["life"] = 1
work_plan["life cycle"] = 1
work_plan["subscriber life"] = 1

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

    Function asks question about the length of standard subscription term. 
    """
    new_question = topic.questions["subscription term in months?"]
    topic.wrap_scenario(new_question)

def scenario_2(topic):
    """


    scenario_2(topic) -> None


    **closing scenario**

    Scenario concludes with wrap_topic()

    Function pulls out user response, records it in the interview work_space
    under ``subscription_term_months``, and passes the stated term to
    apply_data() for processing. 
    """
    model = topic.MR.activeModel
    stated_term = topic.get_first_answer()
    stated_term = float(stated_term)
    model.interview.work_space["subscription_term_months"] = stated_term
    apply_data(topic, stated_term)
    topic.wrap_topic()

def end_scenario(topic):
    """


    end_scenario(topic) -> None

    **end scenario**

    Scenario concludes with wrap_to_end().
    
    Scenario assumes the standard subscription term and passes the assumption
    to apply_data() for implementation.
    """
    assumed_term = knowledge_re_software.standard_subscription_term_months
    apply_data(topic, assumed_term)
    topic.wrap_to_end()

def apply_data(topic, datapoint):
    """


    apply_data(topic, datapoint) -> None


    ``datapoint`` should be a number of months in the standard contract term
    
    Function creates a template business unit that represents subscribers and
    sets the length of a life segment for that unit to the datapoint (translated
    into days). Function then adds the unit template to the model taxonomy.

    Function annotates path and adds tags to model.
    """
    model = topic.MR.activeModel
    #
    basic_unit_template = model.taxonomy["standard"]
    subscriber_unit_template = basic_unit_template.copy()
    subscriber_unit_template.setName("subscriber unit template")
    subscriber_unit_template.type = "subscriber"
    #
    model.taxonomy["subscriber"] = dict()
    model.taxonomy["subscriber"]["standard"] = subscriber_unit_template
    #
    term_in_months = datapoint
    term_in_days = datapoint * Globals.days_in_month
    subscriber_unit_template.life.segment = timedelta(term_in_days)
    #life segement is the smallest increment of time over which descriptive life
    #attributes can change status. 
    #
    path = model.interview.path
    subscriber_life = LineItem(name = "subscriber life")
    subscriber_life.guide.quality.set_standard(2) #max used to be 5
    path.add_line_to(subscriber_life, "structure")
    model.interview.clear_cache()
    #
    model.tag("known subscription length")
    model.tag("subscriber unit template")
    model.tag("subscriber unit template: in progress")
    model.tag("taxonomy content")    

scenarios[None] = scenario_1
scenarios["subscription term in months?"] = scenario_2
scenarios[message_tools.USER_STOP] = end_scenario

