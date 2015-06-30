#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: TW.Introduction.software_license_status
"""

Topic asks a binary question about whether the user sells software as a product
or as a service. 

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

from DataStructures.Modelling.LineItem import LineItem



#globals
topic_content = True
name = "software subscription or product"
topic_author = "Ilya Podolyako"
date_created = "2015-06-30"
extra_prep = False

#standard topic prep
user_outline_label = "Distribution"
requiredTags = ["software",
                "introduction"]
optionalTags = ["distribution model",
                "license structure",
                "distribution structure",
                "perpetual license",
                "term or perpetual",
                "saas",
                "subscription",
                "product",
                "software as a service",
                "software-as-a-service",
                "SaaS",
                "term license"]
#
applied_drivers = dict()
formula_names = []
question_names = []
scenarios = dict()
work_plan = dict()

question_names = ["software subscription or product?"]
work_plan["introduction"] = 1
work_plan["distribution model"] = 1

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
    new_question = topic.questions["software subscription or product?"]
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
    license_status = topic.get_first_answer()
    model = topic.MR.activeModel
    model.interview.work_space["license status"] = license_status
    apply_data(topic, license_status)
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
    #<---------------------------------------------------------------------assume subscription ?
    #

def apply_data(topic, datapoint):
    """


    apply_data(topic, datapoint) -> None


    No-op in this topic. 
    """
    saas = False
    if datapoint == "subscription":
        saas = True
    #1 unpack
    model = topic.MR.activeModel
    path = model.interview.path
    price_structure = LineItem("pricing element")
    price_structure.guide.priority.reset()
    price_structure.guide.priority.increment(3)
    price_structure.guide.quality.setStandards(1,5)

    #2 apply
    if saas:
        model.tag("subscription",
                  "internet",
                  "online",
                  "web-based",
                  "term license",
                  "saas",
                  "software as a service")
    else:
        pass

    #3 update guidance attributes
    if saas:
        path.add_line_to(price_structure, "introduction")
        model.interview.clear_cache()
    else:
        pass
    #
    

scenarios[None] = scenario_1
scenarios["software subscription or product?"] = scenario_2
scenarios[Globals.user_stop] = end_scenario


