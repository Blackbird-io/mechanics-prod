#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: TW.Structure.Software.EmployeeCount_SoftwareTeams
"""

Topic asks about the number of employees across teams common to a software
company's organization. Topic then populates the model with business units
representative of those teams. 

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

from data_structures.modelling.business_unit import BusinessUnit




#globals
topic_content = True
name = "employee head count for a software company"
topic_author = "Ilya Podolyako"
date_created = "2015-06-12"
extra_prep = False

#store tags this topic uses multiple times in variables to avoid typos
tg_critical = "critical user input"
tg_expands_taxonomy = "expands taxonomy"
tg_single_product = "describes resources associated with one product"
tg_static_count = "head count stays constant over time"
tg_size_significant = "size value is significant"

#standard topic prep
user_outline_label = "Team composition"
requiredTags = ["software",
                "operating expense"]
optionalTags = [tg_critical,
                tg_single_product,
                "full time employees",
                "employee expense",
                "employee count",
                "teams",
                "employee head count",
                "personnel",
                "staffing",
                tg_static_count,
                tg_expands_taxonomy]

applied_drivers = dict()
formula_names = []
question_names = []
scenarios = dict()
work_plan = dict()

question_names = ["employee head count across software company roles?"]

work_plan["head count"] = 2
work_plan["employee expense"] = 1
work_plan["expenses"] = 1
work_plan["structure"] = 1
work_plan["staffing"] = 1

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

    Function asks user about employee head count across categories. The question
    comes pre-baked with teams that typically make up the bulk of a software
    organization's personnel. 
    """
    new_question = topic.questions["employee head count across software company roles?"]
    #how many employees do you have in each of the following categories? ------------------------------------------------------------------------------
    topic.wrap_scenario(new_question)    

def scenario_2(topic):
    """


    scenario_2(topic) -> None


    **closing scenario**

    Scenario concludes with wrap_topic()

    Function pulls out user response for head count across teams, records the
    response in work_space, and then passes the data on to apply_data() for
    processing. 
    """
    model = topic.MR.activeModel
    portal_question = topic.MR.activeQuestion
    input_array = portal_question["input_array"]
    portal_response = topic.MR.activeResponse
    #
    count_by_role = dict()
    #
    for i in range(len(input_array)):
        role = input_array[i]["main_caption"]
        raw_count = portal_response[i]["response"]
        #per api, raw_count (a number response) is a list of one decimal
        count = round(raw_count[0])
        #head count has to be an integer. round
        count_by_role[role] = count
    #
    model.interview.work_space["employee_count_by_role"] = count_by_role
    apply_data(topic, count_by_role)
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


    ``datapoint`` is monthly subscription cost in dollars. 

    Function creates a unit for each role in datapoint and sets that unit's
    size to the stipulated head count. Function then adds these team units to the
    main product unit's ``personnel`` container.

    Function defines a staff unit template that it then copies for each of the
    team units. Function adds the staff template to the model taxonomy.

    If the model taxonomy does not include a container template, function makes
    one from scratch and adds it in. 
    """
    model = topic.MR.activeModel
    current_period = model.time_line.current_period
    company = current_period.content
    #
    basic_template = model.taxonomy["standard"]
    #
    office_ids = current_period.ty_directory.get("office")
    #
    if office_ids:
        hq = current_period.get_units(office_ids)[0]
    else:
        #check if office template in place
        office_taxonomy = model.taxonomy.setdefault("office", dict())
        if office_taxonomy:
            office_template = office_taxonomy["standard"]
        else:
            #make an office template from scratch
            office_template = basic_template.copy()
            office_template.setName("office unit template")
            office_template.tag("office")
            office_template.type = "office"
            office_taxonomy["standard"] = office_template
        hq = office_template.copy()
        hq.setName("headquarters")
        company.addComponent(hq)
    #
    staff_unit = basic_template.copy()
    staff_unit.setName("Staff Template")
    staff_unit.type = "team"
    #tags:
    staff_unit.tag("staff unit")
    staff_unit.tag("personnel")
    staff_unit.tag("team")
    staff_unit.tag("cost center")
    staff_unit.tag("non-revenue generating")
    staff_unit.tag("size is head count for a particular team")
    team_taxonomy = model.taxonomy.setdefault("team", dict())
    team_taxonomy["standard"] = staff_unit
    #
    teams = basic_template.copy()
    teams.setName("personnel")
    hq.addComponent(teams)
    #
    for (role, head_count) in datapoint.items():
        if head_count:
            team = staff_unit.copy()
            team.setName(role)
            team.size = head_count
            teams.addComponent(team)
    #    
    model.tag("known team composition")
    
scenarios[None] = scenario_1
#
scenarios["employee head count across software company roles?"] = scenario_2
#
scenarios[Globals.user_stop] = end_scenario

