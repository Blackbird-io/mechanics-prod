#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: TW.Introduction.software_seat_pricing
"""

Topic asks a binary question about whether the user charges subscribers per seat
or a flat fee. 

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

from data_structures.modelling.line_item import LineItem




#globals
topic_content = True
name = "software seat pricing check"
topic_author = "Ilya Podolyako"
date_created = "2015-06-30"
extra_prep = False

#standard topic prep
user_outline_label = "Distribution"

#tag storage
tg_element_seat = "pricing element: seat"
tg_price_by_seat = "price by seat"
tg_sbr_per_seat = "subscriptions priced per seat"


requiredTags = ["software",
                "introduction"]
optionalTags = ["distribution model",
                "license structure",
                "distribution structure",
                "saas",
                "subscription",
                "product",
                "software as a service",
                "software-as-a-service",
                "SaaS",
                "term license",
                "pricing",
                "pricing element",
                "subscription pricing structure",
                "subscription pricing element",
                tg_element_seat,
                tg_price_by_seat,
                tg_sbr_per_seat]
#
applied_drivers = dict()
formula_names = []
question_names = []
scenarios = dict()
work_plan = dict()

question_names = ["do you charge subscribers by seat?"]

#put in back of structure, apply to size. 
work_plan["introduction"] = 1
work_plan["distribution model"] = 1
work_plan["structure"] = 1
work_plan["pricing element"] = 1
work_plan["pricing"] = 1

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
    new_question = topic.questions["do you charge subscribers by seat?"]
    if model.name:
        new_question.context["company_name"] = model.name
        #can fill in product name here too
    topic.wrap_scenario(new_question)

def scenario_2(topic):
    """


    scenario_2(topic) -> None


    **closing scenario**

    Scenario concludes with wrap_topic()

    Function pulls out user response and stores it in model's interview
    workspace. 
    """
    pricing_element = topic.get_first_answer()
    model = topic.MR.activeModel
    model.interview.work_space["pricing element"] = pricing_element
    apply_data(topic, pricing_element)
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
    #<---------------------------------------------------------------------assume by subscriber ?
    #

def apply_data(topic, datapoint):
    """


    apply_data(topic, datapoint) -> None


    No-op in this topic. 
    """
    seat_pricing = False
    if datapoint.casefold().startswith(("yes",
                                        "seat")):
        seat_pricing = True
    #1 unpack
    model = topic.MR.activeModel
    path = model.interview.path
    if not seat_pricing:
        pass
        #dont bother doing anything
    else:
        seat_count = LineItem("seat count")
        seat_count.guide.priority.reset()
        seat_count.guide.priority.increment(3)
        seat_count.guide.quality.set_standard(1) #max used to be 5

    #2 apply
    if seat_pricing:
        model.tag(tg_element_seat,
                  tg_price_by_seat,
                  tg_sbr_per_seat)

    #3 update guidance attributes
    if seat_pricing:
        path.add_line_to(seat_count, "structure")
        model.interview.clear_cache()
    #
    

scenarios[None] = scenario_1
scenarios["do you charge subscribers by seat?"] = scenario_2
scenarios[Globals.user_stop] = end_scenario


