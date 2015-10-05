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
import BBGlobalVariables as Globals
import BBExceptions




#globals
topic_content = True
name = "average seats per subscriber"
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
tg_populated = "known subscriber pool"
tg_single_product = "describes resources associated with one product"
tg_subscriber_unit = "subscribers"
#
#storing in tags in variables above is solely for the convenience of the author
#



#standard topic prep
user_outline_label = "Subscriber Seats"
requiredTags = ["structure",
                "seat count",
                tg_populated]
optionalTags = ["customers",
                "subscriber count",
                "subscriber population",
                "saas",
                "software",
                "subscription",
                "product",
                tg_subscriber_unit,
                tg_single_product]
#
applied_drivers = dict()
formula_names = []
question_names = []
scenarios = dict()
work_plan = dict()

question_names = ["average seats per subscriber?"]
work_plan["subscriber population"] = 1
work_plan["customers"] = 1
work_plan["structure"] = 1
work_plan["subscriber count"] = 1
work_plan["subscriber seats"] = 1
work_plan["seats"] = 1


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

    Function asks user about their subscriber count. 
    """
    #
    new_question = topic.questions["average seats per subscriber?"]
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
    seats = float(topic.get_first_answer())
    model.interview.work_space["seats_per_subscriber"] = seats
    apply_data(topic, seats)
    topic.wrap_topic()

def end_scenario(topic):
    """


    end_scenario(topic) -> None


    **end scenario**
    
    No-op here. Subscriber count is critical information. Engine cannot
    afford to guess here.
    """
    topic.wrap_to_close()
    #do nothing, assume 1 seat per subscriber

def apply_data(topic, datapoint):
    """


    apply_data(topic, datapoint) -> None


    ``datapoint`` is an integer count of subscribers to a SaaS product.

    Function populates the company's product unit with susbcriber units that
    represent the known count. If datapoint exceeds the maximum permitted unit
    count number, function splits the subscriber base into batch units.

    Function assumes that units are uniformly distributed in age wihin a 2-sigma
    range of 50% of the lifespan. Function assigns dates of conception
    accordingly, provided that all units must be alive as of the end of the
    current period.

    Function assigns units names based on their date of birth and derived from
    a general template.
    """
    model = topic.MR.activeModel
    current_period = model.time_line.current_period
    company = current_period.content
    all_subscribers = []
    subscriber_ids = current_period.ty_directory.get("subscriber")
    if subscriber_ids:
        all_subscribers = current_period.get_units(subscriber_ids)
    subscriber_taxonomy = model.taxonomy.get("subscriber")
    if subscriber_taxonomy:
        subscriber_template = subscriber_taxonomy["standard"]
        all_subscribers.append(subscriber_template)

    #2. put data into model
    for subscriber in all_subscribers:
        subscriber.size =  datapoint

    #3. tag model
    #n/a

    #THE END
                                      
scenarios[None] = scenario_1
#
scenarios["average seats per subscriber?"] = scenario_2
#
scenarios[Globals.user_stop] = end_scenario

