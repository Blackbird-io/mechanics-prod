 #PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: TW.Structure.Deterministic.RetailExistingStores
"""

Content module for a topic that builds out the business unit structure of a
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
from datetime import date, timedelta

import BBExceptions
import BBGlobalVariables as Globals
import tools

from data_structures.modelling.business_unit import BusinessUnit
from data_structures.modelling.life_stage import LifeStage
from data_structures.valuation.company_value import CompanyValue

from .. import SharedKnowledge as SubjectKnowledge
from .. import standard_financials



#globals
name = "Retail Existing Store Structure"
topic_author = "IOP"
date_created = "2015-05-06"
topic_content = True
extra_prep = False


#standard prep
#
requiredTags = ["Retail"]
optionalTags = ["standard analysis depth",
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
        #only do transform if model_industry is a string, not a None
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

    Scenario retrieves user response about number of units in the company and
    then asks about unit lifespan. Scenario uses max and expected (shadow)
    lifespan values from Structure.SharedKnowledge. 
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
        #only do transform if model_industry is a string, not a None
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
        new_Q.input_array[0].shadow = (life_in_years * 12) * 0.40
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
    top_bu = M.time_line.current_period.content
    dob_company_date = top_bu.life.date_of_birth
    dob_company_string = dob_company_date.isoformat()
    #put in work_space to save work in later scenarios
    M.interview.work_space["earliest_store_open"] = dob_company_string
    #
    industry_standard = SK.months_to_first_unit["retail"]
    shift = timedelta(industry_standard * Globals.days_in_month)
    anchor_date = dob_company_date + shift
    #
    new_Q = topic.questions["first store open date?"]
    #set bounds for the input element
    new_Q.input_array[0].r_min = dob_company_string
    new_Q.input_array[0].r_max = date.today().isoformat()
    new_Q.input_array[0].shadow = anchor_date.isoformat()
    #
    topic.wrap_scenario(new_Q)

def scenario_5(topic):
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
    adj_r = tools.parsing.date_from_iso(R)
    M.interview.work_space["earliest_store_open"] = R
    M.interview.work_space["first_dob_date"] = adj_r
    #
    industry_standard = SK.months_to_first_unit["retail"]
    shift = timedelta(industry_standard * 30)
    #timedelta in days
    anchor_date = date.today() - shift
    anchor_string = anchor_date.isoformat()
    #
    new_Q = topic.questions["latest store open date?"]
    #set bounds for the input element
    new_Q.input_array[0].r_min = R
    new_Q.input_array[0].r_max = date.today().isoformat()
    new_Q.input_array[0].shadow = anchor_string
    #
    topic.wrap_scenario(new_Q)

    #ask about last store
    #use date as ceiling on dob
    #also compute time to open store =  (first_dob - last_dob)/no_of_stores
    #embed that period in the model as unit gestation
    
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
    #
    M = topic.MR.activeModel
    #
    #Step 1:
    #Retrieve and format user response
    R = topic.get_first_answer()
    adj_R = tools.parsing.date_from_iso(R)
    M.interview.work_space["latest_store_open"] = R
    #
    #Step 2:
    #Now, make a business unit that represents the company's standard.
    #Topic will create and insert actual working units into the model by
    #copying and customizing this template.
    #
    #2.1 - configure model (logic used to be in starter)
    if M.time_line.current_period.content:
        top_bu = M.time_line.current_period.content
    else:
        top_name = (M.name or Globals.default_unit_name)
        top_bu = BusinessUnit(top_name)
        M.time_line.current_period.setContent(top_bu)  
    #
    standard_fins = standard_financials.basic_fins.copy()
    M.defaultFinancials = standard_fins.copy()
    top_bu.setFinancials(standard_fins.copy())
    atx = CompanyValue()
    top_bu.setAnalytics(atx)
    #
    bu_template = BusinessUnit("Standard Store Unit", standard_fins)
    #figure out unit lifespan, set accordingly
    life_in_years = M.interview.work_space["unit_life_years"]
    life_in_days = life_in_years * Globals.days_in_year
    bu_template.life.span = timedelta(life_in_days)
    ref_date = M.time_line.current_period.end
    bu_template.life.set_ref_date(ref_date)
    #figure out unit gestation
    first_dob_date = M.interview.work_space["first_dob_date"]
    latest_dob_date = adj_R
    unit_count = M.interview.work_space["unit_count"]
    #to estimate unit gestation (time from moment of conception/decision to
    #doors opening), calculate how much time per unit it took the company to
    #open all existing units after the first one.
    avg_gestation = ((latest_dob_date - first_dob_date)/
                              (unit_count - 1))
    #adjust gestation to max of average time to open a store and time to open
    #first store. average time can be skewed materially if company prepared
    #stores in batches (eg, 5 openings at a time).
    first_gestation = first_dob_date - top_bu.life.date_of_birth
    step_up = SK.gestation_rate_boost
    avg_gestation = max(avg_gestation,
                        (first_gestation * (1 - step_up)))
    #assume company gets 20% faster at opening units; more advanced topics
    #ask questions first.
    bu_template.life.gestation = avg_gestation
    M.interview.work_space["average_gestation_days"] = avg_gestation
    #
    #figure out life stage pattern
    months_to_mature = M.interview.work_space["months_to_mature"]
    period_to_mature = timedelta(months_to_mature * Globals.days_in_month)
    youth_ends_percent = int(period_to_mature/bu_template.life.span * 100)
    if youth_ends_percent < 50:
        #maturation less than 50% of lifespan; create custom life stage pattern
        maturity = bu_template.life._stages.by_name["maturity"]
        decline = bu_template.life._stages.by_name["decline"]
        #
        maturity["start"] = youth_ends_percent + 1
        decline["start"] = youth_ends_percent + 30 + 1
        #make sure stages reorganized data now that we've changed start points
        bu_template.life._stages.organize()
        #
        tag1 = "long adolescence"
        tag2 = "rapid decline"
        tag3 = "unusual LifeCycle"
        bu_template.tag(tag1, tag2, tag3)
    else:
        #compared to common sense expectations for how long a company will wait
        #for a unit to mature, known maturation takes too long. scenario assumes
        #the error occurs because the user underestimated the life span of their
        #units. adjust the life span to 3x maturity.
        bu_template.life.span = period_to_mature * 3
        tag4 = "standard LifeCycle"
        tag5 = "pro forma lifeSpan"
        tag6 = "response difficulty"
        bu_template.tag(tag4, tag5, tag6)
    #template configuation complete
    M.tag("defined standard operating unit")
    #
    #Step 3:
    #Add template to model taxonomy
    M.taxonomy["standard"] = bu_template
    M.taxonomy["operating"] = dict()
    M.taxonomy["operating"]["standard"] = bu_template
    #
    #later topics can sub-type "operating" into "small", "large", etc. since the
    #custom Taxonomy class doesnt unpickle correctly, ``taxonomy`` is a simple
    #dictionary where the "standard" key always points to a business unit object
    #and all other keys point to other dictionaries with a similar
    #configuration.
    #
    #Step 4:
    #Use the template operating unit to create a batch of clones. The clones
    #will go in to the model as actual working components. 
    batch = {}
    #clone bU0 x #of units
    for n in range(unit_count):
        clone = bu_template.copy(enforce_rules = False)
        c_name = "Existing %s" % n
        clone.setName(c_name)
        clone.id.assignBBID(clone.name)
        batch[clone.id.bbid] = clone
    ordered_batch = []
    for bbid in sorted(batch.keys()):
        unit = batch[bbid]
        ordered_batch.append(unit)
    #
    #Step 5:
    #Customize the batch units and insert them into the top_unit. This scenario
    #assumes that clones are identical except for their age. The scenario also
    #assumes that the first and last store are still open and adjusts their life
    #spans accordingly. Since user has specified an existing store count,
    #allowing some of the early stores to close by virtue of age would require
    #the company to have opened new stores. The topic does not make this
    #assumption on its own. <------------------------------------------------------------------------
    first_bu = ordered_batch.pop(0)
    first_bu.life.date_of_conception = first_dob_date - avg_gestation
    if not first_bu.life.alive:
        extend_life(first_bu, ref_date)
    top_bu.addComponent(first_bu)
    #
    last_bu = ordered_batch.pop()
    last_bu.life.date_of_conception = latest_dob_date - avg_gestation
    if not last_bu.life.alive:
        extend_life(last_bu, ref_date)
    top_bu.addComponent(last_bu)
    #ordered_batch now 2 units shorter than unit_count. apply distribution to
    #all remaining units.
    next_conception_date = first_bu.life.date_of_birth
    #assume that company is creating units at a uniform rate over time. can
    #eventually modify this to look like a curve that's fast early and slow
    #later (log curve).
    latest_conception_date = latest_dob_date - avg_gestation
    for bu in ordered_batch:
        bu.life.date_of_conception = next_conception_date
        #
        #the user told blackbird how many units they have operating
        #**right now**. blackbird translates right now into ref_date and the
        #count into units that are alive as of the ref date. since units must
        #have compelted gestation to count as alive, blackbird can also
        #determine the latest possible date the user could have conceived a
        #unit (based on blackbird's current assumptions about unit life cycle).
        #
        next_conception_date = next_conception_date + avg_gestation
        next_conception_date = min(next_conception_date,
                                   latest_conception_date)
        if not bu.life.alive:
            extend_life(bu, ref_date)
            #
            #assume that an existing store can be no more than 90% of the way
            #through their life as of the ref date. adjust unit life
            #accordingly. in other words, assume that some of the earlier
            #stores can live longer than the cookie cutter new ones.
            #
        #
        if bu.life.alive:
            top_bu.addComponent(bu)
        else:
            #
            c = "Topic detected non-living unit: \n%s\nTopic expected to"
            c += " generate living units only."
            c = c % bu
            raise BBExceptions.BBAnalyticalError(c)
    #
    ##provide guidance for additional processing
    small_num = 10
    med_num = 50
    more_structure_processing = False
    tag7 = "small number of units"
    tag8 = "medium number of units"
    tag9 = "large number of units"
    if unit_count <= small_num:
        top_bu.tag(tag7)
        M.tag(tag7)
    elif unit_count <= med_num:
        top_bu.tag(tag8)
        M.tag(tag8)
        M.tag("medium analysis depth permitted")
        more_structure_processing = True
    else:
        top_bu.tag(tag9)
        M.tag(tag9)
        M.tag("medium analysis depth permitted")
        M.tag("high analysis depth permitted")
        more_structure_processing = True
    #
    if more_structure_processing:
        M.tag("check for stores in progress")
        #this tag functions like a homing beacon.
        i_structure = M.interview.path.indexByName("structure")
        step_structure = M.interview.path[i_structure]
        step_structure.guide.quality.setStandards(3, 5)
        #
        step_structure.guide.selection.eligible.clear()
        #since we modified the criteria on the focal point, now have to clear
        #the cache of eligible topics to force yenta to search through the full
        #catalog. otherwise, yenta would only see the eligible topics from before
        #the new tags. 
    #                 
    topic.wrap_topic()

def extend_life(bu, ref_date, max_current_age = 0.90):
    """


    extend_life(bu, ref_date, max_current_age = 0.90) -> None


    Function adjusts unit lifespan so that the unit 90% old as of ref date.
    Function only updates unit lifespan if the new value is longer than the
    existing one. 
    """
    known_period = ref_date - bu.life.date_of_birth
    adj_lifespan = known_period * (1/ max_current_age)
    adj_lifespan = max(timedelta(0), adj_lifespan)
    #life span must be positive
    if adj_lifespan > bu.life.span:
        bu.life.span = adj_lifespan
        bu.life._date_of_death = None
        
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
scenarios["first store open date?"] = scenario_5
scenarios["latest store open date?"] = scenario_6
#
scenarios[Globals.user_stop] = end_scenario

