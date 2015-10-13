#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: topic_warehouse.structure.goods_or_services
"""

Topic asks about whether the company sells goods or services. Part of analysis
for unknown industries.
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
====================  ==========================================================
"""




#imports
import BBGlobalVariables as Globals

from data_structures.modelling.business_unit import BusinessUnit





#globals
topic_content = True
name = "whether company derives revenue from goods or services."
topic_author = "Ilya Podolyako"
date_created = "2015-10-12"
extra_prep = False
#
#tags
tg_rev_service = "service revenue"
tg_rev_product = "product revenue"
tg_rev_multi = "multiple types of revenue"


#standard topic prep
user_outline_label = "Source of revenue"
requiredTags = ["structure", 
                "unknown industry"]
optionalTags = [tg_rev_product,
                tg_rev_service,
                tg_rev_multi,
                "makes unit templates",
                "taxonomy content",
                "generic",
                "source of revenue",
                "fundamental",
                "basic"]
#
applied_drivers = dict()
formula_names = []
scenarios = dict()
work_plan = dict()

my_question = "fundamental sources of revenue?"
work_plan["structure"] = 1
work_plan["revenue"] = 1

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
    model = topic.MR.activeModel
    new_question = topic.questions[my_question]
    topic.wrap_scenario(new_question)

def scenario_2(topic):
    """


    scenario_2(topic) -> None


    **closing scenario**

    Scenario concludes with wrap_topic()

    Function pulls out user response and [. . . ]
    """
    model = topic.MR.activeModel
    question = topic.MR.activeResponse
    response = topic.MR.activeResponse
    
    #
    revenue_profile = {"product" : False, "service" : False}
    for i in range(len(response)):
        q_element = question["input_array"][i]
        r_element = response[i]
        caption = q_element["main_caption"].casefold()        
        value = r_element["response"]
        #
        revenue_profile[caption] = value
    #
    apply_data(topic, profile)
    #
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


    ``datapoint`` is a dictionary with two keys, ``goods`` and ``services``,
    each pointing to a bool value.

    Function uses revenue composition to create template units, add lines to
    company financials, and tag the model. 
    """
    model = topic.MR.activeModel
    company = model.time_line.current_period.content
    product_unit = BusinessUnit("product template")
    service_unit = BusinessUnit("service template")
    #
    line_product = LineItem("product")
    line_service = LineItem("service")
    #
    line_rev_product = LineItem("revenue (products)")
    line_rev_service = LineItem("revenue (services)")
    product_unit.financials.add_line_to(line_rev_product, "revenue")
    service_unit.financials.add_line_to(line_rev_service, "revenue")
    #
    if datapoint["product"]:
        model.taxonomy["product"] = {"standard" : product_unit}
        model.tag(tg_rev_product)
        model.path.add_line_to(line_product, "structure")
    # 
    if datapoint["service"]:
        model.taxonomy["service"] = {"standard" : service_unit}
        model.tag(tg_rev_service)
        model.path.add_line_to(line_service, "structure")
    #
    if all(datapoint.values()):
        model.tag(tg_rev_multi)
    
    
    

scenarios[None] = scenario_1
scenarios[my_question] = scenario_2
scenarios[Globals.user_stop] = end_scenario


