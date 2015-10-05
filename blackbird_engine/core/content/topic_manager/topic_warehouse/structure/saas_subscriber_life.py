#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: TW.Structure.subscriber_life_saas
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

from data_structures.modelling.line_item import LineItem




#globals
topic_content = True
name = "saas subscriber life"
topic_author = "Ilya Podolyako"
date_created = "2015-06-10"
extra_prep = False
#if extra_prep = True, TopicManager will run this module's prep() function
#after completing standard prep


#standard topic prep
user_outline_label = "Subscriber Life"
requiredTags = ["software",
                "structure",
                "taxonomy content",
                "subscriber unit template"]
optionalTags = ["saas",
                "deterministic",
                "life",
                "life cycle",
                "subscriber population",
                "subscriber life",
                "subscriber unit template: in progress",
                "assumed distribution",
                "implied churn"]
#
applied_drivers = dict()
formula_names = []
question_names = []
scenarios = dict()
work_plan = dict()

question_names = ["subscriber life range?"]
work_plan["subscriber life"] = 1
work_plan["structure"] = 1
work_plan["life cycle"] = 1
work_plan["life"] = 1

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

    Function asks question about the range of subscriber lives. Function
    adjusts input element parameters to track the length of a contract
    segment. 
    """
    #
    model = topic.MR.activeModel
    subscriber_unit_template = model.taxonomy["subscriber"]["standard"]
    segment_in_months = int((subscriber_unit_template.life.segment.days /
                             Globals.days_in_month))
    #
    new_question = topic.questions["subscriber life range?"]
    main_element = new_question.input_array[0]
    main_element.r_min = 0
    main_element.r_max = int(30 * segment_in_months)
    anchor_min = round(0.5 * segment_in_months)
    anchor_max = 5 * segment_in_months
    main_element.shadow = str(anchor_min)
    main_element.shadow_2 = str(anchor_max)
##    main_element.r_step = 1
    #
    topic.wrap_scenario(new_question)
    

def scenario_2(topic):
    """


    scenario_2(topic) -> None


    **closing scenario**

    Scenario concludes with wrap_topic()

    Function pulls out user response, adds it to work_space as
    ``subscriber_life_range``, and then passes the response to apply_data() for
    implementation.     
    """
    model = topic.MR.activeModel
    stated_range = topic.get_first_answer()
    model.interview.work_space["subscriber_life_range"] = stated_range
    apply_data(topic, stated_range)
    topic.wrap_topic()

def end_scenario(topic):
    """


    end_scenario(topic) -> None

    **end scenario**

    Scenario concludes with wrap_to_end().
    
    Function assumes the range is between 1 and 5 times the standard contract
    length. Function runs apply_data() on this assumption. 
    """
    model = topic.MR.activeModel
    subscriber_unit_template = model.taxonomy["subscriber"]["standard"]
    segment_months = (subscriber_unit_template.life.segment.days /
                      Globals.days_in_month)
    assumed_range = [1 * segment_months,
                     5 * segment_months] 
    apply_data(topic, assumed_range)
    topic.wrap_to_end()

def apply_data(topic, datapoint):
    """


    apply_data(topic, datapoint) -> None


    ``datapoint`` is a [min, max] range, with values in months.
    
    Function assumes:
    
    - subscriber distribution is symmetric around a mean life,
    - subscriber distribution is random and normal, and
    - user interprets ``most`` to mean 95% of cases.

    In a normal distribution, 95% of the population will fall within 2 standard
    deviations of the mean. Function uses the datapoint to compute the mean,
    sigma (standard deviation), and maximum life span (assumed as mean + 3
    sigma).

    Function also computes churn on the theory that at the mean age, each
    customer has a 50% chance of cancelling at the next contract cycle. 
    """
    datapoint = [float(x) for x in datapoint]
    #
    model = topic.MR.activeModel
    subscriber_unit_template = model.taxonomy["subscriber"]["standard"]
    sbr_count_label = "subscriber count"
    #
    lo = timedelta(datapoint[0] * Globals.days_in_month)
    hi = timedelta(datapoint[1] * Globals.days_in_month)
    mean = (lo + hi)/2
    sigma = (hi - lo)/4
    #assume normal distribution that's symmetric around a mean. 95% (``most``)
    #of the population would fall w/in 2 st deviations of the mean.
    #
    upper_limit = mean + 3 * sigma
    #upper limit is longest likely life for the population. even for non-normal
    #distributions, ~98% of observations should fall w/ in 3 st devs
    #
    avg_contract_count = mean / subscriber_unit_template.life.segment
    churn = 0.50 / avg_contract_count
    #assume that at the mean age, the average customer has a 50% probability of
    #renewing their contract and a 50% probability of cancelling it. The
    #probability of renewal goes down as the customer ages. If we assume each
    #renewal is an independent, random event, we can **roughly** estimate the
    #probability of cancellation (churn) after any given contract by dividing
    #the known 50% probability by the number of contracts that went into getting
    #the probability to this level.
    #
    #solving for churn in 0.50=(1 - churn)^(count) would produce a better
    #estimate from a theoretical perspective. it's unclear whether this approach
    #would lead to more accurate forecasting though. 
    #
    #apply info to subscriber unit template:
    subscriber_unit_template.life.span = upper_limit
    subscriber_unit_template.life.sigma = sigma
    subscriber_unit_template.life.mean = mean
    subscriber_unit_template.life.churn = churn
    #
    #modify path
    path = model.interview.path
    model.interview.clear_cache()
    #always clear interview cache before modifying path, otherwise controller
    #may follow old plan
    #
    path.buildDictionaries()
    if sbr_count_label in path.dNames:
        pass
    else:
        subscriber_count = LineItem(sbr_count_label)
        subscriber_count.guide.quality.set_standard(1) #max used to be 5
        subscriber_count.guide.priority.increment(3)
        path.add_line_to(subscriber_count, "structure")
    #
    ##    model.interview.set_focal_point(subscriber_count)
    #direct controller attention to focal point
    #
    #annotate model
    model.tag("known subscriber life")
    model.unTag("subscriber unit template: in progress")
    model.tag("subscriber unit template: ready")
    
    

scenarios[None] = scenario_1
#
scenarios["subscriber life range?"] = scenario_2
#
scenarios[Globals.user_stop] = end_scenario

