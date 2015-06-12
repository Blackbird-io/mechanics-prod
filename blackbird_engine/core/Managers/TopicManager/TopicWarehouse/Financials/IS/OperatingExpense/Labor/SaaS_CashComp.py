#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: TW.Structure.Software.Saas_SubscriberCount
"""

Topic asks about subscriber life distribution and uses that information to
compute population life span and renewal statistics. 

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
apply_data()
end_scenario()
scenario_1()
scenario_2()

CLASSES:
n/a
====================  ==========================================================
"""




#imports
from datetime import timedelta

import BBGlobalVariables as Globals
import BBExceptions

from DataStructures.Modelling.BusinessUnit import BusinessUnit

from ..StandardFinancials import standard_financials




#globals
topic_content = True
name = "saas subscriber revenue"
topic_author = "Ilya Podolyako"
date_created = "2015-06-12"
extra_prep = False


###--------------------------------------------------------------------------have to finish tags here!!!!
#store tags this topic uses multiple times in variables to avoid typos
tg_constant_life_revenue = "constant revenue over lifecycle"
tg_constant_price = "constant price over time"
tg_critical = "critical user input"
tg_no_inflation = "no inflation"
tg_single_product = "describes resources associated with one product"
tg_sbx_revenue = "subscription-based revenue"

#standard topic prep
user_outline_label = "Subscription Pricing"
requiredTags = ["software",
                "head count",
                "personnel"]
optionalTags = [tg_critical,
                tg_single_product,
                "full time employees"]

applied_drivers = dict()
formula_names = []
question_names = []
scenarios = dict()
work_plan = dict()

question_names = ["employee headcount across software company roles?"]

work_plan["headcount"] = 2
work_plan["employee expense"] = 1
work_plan["expenses"] = 1
work_plan["structure"] = 1

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

    Function asks user about employee headcount across categories.
    """
    new_question = topic.questions["employee cash salary across roles?"] 
    model = topic.MR.activeModel
    product_unit = model.time_line.current_period.content
    personnel_container_bbid = product_unit.components.by_name["personnel"]
    personnel_container = product_unit.components.by_id[personnel_container_bbid]
    roles_by_count = sorted(personnel_container.values(), lambda headcount) #<----------------set up personnel containers
    #
    #configure question w existing roles:
    input_array = new_question["input_array"]
    for i in len(input_array):
        element = input_array[i]
        element["main_caption"] = roles_by_count[i].name
        element[
    #
    #sort by headcount
    #
    #
    #how many employees do you have in each of the following categories?
    topic.wrap_scenario(new_question)    

def scenario_2(topic):
    """


    scenario_2(topic) -> None


    **closing scenario**

    Scenario concludes with wrap_topic()

    Function pulls out user response for monthly subscription price, records the
    response in work_space, and then passes it on to apply_data() for
    processing. 
    """
    model = topic.MR.activeModel
    portal_question = topic.MR.activeQuestion
    input_array = portal_question["input_array"]
    portal_response = topic.MR.activeResponse
    #
    count_by_role = dict()
    #
    for i in len(input_array):
        role = input_array[i]["main_caption"]
        count = portal_response[i]["response"]
        count_by_role[role] = count
    #
    model.interview.work_space["employee_count_by_role"] = count_by_role
    apply_data(topic, count_by_role)
    topic.wrap_topic()

def end_scenario(topic):
    """


    end_scenario(topic) -> None


    **end scenario**
    **FORCE EXIT**

    Scenario concludes with force_exit().
    
    No-op here. Subscriber count is critical information. Engine cannot
    afford to guess here.
    """
    topic.force_exit()
    #<-------------- topic.force_exit() should stop IC from any further attempts to limp home-------------------------------------------------

def apply_data(topic, datapoint):
    """


    apply_data(topic, datapoint) -> None


    ``datapoint`` is monthly subscription cost in dollars. 

    Function adds a ``subscriptions`` line to each subscriber unit in 
    c
    """
    #configure question:
        #go through the personnel units
        #add a line to each one called cash comp
        #add a driver to each one that applies value times headcount
            #to line called cash comp
            #
    #
    
    model = topic.MR.activeModel
    prod_unit = model.time_line.current_period.content
    staff_unit = BusinessUnit("Staff Unit Template")
    #tags:
    staff_unit.tag("staff unit")
    staff_unit.tag("personnel")
    staff_unit.tag("cost center")
    staff_unit.tag("non-revenue generating")
    #
    model.taxonomy["staff unit"] = staff_unit
    #
    for (role, head_count) in datapoint.values():
        new_personnel_unit = staff_unit.copy()
        new_personnel_unit.setName(role)
        new_personnel_unit.size = head_count
        prod_unit.addComponent(new_personnel_unit)
    #    
    
scenarios[None] = scenario_1
#
scenarios["employee headcount across software company roles?"] = scenario_2
#
scenarios[Globals.user_stop] = end_scenario

