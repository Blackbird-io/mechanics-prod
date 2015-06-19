#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: TW.Financials.IS.OpEx.Labor.stock_bonus_across_teams
"""

Topic asks about the annual equity bonus as a percentage of salary that teams
across the organization receive. Topic treats bonus as a ratable
expense throughout the year. 
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
name = "stock bonus percent across teams"
topic_author = "Ilya Podolyako"
date_created = "2015-06-15"
extra_prep = False

#store tags this topic uses multiple times in variables to avoid typos
tg_known_bonus = "known bonus structure"
tg_single_product = "describes resources associated with one product"
tg_balance_impact = "balance sheet impact"
tg_equity_impact = "equity impact"

#standard topic prep
user_outline_label = "Salaries"
requiredTags = ["employee expense",
                "known team composition"]

optionalTags = [tg_single_product,
                tg_balance_impact,
                tg_equity_impact,
                "adjust for inflation",
                "bonus",
                "dilutive",
                "equity bonus",
                "equity compensation", 
                "expenses",
                "full time employees",
                "incentive compensation",
                "industry-specific compensation scale",
                "recurring expense",
                "refines template",
                "salaries",
                "sensitive to equity price",
                "software",
                "stock bonus",
                "team-specific analysis",
                "variable teams"]

applied_drivers = dict()
formula_names = []
question_names = []
scenarios = dict()
work_plan = dict()

formula_names = ["set line based on source value and multiplier.",
                 "set line to fixed monthly value."]

question_names = ["annual stock bonus as percent of salary for open teams?"]

work_plan["employee expense"] = 2
work_plan["expenses"] = 1
work_plan["operations"] = 1
work_plan["bonuses"] = 1

#custom prep
def prepare(new_topic):
    #always return the topic
    return new_topic

#drivers:
topic.applied_drivers["team bonus"] = Driver()
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

    Function asks user about employee stock bonus across teams.

    Function populates the input elements for the question with the names of the
    largest teams (by  size) in the organization, excluding sales.

    If the organization has a catch-all team (``everyone else`` or ``other``),
    function pulls the team out and places it last in the input array. 
    """
    #
    q = "annual stock bonus as percent of salary for open teams?"
    new_question = topic.questions[q]
    #
    model = topic.MR.activeModel
    #
    product_unit = model.time_line.current_period.content
    personnel_bbid = product_unit.components.by_name["personnel"]
    personnel_unit = product_unit.components[teams_bbid]
    teams = personnel_unit.components.copy()
    #filter out sales team
    sales_bbid = teams.by_name.get("sales")
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
                                  operator.attrgetter("size"),
                                  reverse = True)
    #
    #configure question w existing roles:
    input_array = new_question["input_array"]
    #
    ask_about = len(input_array)
    if everyone_else:
        ask_about = len(input_array[:-1])
        #save the last element for everyone_else
    ask_about = min(ask_about, len(team_large_to_small))
    #if there are fewer teams than element slots, limit accordingly
    #
    for i in range(ask_about):
        element = input_array[i]
        element["main_caption"] = team_large_to_small[i].name
        element["_active"] = True
        element["r_min"] = 0
        element["r_max"] = 1000
        #when topic gets this question object, elements 2-5 will be inactive.
    else:
        if everyone_else:
            last_element = input_array[ask_about]
            last_element["main_caption"] = everyone_else.name
            last_element["_active"] = True
            last_element["r_min"] = 0
            last_element["r_max"] = 1000
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
    for i in len(input_array):
        role = input_array[i]["main_caption"]
        bonus = portal_response[i]["response"]
        bonus_by_role[role] = bonus
    #
    model.interview.work_space["stock_bonus_by_team"] = bonus_by_role
    apply_data(topic, bonus_by_role)
    topic.wrap_topic()

def end_scenario(topic):
    """


    end_scenario(topic) -> None


    **end scenario**

    Scenario concludes with force_exit().
    
    Function applies standard bonus data to model. 
    """
    standard_data = SK.software.stock_bonus_by_team
    #should pick out applicable data by industry and size
    #
    topic.apply_data(topic, standard_data)

def apply_data(topic, datapoint):
    """


    apply_data(topic, datapoint) -> None


    ``datapoint`` is annual stock bonus per team as a percentage of salary.

    Function adds lines and drivers to each personnel unit that track a monthly
    bonus accrual based on the team-specific structure.

    Function sets all teams that did not get specific data from the user to the
    catch-call "everyone else" bonus.
    """
    #Step 1. Unpack each of the objects used here as parts
    #(ordered from largest to smallest)
    #1.0. model
    model = topic.MR.activeModel
    #1.1. business units
    product_unit = model.time_line.current_period.content
    personnel_bbid = product_unit.components.by_name["personnel"]
    personnel_unit = product_unit.components[teams_bbid]
    all_teams = personnel_unit.components
    staff_template_unit = model.taxonomy["personnel"]
    #1.2. drivers
    dr_average_bonus = Driver()
    dr_team_bonus = topic.applied_drivers["team bonus"]
    #1.3. formulas
    f_multiplier = topic.formulas["set line based on source value and multiplier."]
    f_fixed = topic.formulas["set line to fixed monthly value."]
    #1.4. lines
    l_average_bonus = LineItem("annual stock bonus (% of salary)")
    #
    l_team_bonus = LineItem("stock bonus (team)")
    l_team_bonus.tag("accrual")
    l_team_bonus.tag("non-cash")
    l_team_bonus.tag("year-end")
    l_team_bonus.tag("dilutive")
    l_team_bonus.tag("ratable")
    l_team_bonus.tag("add back")
    l_team_bonus.tag("sensitive to price of equity")
    #
    dr_average_bonus.setWorkConditions(l_average_bonus.name)
    #1.5. labels
    team_label_template = "stock bonus reserved (%s)"
    #1.6. data
    ##    shared_data = dict()
    generic_bonus = datapoint.get("everyone else")
    if not generic_salary:
        generic_bonus = datapoint.get("other")
    #1.7. adjust objects to fit each other
    #n/a
    
    #Step 2. Populate model with new information
    #2.1. Update each team with their specific bonus
    for (team_name, team_bonus_percent) in datapoint.items():
        team_bbid = all_teams.by_name[team_name]
        team = all_teams[team_bbid]
        #
        #delegate repetitive work to unit_work()
        unit_work(team, team_bonus_percent)
        #
    #2.2. Update remaining teams with the generic salary
    unspecified_team_names = set(all_teams.keys()) - set(datapoint.keys())
    for team_name in unspecified_team_names:
        team_bbid = all_teams.by_name[team_name]
        team = all_teams[team_bbid]
        #
        #delegate repetitive work to unit_work()
        unit_work(team, generic_bonus)
        #
        #custom tags
        team.tag("generic bonus")
        team.tag("estimated bonus")
    #2.3. Update staff unit template with generic salary:
    unit_work(staff_template_unit, generic_salary)

    #Step 3. Prepare model for further processing
    #3.1. Add tags to model
    #n/a
    #3.2. Update path if necessary
    #n/a
    #
    #THE END
    
    
def unit_work(team, team_bonus_percent):
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
    team.financials.add_line_to(l_own_bonus, "g&a", "employee expense", "bonus") 
    #
    team.addDriver(dr_own_average)
    team.addDriver(dr_own_bonus)
    #
    team.tag(tg_known_bonus)
    #
    
scenarios[None] = scenario_1
#
scenarios["annual stock bonus as percent of salary for open teams?"] = scenario_2
#
scenarios[Globals.user_stop] = end_scenario

