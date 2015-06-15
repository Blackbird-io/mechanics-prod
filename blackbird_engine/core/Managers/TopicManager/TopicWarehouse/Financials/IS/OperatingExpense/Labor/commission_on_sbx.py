#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: TW.Financials.IS.OpEx.Labor.commission_on_sbx
"""

Topic asks about commissions that the company pays out from product subscriptions.
Topic treats the commission as a ratable expense throughout the year (assumes
that company moves cash into a reserve account as appropriate). 
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

from DataStructures.Modelling.Driver import Driver
from DataStructures.Modelling.LineItem import LineItem




#globals
topic_content = True
name = "commission on product subscriptions"
topic_author = "Ilya Podolyako"
date_created = "2015-06-15"
extra_prep = False

#store tags this topic uses multiple times in variables to avoid typos
tg_single_product = "describes resources associated with one product"
tg_sales_team = "describes sales team"
tg_f_sales = "function of product sales"
tg_product_modification = "modifies product unit"
tg_biz_dev = "business development"

#standard topic prep
user_outline_label = "Commission"
requiredTags = ["employee expense",
                "known team composition"]

optionalTags = [tg_single_product,
                "commission",
                #
                "all current",
                "assumes simple comission structure",
                "assumes current pay",
                "assumes no deferred elements",
                "assumes no clawback",
                #
                "bonus",
                "expenses",
                "incentive compensation",
                "industry-specific compensation scale",
                #
                "may distort cash flow",
                "no deferred",
                #
                "percent of revenue",
                "percent of product sales",
                "performance-based",
                "points",
                "recurring expense",
                "refines template",
                "sales team in place",
                #                
                "selling",
                "selling expense",
                "selling, general & administrative",
                "sg&a",
                #
                "smooths cash flow",
                "smoothing assumptions",
                #
                "software",
                "team-specific analysis"]

applied_drivers = dict()
formula_names = []
question_names = []
scenarios = dict()
work_plan = dict()

formula_names = ["set line based on source value and multiplier."]

question_names = ["commission on subscription revenues for open teams?"]

work_plan["employee expense"] = 2
work_plan["expenses"] = 1
work_plan["operations"] = 1
work_plan["bonuses"] = 1
work_plan["commission"] = 1
work_plan["product"] = 1

#custom prep
def prepare(new_topic):
    #always return the topic
    return new_topic

#drivers:
topic.applied_drivers["team commission"] = Driver()
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
    **dual mode**

    Scenario concludes with wrap_scenario(question) OR wrap_topic().

    Function checks if the model includes sales teams that would be likely to
    earn commission.

    If the top product includes sales teams, function asks user about their
    commission take.

    If top product does not include any sales teams, function wraps topic. 
    """
    #
    new_question = topic.questions["sales team commission?"]
    #<------------------------------------------------------------ in percent of product revenue
    #
    model = topic.MR.activeModel
    #
    product_unit = model.time_line.current_period.content
    personnel_bbid = product_unit.components.by_name["personnel"]
    personnel_unit = product_unit.components[teams_bbid]
    teams = personnel_unit.components.copy()
    sales_team_names = {"sales",
                        "bizdev",
                        "business development",
                        "development",
                        "forward-deployed",
                        "forward-deployed engineers",
                        "inside sales",
                        "outside sales",
                        "inside",
                        "outside",
                        "sales and marketing",
                        "sales & marketing",
                        "marketing"}
    sales_names_in_place = sales_team_names & set(teams.by_name.keys())
    #
    #in multiproduct version, run against bu_types keys.
    #could potentially run review on team tags.
    #
    sales_teams_in_place = dict()
    for sales_name in sales_names_in_place:
        team_bbid = teams.by_name[sales_name]
        team = teams[team_bbid]
        #
        team.tag(tg_biz_dev)
        #tag the team for future reference
        #
        sales_teams_in_place[team_bbid] = team
        
    #
    if not sales_teams_in_place:
        model.tag("no sales teams")
        #
        topic.wrap_topic()
    else:
        sales_teams_ordered = sorted(sales_team_in_place.values(),
                                     operator.attrgetter("size"),
                                     reverse = True) 
        input_array = new_question["input_array"]
        ask_about = len(input_array)
        ask_about = min(ask_about, len(sales_teams_ordered))
        #if there are fewer teams than element slots, limit accordingly
        for i in range(ask_about):
            element = input_array[i]
            element["_active"] = True
            #when topic gets this question object, elements 2-5 will be
            #inactive.
            element["main_caption"] = sales_teams_ordered[i].name
            element["r_min"] = 0
            element["r_max"] = 100
            element["shadow"] = 0
        #
        topic.wrap_scenario(new_question)

def scenario_2(topic):
    """


    scenario_2(topic) -> None


    **closing scenario**

    Scenario concludes with wrap_topic()

    Function pulls out user response for each team's commmission, records the
    response in work_space, and then passes it on to apply_data() for
    processing.
    """
    model = topic.MR.activeModel
    portal_question = topic.MR.activeQuestion
    input_array = portal_question["input_array"]
    portal_response = topic.MR.activeResponse
    #
    commission_by_role = dict()
    #
    for i in len(input_array):
        role = input_array[i]["main_caption"]
        commission = portal_response[i]["response"]
        commission_by_role[role] = commission
    #
    model.interview.work_space["commission_by_team"] = commission_by_role
    apply_data(topic, commission_by_role)
    topic.wrap_topic()

def end_scenario(topic):
    """


    end_scenario(topic) -> None


    **end scenario**

    Scenario concludes with force_exit().
    
    Function applies standard bonus data to model. 
    """
    standard_data = SK.software.commissions
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
    #
    personnel_bbid = product_unit.components.by_name["personnel"]
    personnel_unit = product_unit.components[teams_bbid]
    all_teams = personnel_unit.components
    staff_template_unit = model.taxonomy["personnel"]
    product_template_unit = model.taxonomy["product"]
    #1.2. drivers
    dr_average_commission = Driver()
    dr_team_commission = topic.applied_drivers["team commission"]
    #1.3. formulas
    f_multiplier = topic.formulas["set line based on source value and multiplier."]
    f_fixed = topic.formulas["set line to fixed monthly value."]
    #1.4. lines
    l_average_commission = LineItem("commission (% of product revenue)")
    #
    l_team_commission = LineItem("commission (team)")
    l_team_commission.tag("accrual")
    l_team_commission.tag("year-end")
    #<-------------------------------------------------------tag("distorts cash timing"; "smooths out cash disbursements")
    l_team_commission.tag("ratable")
    #

    #1.5. labels
    team_label_template = "commission (%s team)"
    #1.6. data
    #assumes commission only for enumerated teams #<------------------------------------------ tag accordingly
    #1.7. adjust objects to fit each other
    dr_average_commission.setWorkConditions(l_average_commission.name)
    
    #Step 2. Populate model with new information
    #2.1. Update each team with their specific commission
    for (team_name, team_commission) in datapoint.items():
        team_bbid = all_teams.by_name[team_name]
        team = all_teams[team_bbid]
        #
        #delegate repetitive work to unit_work()
        unit_work(team, team_commission)
        #

    #Step 3. Prepare model for further processing
    #3.1. Add tags to model
    #n/a
    #3.2. Update path if necessary
    #n/a
    #
    #THE END
    
    
def unit_work(team, team_commission):
    """


    unit_work(team, team_salary) -> None


    Function manages repetitive work. Here, unit_work() adds bonus-related
    lines and drivers to each team unit. 
    """
    #
    team_label = team_label_template % team.name
    #
    overview_data = dict()
    overview_data["fixed_monthly_value"] = team_commission
    #
    team_data = dict()
    team_data["source_line_name"] = "subscriptions"
    team_data["source_multiplier"] = team_commission / 100
    #
    #team-specific lines
    l_own_commission = l_team_commission.copy()
    l_own_commission.setName(team_label)
    #
    #team-specific drivers
    dr_own_average = dr_average_commission.copy()
    dr_own_average.configure(overview_data, f_fixed)
    #
    dr_own_commission = dr_team_commission.copy()
    dr_own_commission.setWorkConditions(team_label)
    dr_own_commission.configure(team_data, f_multiplier)
    #
    #add the overview line and driver to team
    team.financials.add_line_to(l_average_commission.copy(), "overview")
    team.addDriver(dr_own_average)
    #
    #add a line and a driver for the team's commission to the product unit;
    #add the same to the product template, so commission drivers and lines are
    #built in
    for unit in [product_unit, product_template_unit]:
        unit.financials.add_line_to(l_own_commission, "employee expense")    
        unit.addDriver(dr_own_commission)
        unit.tag(tg_known_commission)
    #
    if "generic bonus" in team.allTags:
        team.remove_drivers(generic_bonus_cash)
        team.remove_drivers(generic_bonus_stock)
        #or remove lines from fins.
        team.restFinancials()
        
    team.tag(tg_known_commission)
    #
    
scenarios[None] = scenario_1
#
scenarios["commission on subscription revenues for open teams?"] = scenario_2
#
scenarios[Globals.user_stop] = end_scenario

