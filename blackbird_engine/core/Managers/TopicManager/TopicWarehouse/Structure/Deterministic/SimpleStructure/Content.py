 #PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: TW.Structure.Deterministic.SimpleStructure.Content.
"""

Content module for a topic that builds out the business unit structure of a
simple model.
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
import Tools

from DataStructures.Modelling.BusinessUnit import BusinessUnit

from . import PrivateKnowledge
from ... import SharedKnowledge as SubjectKnowledge


#globals
name = "Simple Deterministic Structure"
topic_author = "IOP"
date_created = "2015-04-01"
topic_content = True
extra_prep = False


#standard prep
#
requiredTags = []
optionalTags = ["Simple","Deterministic","Structure","Generic"]
applied_drivers = dict()
scenarios = dict()
    #ks are question names, None, or user_stop
    #values are scenario functions
work_plan = dict()

formula_names = []
question_names = ["number of business units?",
                  "unit lifespan in years?",
                  "months to unit maturity?"]
work_plan["structure"] = 1

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
    M.interview.work_space["number of units"] = number_of_units
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
    M.interview.work_space["unit lifespan in years"] = life_in_years
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

    **closing**
    
    Scenario concludes with wrap_topic().

    Scenario uses information collected to create and insert business units.
    Scenario configures lifespan to be either as user specified or, if
    maturation takes over 50% of stated life, 3x maturation. Scenario then
    creates class-specific copies of the standard unit and adds them to Model's
    current period top-level. 
    """
    M = topic.MR.activeModel
    Q = topic.MR.activeQuestion
    R = topic.MR.activeResponse
    #
    months_to_mature = float(topic.get_first_answer())
    M.interview.work_space["months to mature"] = months_to_mature
    #
    number_of_units = M.interview.work_space["number of units"]
    life_in_years = M.interview.work_space["unit lifespan in years"]
    ref_date = None
    #
    life_in_seconds = Tools.Parsing.monthsToSeconds((life_in_years * 12))
    mature_in_seconds = Tools.Parsing.monthsToSeconds(months_to_mature)
    youth_ends_percent = int(mature_in_seconds/life_in_seconds * 100)
    #
    stnd_fins  = M.defaultFinancials.copy()
    #
    bu_0 = BusinessUnit("BU0: Template", stnd_fins)
    bu_0.lifeCycle.setLifeSpan(life_in_seconds)
    if Globals.fix_ref_date:
        ref_date = Globals.t0
    else:
        ref_date = time.time()
    bu_0.lifeCycle.setRefDate(ref_date)
    #
    if youth_ends_percent < 50:
        #maturation less than 50% of lifespan
        bu_0.lifeCycle.allLifeStages[0].ends = youth_ends_percent
        bu_0.lifeCycle.allLifeStages[1].starts = youth_ends_percent + 1
        bu_0.lifeCycle.allLifeStages[1].ends = youth_ends_percent + 30
        bu_0.lifeCycle.allLifeStages[2].starts = youth_ends_percent + 30 + 1
        tag1 = "long adolescence"
        tag2 = "rapid decline"
        tag3 = "unusual LifeCycle"
        bu_0.tag(tag1, tag2, tag3)
    else:
        #maturation too long, assume lifespan too short, set to 3x maturity
        bu_0.lifeCycle.setLifeSpan(mature_in_seconds * 3)
        tag4 = "standard LifeCycle"
        tag5 = "pro forma lifeSpan"
        tag6 = "response difficulty"
        bu_0.tag(tag4, tag5, tag6)
    #
    #clone bU0 x #of units
    component_batch = []
    for n in range(number_of_units):
        clone = bu_0.copy(enforce_rules = False)
        #clone was originally a deepcopy; can try reverting if doesnt work
        c_name = "Cloned Unit %s" % n
        clone.setName(c_name)
        clone.id.assignBBID(clone.name)
        fixed_age = 0.40 * life_in_seconds
        #assume a particular age, uniform across units
        clone.lifeCycle.setInitialAge(fixed_age, ref_date)
        component_batch.append(clone)
        M.currentPeriod.content.addComponent(clone)
    #
    tag7 = "small number of units"
    small_num = 10
    tag8 = "medium number of units"
    med_num = 50
    tag9 = "large number of units"
    parent_bu = M.currentPeriod.content
    if number_of_units <= small_num:
        parent_bu.tag(tag7)
    elif number_of_units <= med_num:
        parent_bu.tag(tag8)
    else:
        parent_bu.tag(tag9)
    #
    topic.wrap_topic()
        
def end_scenario(topic):
    #user pressed stop interview in middle of question
    #if know number of units, good to go off GeneralKnowledge; otherwise, dont bother
    pass

scenarios[None] = scenario_1
#
scenarios["number of business units?"] = scenario_2
scenarios["unit lifespan in years?"] = scenario_3
scenarios["months to unit maturity?"] = scenario_4
#
scenarios[Globals.user_stop] = end_scenario

