#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: TW.Financials.IS.OpEx.Labor.dev_spend_allocation
"""

Topic asks about the percent of total development spend the company allocates
to cost (versus R&D / SGA) for each product. 
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
name = "development expense allocation"
topic_author = "Ilya Podolyako"
date_created = "2015-06-16"
extra_prep = False

#store tags this topic uses multiple times in variables to avoid typos
tg_product_modification = "modifies product unit"

#standard topic prep
user_outline_label = "Cost"
requiredTags = ["employee expense",
                "known team composition"]

optionalTags = [tg_single_product,
                "commission",
                #
                #software ------------------------------------------------------------------------------------update tags
                "adjusts allocation of known value",
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

formula_names = ["set line based on source value and multiplier."] #<--------------------------------------------------

question_names = ["development allocation to product cost?"] #should only ask about a single product------------- tag accordingly
#get value, add line to cost in product, add offsetting entry to sga or wherever. 

work_plan["employee expense"] = 2 #<----------------------------------------------------- update
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
    new_question = topic.questions["development allocation to product cost?"]
    #always the same question; dont even both updating it for models
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
    percent_to_cost = topic.get_first_response()
    model.interview.work_space["dev_allocation_to_cost"] = percent_to_cost
    apply_data(topic, percent_to_cost)
    topic.wrap_topic()

def end_scenario(topic):
    """


    end_scenario(topic) -> None


    **end scenario**

    Scenario concludes with force_exit().
    
    Function applies standard bonus data to model. 
    """
    standard_data = SK.software.commissions #<-----------------------------------update
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
    ##for the product unit:
        #insert line "cost"
            #insert line "development allocation"
        #also insert a symmetric line into EE\Dev
            #"allocation to cost"
            #again, at the top level
            #negative value.
            #drivers are mirror images of each other
            #but distinct objects. point to the same formula.
        #EBITDA neutral
        #
        #insert 2 drivers that do the work
        #driver: look at employment expense in the "dev" team:
            #find the "dev" component
            #find the "total employee expense" line
            #apply the thing at the parent level
            #must be a negative number
        #requires new formula: multiply_component_line_value
            #data: component_name, target_line, multiplier
            
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

