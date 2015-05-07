 #PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: TW.Structure.Deterministic.RetailExistingStores
"""

Content module for a topic that builds out the businessf unit structure of a
retail business.
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
import datetime
import time

import BBGlobalVariables as Globals
import Tools

from DataStructures.Modelling import CommonLifeStages
from DataStructures.Modelling.BusinessUnit import BusinessUnit
from DataStructures.Modelling.LifeStage import LifeStage

from .. import SharedKnowledge as SubjectKnowledge


#globals
name = "Retail Existing Store Structure"
topic_author = "IOP"
date_created = "2015-05-06"
topic_content = True
extra_prep = False


#standard prep
#
requiredTags = ["Retail"]
optionalTags = ["Simple",
                "Deterministic",
                "Structure",
                "Existing",
                "In-Place",
                "As-Built"]
applied_drivers = dict()
scenarios = dict()
    #ks are question names, None, or user_stop
    #values are scenario functions
work_plan = dict()

formula_names = []
question_names = ["number of business units?",
                  "unit lifespan in years?",
                  "months to unit maturity?",
                  "first store open date?",
                  "latest store open date?"]

work_plan["structure"] = 2

SK = SubjectKnowledge

#scenarios
#
#define scenario functions, then fill out scenarios dictionary
#scenarios must end with either:
    #scenarios that ask a question - topic.wrap_scenario()
    #scenarios that complete processing - topic.wrap_topic()
    #scenarios that respond to a user stop - topic.wrap_to_end()
#
def scenario_1(topic):
    """


    scenario_1(topic) -> None


    **opening**

    Asks user about the number of units their company has. Max units capped
    at 1000 (one thousand). 
    """
    M = topic.MR.activeModel
    new_Q = topic.questions["number of business units?"]
    model_industry = M.header.profile.get("industry")
    #use dict.get() because header might not specify industry
    unit_label = None
    if model_industry:
        model_industry = model_industry.casefold()
        #only do transform is model_industry is a string, not a None
        unit_label = SubjectKnowledge.unit_labels.get(model_industry)
        M.interview.work_space["industry"] = model_industry
    if unit_label:
        new_Q.context["unit_label_plural"] = unit_label["plural"]
        #SubjectKnowledge unit_label values are a dict of singular and plural
        new_Q.input_array[0]._active = True
        new_Q.input_array[0].r_max = SK.unit_number_limit
        M.interview.work_space["unit label"] = unit_label
    topic.wrap_scenario(new_Q)

def scenario_2(topic):
    """


    scenario_2(topic) -> None


    Scenario concludes with wrap_scenario(Q).

    Scenario retrieves number of units in company, asks about unit lifespan.
    Scenario uses max and expected (shadow) lifespan values from
    Structure.SharedKnowledge. 
    """
    #
    M = topic.MR.activeModel
    Q = topic.MR.activeQuestion
    R = topic.MR.activeResponse
    number_of_units = int(topic.get_first_answer())
    M.interview.work_space["unit_count"] = number_of_units
    #save answer for later processing
    #
    #prep follow up question
    new_Q = topic.questions["unit lifespan in years?"]
    unit_label = M.interview.work_space.get("unit label")
    #use dict.get() because model may not have a known unit label
    if unit_label:
        new_Q.context["unit_label_singular"] = unit_label["singular"]
    new_Q.input_array[0].r_max = max(30,
                                     max(SK.unit_life_spans.values()))
    #default max lifespan of 30 years, activated if general knowledge empty
    model_industry = M.interview.work_space.get("industry")
    if model_industry:
        model_industry = model_industry.casefold()
        #only do transform is model_industry is a string, not a None
        new_Q.input_array[0].shadow = SK.unit_life_spans.get(model_industry)
        #shadow serves as anchor, should be approximate mean
    else:
        new_Q.input_array[0].shadow = SK.unit_life_spans["default"]
    topic.wrap_scenario(new_Q)

def scenario_3(topic):
    """


    scenario_3(topic) -> None


    Scenario concludes with wrap_scenario(Q).

    Scenario retrieves user answer about unit life span and asks them how long
    a unit takes to mature. Scenario sets anchor to either SubjectKnowledge
    value or 40% of lifespan. 
    """
    M = topic.MR.activeModel
    Q = topic.MR.activeQuestion
    R = topic.MR.activeResponse
    life_in_years = float(topic.get_first_answer())
    M.interview.work_space["unit_life_years"] = life_in_years
    #save answer for later processing
    #
    #select question
    new_Q = topic.questions["months to unit maturity?"]
    #
    #customize question
    #set context
    unit_label = M.interview.work_space.get("unit label")
    #use dict.get() because model may not have a known unit label
    if unit_label:
        new_Q.context["unit_label_singular"] = unit_label["singular"]
    #
    #adjust input parameters
    new_Q.input_array[0].r_max = max(120,
                                     max(SK.unit_months_to_mature.values()))
    #default max months to mature is 120
    model_industry = M.interview.work_space.get("industry")
    if model_industry:
        model_industry = model_industry.casefold()
        #only do transform is model_industry is a string, not a None
        new_Q.input_array[0].shadow = SK.unit_months_to_mature.get(model_industry)
    else:
        new_Q.input_array[0].shadow = (life_in_years * 12 ) * 0.40
        #assume by default units mature 40% of the way through their life
    topic.wrap_scenario(new_Q)

def scenario_4(topic):
    """


    scenario_4(topic) -> None

    
    Scenario concludes with wrap_scenario(Q).

    Scenario receives a message with a response about months to mature and
    retrieves the answer.

    Scenario then asks when the user opened their first store. Scenario sets
    anchor to standard industry period after company founding. 
    """
    M = topic.MR.activeModel
    #
    months_to_mature = float(topic.get_first_answer())
    M.interview.work_space["months_to_mature"] = months_to_mature
    #
    top_bu = M.currentPeriod.content
    dob_company_seconds = top_bu.lifeCycle.dateBorn
    dob_company_date = datetime.date.fromtimestamp(dob_company_seconds)
    dob_company_string = dob_company_date.isoformat()
    #put in work_space to save work in later scenarios
    M.interview.work_space["earliest_store_open"] = dob_company_string
    #
    industry_standard = SK.months_to_first_unit["retail"]
    shift = Tools.Parsing.monthsToSeconds(industry_standard)
    anchor_seconds = int(dob_company_standards + shift)
    anchor_string = datetime.date.fromtimestamp(anchor_seconds).isoformat()
    #
    new_Q = topic.questions["first store open date?"]
    #set bounds for the input element
    new_Q.input_array[0].r_min = dob_company_string
    new_Q.input_array[0].r_max = datetime.date.today().isoformat()
    new_Q.input_array[0].shadow = anchor_string
    #
    topic.wrap_scenario(new_Q)

def scenario_5
    """


    scenario_5(topic) -> None


    Scenario concludes with wrap_scenario(Q).

    
    Scenario receives a message with a response about the first store opening
    date. Scenario retrieves the message and formats the answer into seconds.

    Scenario then asks user about their most recent store opening.     
    """
    M = topic.MR.activeModel
    R = topic.get_first_answer()
    #R is a YYYY-MM-DD string
    adj_r = Tools.Parsing.seconds_from_iso(R)
    M.interview.work_space["earliest_store_open"] = R
    M.interview.work_space["first_dob_seconds"] = adj_r
    #
    industry_standard = SK.months_to_first_unit["retail"]
    shift = Tools.Parsing.monthsToSeconds(industry_standard)
    anchor_seconds = int(time.time() - shift)
    anchor_string = datetime.date.fromtimestamp(anchor_seconds).isoformat()
    #
    new_Q = topic.questions["latest store open date?"]
    #set bounds for the input element
    new_Q.input_array[0].r_min = R
    new_Q.input_array[0].r_max = datetime.date.today().isoformat()
    new_Q.input_array[0].shadow = anchor_string
    #
    topic.wrap_scenario(new_Q)

    #ask about last store
    #use date as ceiling on dob
    #also compute time to open store =  (first_dob - last_dob)/no_of_stores
    #embed that period as gestation
    
def scenario_6(topic):
    """


    scenario_6(topic) -> None


    **closing**
    
    Scenario concludes with wrap_topic().

    Scenario uses information collected to create and insert business units.
    Scenario configures lifespan to be either as user specified or, if
    maturation takes over 50% of stated life, 3x maturation. Scenario then
    creates class-specific copies of the standard unit and adds them to Model's
    current period top-level. 
    """
    
    M = topic.MR.activeModel
    top_bu = M.currentPeriod.content
    #
    R = topic.get_first_answer()
    adj_R = Tools.Parsing.seconds_from_iso(R)
    #
    unit_count = M.interview.work_space["unit_count"]
    #
    first_dob_seconds = M.interview.work_space["first_dob_seconds"]
    latest_dob_seconds = adj_R
    #
    months_to_mature = M.interview.work_space["months_to_mature"]
    gestation_seconds = ((latest_dob_seconds - first_dob_seconds)/
                              (unit_count - 1))
    #unit gestation should show approximately how long it takes to take
    #a new unit from idea to open doors
    #
    #adjust gestation to max of average time to open a store and time to open
    #first store. average time can be skewed materially if company prepared
    #stores in batches (eg, 5 openings at a time).
    first_unit_runway = first_dob_seconds - top_bu.lifeCycle.dateBorn
    gestation_seconds = max(gestation_seconds,
                            (first_unit_runway * (1-0.20)))
    #assume company gets 20% faster at opening units; more advanced topics
    #ask questions first.
    #                       
    M.interview.work_space["unit_gestation_seconds"] = gestation_seconds
    #
    life_in_years = M.interview.work_space["unit_life_years"]
    life_in_seconds = Tools.Parsing.monthsToSeconds((life_in_years * 12))
    life_in_seconds = life_in_seconds + gestation_seconds
    #
    #for purposes of Blackbird, life begins at conception
    #
    mature_in_seconds = Tools.Parsing.monthsToSeconds(months_to_mature)    
    youth_ends_percent = int(mature_in_seconds/life_in_seconds * 100)
    ref_date = None
    if Globals.fix_ref_date:
        ref_date = Globals.t0
    else:
        ref_date = time.time()
    #
    standard_fins = M.defaultFinancials.copy()
    bu_template = BusinessUnit("Unit Template", standard_fins)
    bu_template.life.set_gestation(gestation_seconds)
    bu_template.life.set_duration(life_in_seconds)
    bu_template.life.set_ref_date(ref_date)
    #
    if youth_ends_percent < 50:
        #maturation less than 50% of lifespan
        #
        bu_template.life.stages["all"]["maturity"].starts = youth_ends_percent
        bu_template.life.stages["all"]["decline"].starts = (youth_ends_percent + 30)
        bu_template.life.organize_stages()
        #
        ##by default, include youth, maturity, and decline in all. organize()
        #should ignore stages with None as start. only start should be required
        #end should be optional. default pattern is youth.start = 0,
        #maturity.start  = 30, decline.start = 70. always end at 100. organize
        #should weed out anything below start. if end specified on a period that
        #makes it in, organize() also weeds out any candidates that start below
        #the mandated end. the three default stages dont have ends. 
        #
        tag1 = "long adolescence"
        tag2 = "rapid decline"
        tag3 = "unusual LifeCycle"
        bu_template.tag(tag1, tag2, tag3)
    else:
        #maturation too long, assume lifespan too short, set to 3x maturity
        bu_template.life.set_duration(mature_in_seconds * 3)
        tag4 = "standard LifeCycle"
        tag5 = "pro forma lifeSpan"
        tag6 = "response difficulty"
        bu_template.tag(tag4, tag5, tag6)
    #
    batch = {}
    #clone bU0 x #of units
    for n in range(unit_count):
        clone = bu_template.copy(enforce_rules = False)
        c_name = "Existing %s" % n
        clone.setName(c_name)
        clone.id.assignBBID(clone.name)
        batch[clone.id.bbid] = clone
    #
    ordered_batch = []
    for bbid in sorted(batch.keys()):
        unit = batch[bbid]
        ordered_batch.append[unit]
    #
    first_bu = ordered_batch.pop(0)
    first_bu.life.set_dob(first_dob_seconds)
    last_bu = ordered_batch.pop()
    last_bu.life.set_dob(last_dob_seconds)
    #ordered_batch now 2 units shorter than unit_count. apply distribution to
    #all remaining units.
    #
    #assume that company is creating units at a uniform rate over time. can
    #eventually modify this to look like a curve that's fast early and slow
    #later (log curve).
    #
    conception_date = first_bu.life.date_of_birth
    for bu in ordered_batch:
        bu.life.set_conception(conception_date)
        conception_date = conception_date + gestation_seconds
    #
    #make sure have same number of units in batch as unit_count. also make
    #sure that all units are alive as of ref_date. if not all alive, logic is
    #wrong, because they all must exist right now, per user's instructions. <----------------------------!!!
    #
    #when all is checked out, add the components to top_bu
    top_bu.addComponent(clone)
    #
    tag7 = "small number of units"
    small_num = 10
    tag8 = "medium number of units"
    med_num = 50
    tag9 = "large number of units"
    if unit_count <= small_num:
        top_bu.tag(tag7)
    elif unit_count <= med_num:
        top_bu.tag(tag8)
    else:
        top_bu.tag(tag9)
    #
    ####### <- tag with Ready_For_Growth_Analysis or smtg, which Growth requires as a reqd tag---------
    #                 
    topic.wrap_topic()
    
        
def end_scenario(topic):
    #user pressed stop interview
    #if know number of units, can do a fair amount of work based on SubjectKnowledge
    #here, would mean a topic structure that delegates scenario work to specialized functions
    #then, can use end_scenario to delegate to those same functions in order, albeit with
    #assumptions instead of actual user responses.
    #
    pass

scenarios[None] = scenario_1
#
scenarios["number of business units?"] = scenario_2
scenarios["unit lifespan in years?"] = scenario_3
scenarios["months to unit maturity?"] = scenario_4
#
scenarios[Globals.user_stop] = end_scenario

