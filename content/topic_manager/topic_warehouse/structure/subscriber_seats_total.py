#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: TW.Structure.Software.subscriber_seats_total
"""

Topic asks about subscriber life distribution and uses that information to
compute population life span and renewal statistics.   3<-----------------------------------fix 

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
from tools import for_messages as message_tools




#globals
topic_content = True
name = "total subscriber seat count"
topic_author = "Ilya Podolyako"
date_created = "2015-06-29"
extra_prep = False
#if extra_prep = True, TopicManager will run this module's prep() function
#after completing standard prep

#store tags this topic uses multiple times in variables to avoid typos
#
tg_basic = "analysis quality: basic"
tg_medium = "analysis quality: medium"
tg_high = "analysis quality: high"
tg_single_product = "describes resources associated with one product"
tg_subscriber_unit = "subscribers"
tg_element_seat = "pricing element: seat"
tg_populated = "known subscriber pool"
tg_price_by_seat = "price by seat"
tg_sbr_per_seat = "subscriptions priced per seat"
tg_size_by_seat = "size represents a batch of seats"
tg_sbr_batch_override = "seat count sizing overrides prior batch count"
tg_size_by_batch = "size represents batch of subscribers"

#
#storing in tags in variables above is solely for the convenience of the author
#



#standard topic prep
user_outline_label = "Subscriber Seats"
requiredTags = ["structure",
                "seat count",
                tg_populated,
                tg_price_by_seat]
optionalTags = ["customers",
                "subscriber count",
                "subscriber population",
                "saas",
                "software",
                "paying seats",
                "revenue build",
                "subscription",
                "product",
                tg_subscriber_unit,
                tg_single_product,
                tg_element_seat,
                tg_sbr_per_seat]
#
applied_drivers = dict()
formula_names = []
question_names = []
scenarios = dict()
work_plan = dict()

question_names = ["total paying subscriber seats?"]

work_plan["subscriber population"] = 1
work_plan["customers"] = 1
work_plan["structure"] = 1
work_plan["subscriber count"] = 1
work_plan["subscriber seats"] = 1
work_plan["seats"] = 1
work_plan["seat count"] = 1
work_plan["revenue build"] = 1


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

    Function asks user about their total seat count. 
    """
    #
    new_question = topic.questions["total paying subscriber seats?"]
    model = topic.MR.activeModel
    current_period = model.time_line.current_period
    sbr_ids = current_period.ty_directory.get("subscriber")
    if sbr_ids:
        sbr_count = len(sbr_ids)
        active_element = new_question.input_array[0]
        active_element.r_max = sbr_count * 1000
        active_element.shadow = sbr_count * 12  
    topic.wrap_scenario(new_question)    

def scenario_2(topic):
    """


    scenario_2(topic) -> None


    **closing scenario**

    Scenario concludes with wrap_topic()

    Function pulls out user response, records the response in model's interview
    workspace, and passes it to apply_data() for implementation.     
    """
    model = topic.MR.activeModel
    total_seats = float(topic.get_first_answer())
    model.interview.work_space["total_paying_seats"] = total_seats
    apply_data(topic, total_seats)
    topic.wrap_topic()

def end_scenario(topic):
    """


    end_scenario(topic) -> None


    **end scenario**
    
    No-op here. Seat count is critical information. Engine cannot
    afford to guess here.
    """
    topic.force_exit() #<--------------------------------------------------- update
    #do nothing, assume 1 seat per subscriber

def apply_data(topic, datapoint):
    """


    apply_data(topic, datapoint) -> None


    ``datapoint`` is an integer count of subscribers to a SaaS product.

    Functio[] #<-----------------------------------------------------------fix
    """
    total_seats = datapoint
    model = topic.MR.activeModel
    current_period = model.time_line.current_period
    company = current_period.content
    #
    subscriber_ids = current_period.ty_directory.get("subscriber")
    all_subscribers = current_period.get_units(subscriber_ids)
    sbr_count = len(subscriber_ids)
    #
    average_seats = total_seats // sbr_count
    #
    subscriber_taxonomy = model.taxonomy.get("subscriber")
    if subscriber_taxonomy:
        subscriber_template = subscriber_taxonomy["standard"]
        subscriber_template.size = average_seats

    #2. put data into model
    seats_remaining = total_seats
    #
    for i in range(sbr_count):
        subscriber = all_subscribers[i]
        if i == (sbr_count - 1):
            applied_seats = seats_remaining
        else:
            applied_seats = average_seats
        subscriber.size = applied_seats
        subscriber.tag(tg_size_by_seat)
        subscriber.unTag(tg_size_by_batch)
        seats_remaining = seats_remaining - applied_seats
        
    else:
        if not seats_remaining == 0:
            raise SeriousErrorInProcessing
    #loop makes sure subscriber population accounts for all paying seats
    #check work:
    sizes_built = [x.size for x in all_subscribers]
    total_built = sum(sizes_built)
    if total_built != total_seats:
        raise SeriousErrorInProcessingAgain

    #3. tag model
    #n/a

    #THE END
                                      
scenarios[None] = scenario_1
#
scenarios["total paying subscriber seats?"] = scenario_2
#
scenarios[message_tools.USER_STOP] = end_scenario

