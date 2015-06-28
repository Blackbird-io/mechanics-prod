#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: TW.Financials.IS.OpEx.Labor.cash_bonus_across_teams
"""

Topic asks about the annual cash bonus as a percentage of salary that teams
across the organization earn, on average. Topic treats bonus as a ratable
expense throughout the year (assumes that company moves cash into a reserve
account as appropriate). 
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
unit_work() 

CLASSES:
n/a
====================  ==========================================================
"""




#imports
import operator

import BBGlobalVariables as Globals

from DataStructures.Modelling.BusinessUnit import BusinessUnit
from DataStructures.Modelling.Driver import Driver
from DataStructures.Modelling.LineItem import LineItem




#globals
topic_content = True
name = "cash bonus percent across teams"
topic_author = "Ilya Podolyako"
date_created = "2015-06-14"
extra_prep = False

#store tags this topic uses multiple times in variables to avoid typos
tg_known_bonus = "known bonus structure"
tg_single_product = "describes resources associated with one product"
tg_variable_comp = "variable compensation"

#standard topic prep
user_outline_label = "Salaries"
requiredTags = ["employee expense",
                "known team composition"]

optionalTags = [tg_single_product,
                "adjust for inflation",
                "bonus",
                "cash bonus",
                "cash compensation",
                "expense",
                "full time employees",
                "incentive compensation",
                "industry-specific compensation scale",
                "operating expense",
                "recurring expense",
                "refines template",
                "salaries",
                "software",
                tg_variable_comp,
                "team-specific analysis",
                "variable",
                "variable teams"]

applied_drivers = dict()
formula_names = []
question_names = []
scenarios = dict()
work_plan = dict()

formula_names = ["set line based on source value and multiplier.",
                 "set line to fixed monthly value."]

question_names = ["annual cash bonus as percent of salary for open teams?"]

work_plan["employee expense"] = 1
work_plan["expenses"] = 1
work_plan["operations"] = 1
work_plan["bonus"] = 1
work_plan["operating expense"] = 1
work_plan["cash bonus"] = 1

#custom prep
def prepare(new_topic):
    #always return the topic
    return new_topic

#drivers:
avg_bonus = Driver()
avg_bonus.setName("average bonus")
applied_drivers["average bonus"] = avg_bonus
#
team_bonus = Driver()
team_bonus.setName("team bonus")
applied_drivers["team bonus"] = team_bonus
#place the driver on the topic, so can access without going through the content
#module's namespace. 


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

    Function asks user about employee bonus across categories. Function
    populates the input elements for the question with the names of the largest
    teams (by  size) in the organization, excluding sales. If the organization
    has a catch-all team (``everyone else`` or ``other``), function pulls the
    team out and places it last in the input array. 
    """
    #
    new_question = topic.questions["annual cash bonus as percent of salary for open teams?"]
    #
    model = topic.MR.activeModel
    #
    model = topic.MR.activeModel
    #
    current_period = model.time_line.current_period
    office_ids = current_period.ty_directory["office"]
    hq = current_period.get_units(office_ids)[0]    
    personnel_bbid = hq.components.by_name["personnel"]
    personnel = hq.components[personnel_bbid]
    teams = personnel.components
    teams = teams.copy()
    #run logic on copy so as not to ruin the original
    #pull out sales team, will figure out their comp separately
    sales_bbid = teams.by_name.get("sales")
    if sales_bbid:
        sales = teams.pop(sales_bbid)
    #
    #pull out the catch-all team to make sure its input element appears
    #last; otherwise, due to unstable dict key order, elements could read
    #"everyone else" []; "dev" []; ...
    #
    everyone_else = None
    everyone_else_bbid = teams.by_name.get("everyone else")
    if not everyone_else_bbid:
        everyone_else_bbid = teams.by_name.get("other")
    if everyone_else_bbid:
        everyone_else = teams.pop(everyone_else_bbid)
    #
    teams_large_to_small = sorted(teams.values(),
                                  key = operator.attrgetter("size"),
                                  reverse = True)
    #
    #configure question w existing roles:
    input_array = new_question.input_array
    #
    ask_about = len(input_array)
    if everyone_else:
        ask_about = len(input_array[:-1])
        #save the last element for everyone_else
    ask_about = min(ask_about, len(teams_large_to_small))
    #if there are fewer teams than element slots, limit accordingly
    #
    for i in range(ask_about):
        element = input_array[i]
        element.main_caption = teams_large_to_small[i].name
        element._active = True
        element.r_min = 0
        element.r_max = 1000
        #when topic gets this question object, elements 2-5 will be inactive.
    else:
        if everyone_else:
            last_element = input_array[ask_about]
            last_element.main_caption = everyone_else.name
            last_element._active = True
            last_element.r_min = 0
            last_element.r_max = 1000
        else:
            pass
    #
    topic.wrap_scenario(new_question)    

def scenario_2(topic):
    """


    scenario_2(topic) -> None


    **closing scenario**

    Scenario concludes with wrap_topic()

    Function pulls out user response for each team's bonus, records the
    response in work_space, and then passes it on to apply_data() for
    processing.
    """
    model = topic.MR.activeModel
    portal_question = topic.MR.activeQuestion
    input_array = portal_question["input_array"]
    portal_response = topic.MR.activeResponse
    #
    bonus_by_role = dict()
    #
    for i in range(len(input_array)):
        role = input_array[i]["main_caption"]
        raw_bonus = portal_response[i]["response"]
        #raw_bonus is a list of one decimal
        bonus = float(raw_bonus[0])
        bonus_by_role[role] = bonus
    #
    model.interview.work_space["employee_bonus_percent_by_role"] = bonus_by_role
    apply_data(topic, bonus_by_role)
    topic.wrap_topic()

def end_scenario(topic):
    """


    end_scenario(topic) -> None


    **end scenario**

    Scenario concludes with force_exit().
    
    Function applies standard bonus data to model. 
    """
    standard_data = SK.software.bonus_by_role
    #should pick out applicable data by industry and size
    #
    topic.apply_data(topic, standard_data)

def apply_data(topic, datapoint):
    """


    apply_data(topic, datapoint) -> None


    ``datapoint`` is annual cash bonus per team as a percentage of salary.

    Function adds lines and drivers to each personnel unit that track a monthly
    bonus accrual based on the team-specific structure.

    Function sets all teams that did not get specific data from the user to the
    catch-call "everyone else" bonus.
    """
    #Step 1. Unpack each of the objects used here as parts
    #(ordered from largest to smallest)
    model = topic.MR.activeModel
    current_period = model.time_line.current_period
    #1.1. business units
    company = current_period.content
    hq_bbid = company.components.by_name["headquarters"]
    hq = company.components[hq_bbid]
    personnel_bbid = hq.components.by_name["personnel"]
    personnel = hq.components[personnel_bbid]
    all_teams = personnel.components
    staff_template_unit = model.taxonomy["team"]["standard"]
    #1.2. drivers
    dr_average_bonus = topic.applied_drivers["average bonus"]
    dr_team_bonus = topic.applied_drivers["team bonus"]
    #1.3. formulas
    f_multiplier = topic.formulas["set line based on source value and multiplier."]
    f_fixed = topic.formulas["set line to fixed monthly value."]
    #1.4. lines
    l_average_bonus = LineItem("annual cash bonus (% of salary)")
    l_bonus = LineItem("bonus")
    #
    l_team_bonus = LineItem("cash bonus (team)")
    l_team_bonus.tag("accrual")
    l_team_bonus.tag("reserve cash")
    l_team_bonus.tag("year-end")
    l_team_bonus.tag("paid annually")
    l_team_bonus.tag("ratable")
    #
    dr_average_bonus.setWorkConditions(l_average_bonus.name)
    #1.5. labels
    team_label_template = "cash bonus reserved (%s)"
    #1.6. data
    ##    shared_data = dict()
    generic_bonus = datapoint.get("everyone else")
    if not generic_bonus:
        generic_bonus = datapoint.get("other")
    #1.7. adjust objects to fit each other
    #n/a
    materials = dict()
    materials["team_label_template"] = team_label_template
    materials["l_average_bonus"] = l_average_bonus
    materials["l_bonus"] = l_bonus
    materials["l_team_bonus"] = l_team_bonus
    materials["dr_average_bonus"] = dr_average_bonus
    materials["dr_team_bonus"] = dr_team_bonus
    materials["f_multiplier"] = f_multiplier
    materials["f_fixed"] = f_fixed
    
    #Step 2. Populate model with new information
    #2.1. Update each team with their specific bonus
    for (team_name, team_bonus_percent) in datapoint.items():
        team_bbid = all_teams.by_name[team_name]
        team = all_teams[team_bbid]
        #
        #delegate repetitive work to unit_work()
        unit_work(team, team_bonus_percent, **materials)
        #
    #2.2. Update remaining teams with the generic bonus
    unspecified_team_names = set(all_teams.by_name.keys()) - set(datapoint.keys())
    for team_name in unspecified_team_names:
        team_bbid = all_teams.by_name[team_name]
        team = all_teams[team_bbid]
        #
        #delegate repetitive work to unit_work()
        unit_work(team, generic_bonus, **materials)
        #
        #custom tags
        team.tag("generic bonus")
        team.tag("estimated bonus")
    #2.3. Update staff unit template with generic bonus:
    unit_work(staff_template_unit, generic_bonus, **materials)

    #Step 3. Prepare model for further processing
    #3.1. Add tags to model
    #n/a
    #3.2. Update path if necessary
    #n/a
    #
    #THE END
    
    
def unit_work(team,
              team_bonus_percent,
              team_label_template,
              #
              l_average_bonus,
              l_bonus,
              l_team_bonus,
              #
              dr_average_bonus,
              dr_team_bonus,
              #
              f_fixed,
              f_multiplier):
    """


    unit_work(team, team_salary) -> None


    Function manages repetitive work. Here, unit_work() adds bonus-related
    lines and drivers to each team unit. 
    """
    #
    team_label = team_label_template % team.name
    #
    overview_data = dict()
    overview_data["fixed_monthly_value"] = team_bonus_percent
    #
    team_data = dict()
    team_data["source_line_name"] = "salary (%s)" % team.name
    team_data["source_multiplier"] = team_bonus_percent / 100
    #
    #team-specific lines
    l_own_bonus = l_team_bonus.copy()
    l_own_bonus.setName(team_label)
    #
    #team-specific drivers
    dr_own_average = dr_average_bonus.copy()
    dr_own_average.configure(overview_data, f_fixed)
    #
    dr_own_bonus = dr_team_bonus.copy()
    dr_own_bonus.setWorkConditions(team_label)
    dr_own_bonus.configure(team_data, f_multiplier)
    #
    #add objects to team
    team.financials.add_line_to(l_average_bonus.copy(), "overview")
    team.financials.add_line_to(l_bonus.copy(),
                                "operating expense",
                                "employee expense")
    team.financials.add_line_to(l_own_bonus,
                                "operating expense",
                                "employee expense",
                                l_bonus.name)
    #
    team.addDriver(dr_own_average)
    team.addDriver(dr_own_bonus)
    #
    team.tag(tg_known_bonus)
    #
    
scenarios[None] = scenario_1
#
scenarios["annual cash bonus as percent of salary for open teams?"] = scenario_2
#
scenarios[Globals.user_stop] = end_scenario

