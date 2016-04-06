#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: TW.Structure.Deterministic.FutureStores_3yrs
"""

Topic asks about expected store count over the next 3 years.

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
import operator

from datetime import date, timedelta
from tools import for_messages as message_tools

from .. import SharedKnowledge as SubjectKnowledge




#globals
name = "stores in progress"
topic_author = "IOP"
date_created = "2015-06-05"
topic_content = True
extra_prep = False


#standard prep
requiredTags = ["retail",
                "completed template",
                "ready for growth analysis",
                "medium analysis"] #--------------------------------------------------------------

optionalTags = ["In-Progress",
                "signed leases",
                "Not Yet Built",
                "LifeCycle",
                "Structure",
                "Growth"
                "uses extrapolation"]

applied_drivers = dict()
scenarios = dict()
    #ks are question names, None, or user_stop
    #values are scenario functions
work_plan = dict()

formula_names = []
question_names = ["store count over next 3 years?"]
work_plan["structure"] = 1
work_plan["growth"] = 2

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

    Scenario concludes with wrap_scenario(Q)
    
    Ask user about expected future store count.
    """
    M = topic.MR.activeModel
    top_bu = M.current_period.content
    ref_year = M.current_period.end.year
    base_count = top_bu.components.living
    #
    new_Q = topic.questions["store count over next 3 years?"]
    #
    #customize input_elements
    for i in range(len(new_Q.input_array)):\
        element = new_Q.input_array[i]
        element.caption = str(ref_year + i)
        #start w the year after ref_year
        element.shadow = str(base_count)
        element.r_steps = 1
    topic.wrap_scenario(new_Q)

def scenario_2(topic):
    """


    scenario_2(topic) -> None


    **closing**
    
    Scenario concludes with wrap_topic().

    assemble user response into datapoint dictionary
    """
    #
    #get the response, convert into dictionary
    #
    portal_response = topic.MR.activeResponse
    store_targets = dict()
    for response_element in portal_response:
        year = int(response_element["caption"])
        store_targets[year] = response_element["response"]
    #
    M.interview.work_space["store_targets"] = store_targets.copy()
    apply_data(topic, store_targets, close_units = True)
    topic.wrap_topic()

def apply_data(topic, datapoint, close_units = True):
    """


    apply_data(topic, datapoint) -> None
    

    ``datapoint`` : dictionary of year integers to expected store count. 
    
    """
    #
    #for each of the 3 years, apply uniform distribution w/in gestation to get
    #dob w/in the year. assume no openings in 4q.

    #check whether any units would have to be conceived now.
    #ask accordingly. check whether any units would have to be closed.
    #
    #deliver notes as [missing, dict[year] = closed].
        #missing are units that should be gestating now to hit target
        #closed are units that will need to be closed to hit target
            #can close based on revenue or ebitda or smtg
    #
    #extrapolate all
    #add non-gestating units in future periods.
        #add special_ex tag to those periods
        #add milestones to those periods
        #
    #topic should only run once template configuration is complete
        #in other words, growth should go last in path
        #
    #
    #can extrapolate the whole timeline
    #then add business units to the right period
        #tag that period's top-level components as special
    #
    model = topic.MR.activeModel
    ops_unit_template = model.taxonomy["operating"].standard
    tag_catalog = topic.tagManager.catalog
    #
    ref_period = model.time_line.current_period
    model.time_line.extrapolate_all()
##    future = model.time_line.get_segments()[2]
##    model.time_line.extrapolate_dates(current_period, future)
##    #for speed, can extrapolate future only
    #
    closing_rule = operator.attrgetter(life.percent) * -1
    #oldest units first
    #
    planned_store_index = 0
    units_missing = 0
    units_closed = dict()
    #
    for year in datapoint:       
        year_start = date(year, 1, 1)
        year_end = date(year, 12, 31)
        last_target_period = model.time_line.find_period(year_end)
        earliest_changed_period = None
        #
        existing_unit_count = last_target_period.content.components.living
        target_unit_count = datapoint[year]
        units_needed = target_unit_count - existing_unit_count
        if units_needed > 0:
            #
            interval = (timedelta(365) * 0.75) / units_needed
            #assume no one opens stores in 4Q
            #
            for i in range(units_needed):
                planned_store_index += i
                scheduled_dob = year_start + (interval * i)
                #assume stores open evenly throughout the interval
                #
                new_unit = ops_unit_template.copy()
                new_unit.life.set_age(timedelta(0), scheduled_dob)                
                #set date when unit is born to start of year plus increment
                label = "Planned Store #%s (%s)"
                label = label % (planned_store_index, scheduled_dob.isoformat()[:7])
                new_unit.setName(label)
                #
                if new_unit.life.date_of_conception <= ref_date:
                    #unit should exist at ref date in order to open on time, but
                    #does not. add to units_missing
                    units_missing += 1
                else:
                    #insert into timeline
                    magic_moment = new_unit.life.date_of_conception
                    magic_period = model.time_line.find_period(magic_moment)
                    #
                    #remember the first period this loop modified so later logic
                    #can extrapolate the smallest amount of dates possible
                    if i == 0:
                        earliest_changed_period = magic_period
                    elif magic_period.start < earliest_changed_period.start:
                        earliest_changed_period = magic_period
                    #
                    parent_unit = magic_period.content
                    parent_unit.add_component(new_unit)
                    parent_unit.components.tag(special_ex_tag)
                    #
        else:
            #units needed is negative: too many units exist at year end
            if not close_units:
                pass
            else:
                #
                #call authorizes function to close units as necessary
                #
                
                existing_units = last_target_period.content.components.get_living()
                closing_queue = sorted(existing_units, key = closing_rule)
                #
                closings = abs(units_needed)
                closings = min(closings, len(closing_queue))
                #
                for i in closings:
                    closing_queue[i].life.kill()
                    #tag that you are forcing some closings --------------------------------------
                #
                units_closed[year] = closings
                #
                last_target_period.tag("closed units")
                last_target_period.content.tag("closed units")
                model.tag("closed units: future",
                          "closed units to conform to projections",
                          "projections imply future unit closures")
                
        #
        #extrapolate forward again to apply changes to future, from this year
        #on. so after working to insert the units necessary for 2018 (starting
        #in nov 2017), ex periods from nov 2017 on.
        #
        earliest_moment = earliest_changed_period.start
        relative_future = model.time_line.get_segments(ref_date = earliest_moment)[2]
        model.time_line.extrapolate_dates(earliest_changed_period, relative_future)        
        #
    #
    #add to milestones? 
    #
    #add tags as necessary
    model.tag("stores in progress")
    #
    return [units_missing, units_closed]
        
def end_scenario(topic):
    """


    end_scenario(topic) -> None


    **end scenario**

    Scenario concludes with wrap_to_end()

    On user interrupt, scenario assumes that 0 stores are in progress and runs
    apply_data() accordingly. 
    """
    assumption = 0
    apply_data(topic, assumption)
    topic.wrap_to_end()

#
scenarios[None] = scenario_1
#
scenarios["stores in progress?"] = scenario_2
#
scenarios[message_tools.USER_STOP] = end_scenario

