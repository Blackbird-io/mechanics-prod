#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: TW.Financials.IS.Revenue.subscription_revenue_seats
"""

Topic asks about monthly seat price and applies the information to the
subscriber population. Topic inserts a driver that determines revenue by
multiplying the per-seat price times subscriber size. 
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
from DataStructures.Modelling.Driver import Driver
from DataStructures.Modelling.LineItem import LineItem




#globals
topic_content = True
name = "seat-based subscription revenue"
topic_author = "Ilya Podolyako"
date_created = "2015-06-30"
extra_prep = False

#store tags this topic uses multiple times in variables to avoid typos
tg_constant_life_rev = "constant revenue over lifecycle"
tg_constant_price = "constant price over time"
tg_critical = "critical user input"
tg_no_inflation = "no inflation"
tg_product_rev = "revenue from product sales"
tg_single_product = "describes resources associated with one product"
tg_subscription_rev = "subscription-based revenue"

tg_element_seat = "pricing element: seat"
tg_price_by_seat = "price by seat"
tg_sbr_per_seat = "subscriptions priced per seat"


#standard topic prep
user_outline_label = "Subscription Pricing"
requiredTags = ["revenue",
                "known subscriber pool",
                tg_price_by_seat]
optionalTags = ["subscriptions",
                "saas",
                "software",
                tg_critical,
                tg_constant_life_rev,
                tg_product_rev,
                tg_single_product,
                tg_sbr_per_seat,
                tg_subscription_rev,]

applied_drivers = dict()
formula_names = []
question_names = []
scenarios = dict()
work_plan = dict()

question_names = ["monthly seat price?"]
formula_names = ["fixed monthly value multiplied by unit size."]

work_plan["subscriptions"] = 1 
work_plan["revenue"] = 1
work_plan["revenue build"] = 1


#custom prep
def prepare(new_topic):
    #always return the topic
    return new_topic

#drivers:
D1 = Driver()
D1.setName("subscription revenue driver")
D1.setWorkConditions("subscriptions")
applied_drivers["D1"] = D1

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

    Function asks user about the monthly price of their subscription. 
    """
    #
    model = topic.MR.activeModel
    new_question = topic.questions["monthly seat price?"]
    product_name = model.interview.work_space.get("product_name")
    if product_name:
        new_question.context["product_name"] = product_name
        #could also look at whether "actual name" tag is on the bu. if it is,
        #can pull product name off the top bu. 
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
    stated_price = topic.get_first_answer()
    stated_price = float(stated_price)
    model.interview.work_space["monthly_seat_price"] = stated_price
    apply_data(topic, stated_price)
    topic.wrap_topic()

def end_scenario(topic):
    """


    end_scenario(topic) -> None


    **end scenario**
    **FORCE EXIT**

    Scenario concludes with force_exit().
    
    No-op here. Subscription price is critical information. Engine cannot
    afford to guess here.
    """
    topic.force_exit()
    #<-------------- topic.force_exit() should stop IC from any further attempts to limp home-------------------------------------------------

def apply_data(topic, datapoint):
    """


    apply_data(topic, datapoint) -> None


    ``datapoint`` is monthly subscription cost in dollars. 

    Function adds a ``subscriptions`` line to each subscriber unit in #<------------------
    c
    """
    model = topic.MR.activeModel
    current_period = model.time_line.current_period
    #
    subscriptions_line = LineItem("subscriptions")
    #
    D1 = topic.applied_drivers["D1"]
    rev_formula = topic.formulas["fixed monthly value multiplied by unit size."]
    #
    local_data = dict()
    local_data["fixed_monthly_value"] = datapoint
    #
    D1.configure(local_data, rev_formula)
    #
    subscriber_ids = current_period.ty_directory.get("subscriber")
    subscribers = current_period.get_units(subscriber_ids)
    sbr_template = model.taxonomy["subscriber"]["standard"]
    subscribers.append(sbr_template)
    #
    for sbr_unit in subscribers:
        #
        own_d1 = D1.copy()
        own_line = subscriptions_line.copy()
        #
        sbr_unit.financials.add_line_to(own_line, "revenue")
        sbr_unit.addDriver(own_d1)
        #
        sbr_unit.tag(tg_constant_life_rev,
                     tg_constant_price,
                     tg_no_inflation)
    #
    model.tag(tg_product_rev,
              tg_subscription_rev,
              "subscriptions")
    
scenarios[None] = scenario_1
#
scenarios["monthly seat price?"] = scenario_2
#
scenarios[Globals.user_stop] = end_scenario

