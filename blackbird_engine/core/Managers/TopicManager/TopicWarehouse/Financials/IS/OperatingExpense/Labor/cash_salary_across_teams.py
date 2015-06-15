#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: TW.Financials.IS.OpEx.Labor.cash_salary_across_teams
"""

Topic asks about the cash salary that members of various functional teams in an
organization earn. 

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

from Managers.TopicManager.TopicWarehouse.Structure import StandardFinancials
#standard financials should always be a direct import so that you can move topic
#from folder to folder in the warehouse.



#globals
topic_content = True
name = "cash salary across teams"
topic_author = "Ilya Podolyako"
date_created = "2015-06-12"
extra_prep = False

#store tags this topic uses multiple times in variables to avoid typos
tg_known_salaries = "known salaries"
tg_single_product = "describes resources associated with one product"

#standard topic prep
user_outline_label = "Salaries"
requiredTags = ["employee expense",
                "known team composition"]
optionalTags = [tg_single_product,
                "adjust for inflation",
                "cash compensation",
                "expenses",
                "full time employees",
                "refines template",
                "salaries", 
                "team-specific analysis",
                "variable teams"]

applied_drivers = dict()
formula_names = []
question_names = []
scenarios = dict()
work_plan = dict()

formula_names = ["inflation-adjusted monthly value multiplied by unit size.",
                 "inflation-adjusted annualized value multiplied by unit size."]

question_names = ["average annual salary across unspecified teams?"]

work_plan["employee expense"] = 2
work_plan["expenses"] = 1
work_plan["operations"] = 1
work_plan["salaries"] = 2

#custom prep
def prepare(new_topic):
    #always return the topic
    return new_topic

#drivers:
topic.applied_drivers["average salary"] = Driver()
topic.applied_drivers["team salary"] = Driver()
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

    Function asks user about employee salary across categories. Function
    populates the input elements for the question with the names of the largest
    teams (by  size) in the organization. If the organization has a catch-all
    team (``everyone else`` or ``other``), function pulls the team out and
    places it last in the input array. 
    """
    #
    new_question = topic.questions["average annual salary across unspecified teams?"]
    #
    model = topic.MR.activeModel
    #
    product_unit = model.time_line.current_period.content
    personnel_bbid = product_unit.components.by_name["personnel"]
    personnel_unit = product_unit.components[teams_bbid]
    teams = personnel_unit.components
    #
    #pull out the catch-all team to make sure its input element appears
    #last; otherwise, due to unstable dict key order, elements could read
    #"everyone else" []; "dev" []; ...
    #
    everyone_else = None
    everyone_else_bbid = teams.by_name.get("everyone else")
    #
    if not everyone_else_bbid:
        everyone_else_bbid = teams.by_name.get("other")
    if everyone_else_bbid:
        teams = teams.copy()
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
        #when topic gets this question object, elements 2-5 will be inactive.
    else:
        if everyone_else:
            last_element = input_array[ask_about]
            last_element["main_caption"] = everyone_else.name
            last_element["_active"] = True
        else:
            pass
    #
    topic.wrap_scenario(new_question)    

def scenario_2(topic):
    """


    scenario_2(topic) -> None


    **closing scenario**

    Scenario concludes with wrap_topic()

    Function pulls out user response for each team's salary, records the
    response in work_space, and then passes it on to apply_data() for processing.
    """
    model = topic.MR.activeModel
    portal_question = topic.MR.activeQuestion
    input_array = portal_question["input_array"]
    portal_response = topic.MR.activeResponse
    #
    salary_by_role = dict()
    #
    for i in len(input_array):
        role = input_array[i]["main_caption"]
        salary = portal_response[i]["response"]
        salary_by_role[role] = salary
    #
    model.interview.work_space["employee_salary_by_role"] = salary_by_role
    apply_data(topic, salary_by_role)
    topic.wrap_topic()

def end_scenario(topic):
    """


    end_scenario(topic) -> None


    **end scenario**

    Scenario concludes with force_exit().
    
    Function applies standard salary data to model. 
    """
    standard_data = SK.salaries_by_role
    topic.apply_data(topic, standard_data)

def apply_data(topic, datapoint):
    """


    apply_data(topic, datapoint) -> None


    ``datapoint`` is monthly subscription cost in dollars. 

    Function adds a ``subscriptions`` line to each subscriber unit in 
    c
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
    dr_average_salary = topic.applied_drivers["average salary"]
    dr_team_salary = topic.applied_drivers["team salary"]
    #1.3. formulas
    f_monthly = topic.formulas["inflation-adjusted monthly value multiplied by unit size."]
    f_annualized = topic.formulas["inflation-adjusted annualized value multiplied by unit size."]
    #1.4. lines
    l_average_salary = LineItem("average annual salary")
    l_employee_expense = LineItem("employee expense")
    l_salaries = LineItem("salaries")
    l_team_salaries = LineItem("salaries (team)")
    #1.5. labels
    team_label_template = "salaries (%s)"
    #1.6. data
    shared_data = dict()
    shared_data["ref_year"] = product_unit.life.ref_date.year
    shared_data["annual_inflation"] = Globals.annual_inflation
    generic_salary = datapoint.get("everyone else")
    if not generic_salary:
        generic_salary = datapoint.get("other")
    #1.7. adjust objects to fit each other
    dr_average_salary.setWorkConditions(l_average_salary.name)
    
    #Step 2. Populate model with new information
    #2.1. Update each team with their specific salary
    for (team_name, team_salary) in datapoint.items():
        #can wrap this whole thing in KeyError handler? --------------------------- for production
        team_bbid = all_teams.by_name[team_name]
        team = all_teams[team_bbid]
        #
        #delegate repetitive work to unit_work()
        unit_work(team, team_salary)
        #
    #2.2. Update remaining teams with the generic salary
    unspecified_team_names = set(all_teams.keys()) - set(datapoint.keys())
    for team_name in unspecified_team_names:
        team_bbid = all_teams.by_name[team_name]
        team = all_teams[team_bbid]
        #
        #delegate repetitive work to unit_work()
        unit_work(team, generic_salary)
        #
        #custom tags
        team.tag("generic salary")
        team.tag("assumed salary")
    #2.3. Update staff unit template with generic salary:
    unit_work(staff_template_unit, generic_salary)

    #Step 3. Prepare model for further processing
    #3.1. Add tags to model
    model.tag(tg_known_salaries)
    #3.2. Update path if necessary
    #n/a
    #
    #THE END
    
    
def unit_work(team, team_salary):
    """


    unit_work(team, team_salary) -> None


    Function manages repetitive work. Here, unit_work() adds salary-related
    lines and drivers to each team unit. 
    """
    #
    team_label = team_label_template % team.name
    #
    team_data = shared_data.copy()
    team_data["fixed_monthly_value"] = team_salary
    #
    #team-specific lines
    l_own_salaries = l_team_salaries.copy()
    l_own_salaries.setName(team_label)
    #
    #team-specific drivers
    dr_own_average = dr_average_salary.copy()
    dr_own_average.configure(team_data, f_annualized)
    #
    dr_own_salaries = dr_team_salary.copy()
    dr_own_salaries.setWorkConditions(team_label)
    dr_own_salaries.configure(team_data, f_monthly)    
    #
    #add objects to team
    team.financials.add_line_to(l_average_salary.copy(), "overview")
    team.financials.add_line_to(l_employee_expense.copy(), "g&a")
    team.financials.add_line_to(l_salaries.copy(), "g&a", "employee expense")
    team.financials.add_line_to(l_own_salaries, "g&a", "employee expense", "salaries") 
    #
    team.addDriver(dr_own_average)
    team.addDriver(dr_own_salaries)
    #
    team.tag(tg_known_salaries)
    #
    
scenarios[None] = scenario_1
#
scenarios["average annual salary across unspecified teams?"] = scenario_2
#
scenarios[Globals.user_stop] = end_scenario

