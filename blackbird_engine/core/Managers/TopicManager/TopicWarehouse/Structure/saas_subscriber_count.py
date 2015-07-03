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

from .standard_financials import basic_fins #<------------------------------------- this topic should be able to get by
                                            # w/o importing fins because it should just use the unit in the taxonomy (which already has fins)




#globals
topic_content = True
name = "subscriber count saas"
topic_author = "Ilya Podolyako"
date_created = "2015-06-10"
extra_prep = False
#if extra_prep = True, TopicManager will run this module's prep() function
#after completing standard prep

#store tags this topic uses multiple times in variables to avoid typos
#
tg_basic_depth = "basic analysis depth" #-----------------------------------------------------check phrasing here
#should have ``analysis quality: low", ... medium, high
tg_medium_depth = "medium analysis depth"
tg_high_depth = "in-depth analysis"
#
tg_actual_name = "actual name"
tg_assumed_age_dist = "assumes age distribution"
tg_assumed_name = "assumed name"
tg_assumed_normal_population = "assumes normal population"
tg_batch = "batch unit"
tg_critical = "critical user input"
tg_est_age = "estimated age"
tg_expands_taxonomy = "expands taxonomy"
tg_known_subscriber_pool = "known subscriber pool"
tg_median_age = "assumes median age"
tg_multi_taxonomy = "taxonomy contains multiple types of units"
tg_populated = "known subscriber pool"
tg_single_product = "describes resources associated with one product"
tg_revenue_generating = "revenue generating"
tg_rump = "rump batch"
tg_subscriber_unit = "subscribers"
tg_size_by_batch = "size represents batch of subscribers"

sbr_tags = [tg_assumed_age_dist,
            tg_est_age,
            tg_subscriber_unit,
            tg_revenue_generating,
            tg_size_by_batch]
#
#storing in tags in variables above is solely for the convenience of the author
#



#standard topic prep
user_outline_label = "Subscriber Count"
requiredTags = ["structure",
                "subscriber unit template: ready",
                "taxonomy content"]
optionalTags = ["customers",
                "subscriber count",
                "subscriber population",
                "saas",
                "software",
                "product",
                tg_critical,
                tg_expands_taxonomy,
                tg_single_product,
                tg_assumed_age_dist,
                tg_assumed_normal_population,
                tg_size_by_batch]
#
applied_drivers = dict()
formula_names = []
question_names = []
scenarios = dict()
work_plan = dict()

question_names = ["subscriber count?"]
work_plan["subscriber population"] = 1
work_plan["customers"] = 1
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

    Function asks user about their subscriber count. 
    """
    #
    new_question = topic.questions["subscriber count?"]
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
    stated_count = topic.get_first_answer()
    stated_count = int(stated_count)
    model.interview.work_space["subscriber_count"] = stated_count
    apply_data(topic, stated_count)
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
    #apply standard sizing and depth quality -----------------------------------------------------------------------------------------------------------
    #
    model = topic.MR.activeModel
    current_period = model.time_line.current_period
    company = current_period.content
    #
    #subscribers go in product units. locate or create the appropriate unit.
    #when control flow is done with the tree that follows, ``product`` will be
    #defined.
    product_bbids = current_period.ty_directory.get("product")
    if product_bbids:
        product = current_period.get_units(product_bbids)[0]
        #topic assumes only one product is in place and performs all of its
        #subscription work on the first matching unit
    else:
        #company does not yet contain any product-type units. the model may
        #have a template for this type of unit. if it doesn't, we will create
        #one and store it in taxonomy for future use. 
        basic_template = model.taxonomy["standard"]
        product_taxonomy = model.taxonomy.setdefault("product",dict())
        if product_taxonomy:
            product_template = product_taxonomy["standard"]
        else:
            product_template = basic_template.copy()
            product_template.setName("product unit template")
            product_template.type = "product"
            product_template.tag("product",
                                 "single product",
                                 "generates revenue")
            product_taxonomy["standard"] = product_template
        #
        product = product_template.copy()
        product.setName("Product A")
        product.tag("assumed name")
        #
        company.addComponent(product)
    #
    subscriber_template = model.taxonomy["subscriber"]["standard"]
    #
    unit_count = datapoint
    batch_count = unit_count
    batch_size = 1
    rump_size = 0
    #
    if unit_count > Globals.max_unit_count:
        batch_size = round(unit_count / Globals.batch_count)
        batch_count = unit_count // batch_size
        rump_size = unit_count % batch_size
    #
    tg_quality = tg_basic_depth
    if Globals.mid_unit_count <= batch_count:
        if batch_count < Globals.high_unit_count:
            tg_quality = tg_medium_depth
        else:
            tg_quality = tg_high_depth        
    #
    sbr_label_template = "Subscriber Batch #%s"
    if batch_size == 1:
        sbr_label_template = "Subscriber #%s"
    else:
        sbr_tags.append(tg_batch)
    #
    #configure age distribution for the company's subscribers
    assumed_range = 2
    percent_in_range = 0.95
    #assume normal distribution, where 95% w/in 2 sigma of mean
    #
    gestation = subscriber_template.life.gestation
    ref_date = model.time_line.current_period.start
    sigma = subscriber_template.life.sigma
    assumed_median_age = 0.50 * subscriber_template.life.span
    #assume median age is 50 percent of lifespan
    #
    assumed_youngest_age = assumed_median_age - (assumed_range * sigma)
    assumed_oldest_age = assumed_median_age + (assumed_range * sigma)
    earliest_conception_in_range = ref_date - assumed_oldest_age - gestation
    latest_conception_in_range = ref_date - assumed_youngest_age - gestation
    latest_permitted_conception = min(latest_conception_in_range,
                                     (ref_date - gestation - timedelta(1)))
    earliest_permitted_conception = (ref_date -
                                     gestation -
                                     (subscriber_template.life.span - timedelta(1)))
    #
    increment = ((latest_conception_in_range - earliest_conception_in_range) /
                 (batch_count * percent_in_range))
    #increment represents the amount of time between client acquisitions if the
    #company acquired clients at a uniform rate over time. 
    #
    first_applied_conception = (earliest_conception_in_range -
                                ((1 - percent_in_range) / 2) * batch_count 
                                 * increment)
    #if percent_in_range percent of batches are in the range, then 1-pir percent
    #of batches should be outside the range. the actual number of batches
    #outside the range is that percentage times the batch count. for batches
    #outside the range, half fall on one side and half of the other.
    #
    #here, the function moves the earliest conception date back by the
    #increment for every batch that falls on the older (left-hand) side of the
    #expected 2-sigma age distribution. 
    #
    conception = first_applied_conception
    for i in range(batch_count):
        #
        sbr = subscriber_template.copy()
        #
        label = sbr_label_template % i
        #
        sbr.setName(label)
        #
        sbr.size = batch_size
        conception = conception + increment
        conception = max(conception, earliest_permitted_conception)
        conception = min(conception, latest_permitted_conception)
        #
        sbr.life.date_of_conception = conception
        sbr.life.set_ref_date(ref_date)
        #
        sbr.tag(*sbr_tags)
        #
        if sbr.life.alive:
            product.addComponent(sbr)
        else:
            product.addComponent(sbr)
            c = "Method should only generate living units. Unit %s not alive."
            c = c % sbr.id.bbid
            raise BBExceptions.AnalyticalError(c)
    #
    if rump_size:
        #
        rump_unit = subscriber_template.copy()
        rump_unit.size = rump_size
        label = sbr_label_template % (batch_count + 1)
        #
        rump_unit.life.set_age(assumed_median_age, ref_date)
        #
        rump_unit.tag(tg_rump,
                      tg_median_age,
                      *sbr_tags)
        #
        product.addComponent(rump_unit)
    #    
    product.tag(tg_populated)
    #
    model.tag(tg_single_product)
    model.tag(tg_populated)
    model.tag(tg_assumed_age_dist)
    model.tag(tg_assumed_normal_population)
                                      

scenarios[None] = scenario_1
#
scenarios["subscriber count?"] = scenario_2
#
scenarios[Globals.user_stop] = end_scenario

