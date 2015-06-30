#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: TW.Financials.IS.OpEx.Labor.office_expense_basic
"""

Topic asks about the company's monthly office expense. Topic then splits that
expense ratably between every office in the model. 
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
import MarketColor

from DataStructures.Modelling.Driver import Driver
from DataStructures.Modelling.LineItem import LineItem




#globals
topic_content = True
name = "basic office expense"
topic_author = "Ilya Podolyako"
date_created = "2015-06-29"
extra_prep = False

#store tags this topic uses multiple times in variables to avoid typos
tg_hc_intensive = "human-capital-intensive business",
tg_person_intensive = "personnel-intensive"
tg_service = "service-type business"

#standard topic prep
user_outline_label = "Office Expense"
requiredTags = ["operating expense"]
optionalTags = ["occupancy",
                "office",
                "headquarters",
                "common area maintenance",
                "CAM",
                "fully loaded",
                "expense location",
                "sensitive to location",
                tg_hc_intensive,
                tg_service,
                tg_person_intensive,
                #
                "utilities",
                "core infrastructure",
                "core services",
                "critical services",
                "critical infrastructure",
                "recurring expense",
                #
                "g&a",
                "general & administrative",
                "general and administrative",
                "selling, general & administrative",
                "sg&a"]


applied_drivers = dict()
formula_names = []
question_names = []
scenarios = dict()
work_plan = dict()

formula_names = ["fixed monthly value multiplied by unit size."]

question_names = ["monthly office expense for whole company?"]

work_plan["expense"] = 1
work_plan["operating expense"] = 1
work_plan["office"] = 1
work_plan["occupancy"] = 1
work_plan["occupancy expense"] = 1
work_plan["sg&a"] = 1

#custom prep
def prepare(new_topic):
    #always return the topic
    return new_topic

#drivers:
dr_occupancy = Driver()
dr_occupancy.setName("occupancy expense driver")
applied_drivers["occupancy"] = dr_occupancy
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

    Function asks user about monthly spend on hosting. 
    """
    #
    q_name = "monthly office expense for whole company?"
    new_question = topic.questions[q_name]
    #
    topic.wrap_scenario(new_question)

def scenario_2(topic):
    """


    scenario_2(topic) -> None


    **closing scenario**

    Scenario concludes with wrap_topic()

    Function pulls out user response for monthly hosting spend, records the
    response in work_space, and then passes the data on to apply_data() for
    implementation.
    """
    model = topic.MR.activeModel
    office_expense = float(topic.get_first_answer())
    #answer comes in as a decimal by default
    work_space = model.interview.work_space
    work_space["monthly_company_office_expense"] = office_expense
    apply_data(topic, office_expense)
    topic.wrap_topic()

def end_scenario(topic):
    """


    end_scenario(topic) -> None


    **end scenario**

    Scenario concludes with force_exit().
    
    Function applies standard hosting spend data to model. 
    """
    standard_data = knowledge_re_software.hosting_spend
    #should pick out applicable data by industry and size
    #
    topic.apply_data(topic, standard_data)
    topic.wrap_to_close()

def apply_data(topic, datapoint):
    """


    apply_data(topic, datapoint) -> None


    ``datapoint`` is monthly office expense, in dollars.

    Function computes total size of all known offices, then adds in drivers and
    lines into each office. Function uses a size-sensitive formula that creates
    a ratable allocation of the stated office expense between locations. 
    """
    #Step 1. Unpack each of the objects used here as parts
    #(ordered from largest to smallest)
    #1.0. model
    model = topic.MR.activeModel
    current_period = model.time_line.current_period
    #1.1. business units
    company = current_period.content
    office_ids = current_period.ty_directory.get("office")
    if office_ids:
        all_offices = current_period.get_units(office_ids)
    else:
        all_offices = [company]
    office_taxonomy = model.taxonomy.get("office")
    office_template = None
    if office_taxonomy:
        office_template = office_taxonomy["standard"]
    #1.2. drivers
    dr_occupancy = topic.applied_drivers["occupancy"]
    #1.3. formulas
    f_monthly = topic.formulas["fixed monthly value multiplied by unit size."]
    #1.4. lines
    l_occupancy = LineItem("occupancy")
    l_occupancy.tag("accrual")
    l_occupancy.tag("expense")
    l_occupancy.tag("ratable")
    l_occupancy.tag("adjusted for size")
    #1.5. labels
    #n/a
    #1.6. data
    office_sizes = [x.size for x in all_offices]
    if len(all_offices) == 1:
        total_size = 1
    else:
        total_size = sum(office_sizes)
    #
    data = dict()
    data["fixed_monthly_value"] = datapoint / total_size
    #1.7. adjust objects to fit each other
    dr_occupancy.setWorkConditions(l_occupancy.name)
    dr_occupancy.configure(data, f_monthly)
    
    #Step 2. Populate model with new information
    if office_template:
        all_offices.append(office_template)
    for office in all_offices:
        office.financials.add_line_to(l_occupancy.copy(), "operating expense")
        office.addDriver(dr_occupancy.copy())
        office.tag("size represents square footage",
                   "size represents relative area",
                   "occupancy expense adjusted to size")
    
    #Step 3. Prepare model for further processing
    #3.1. Add tags to model
    #n/a
    #3.2. Update path if necessary
    #n/a

    #THE END
    
scenarios[None] = scenario_1
#
scenarios["monthly office expense for whole company?"] = scenario_2
#
scenarios[Globals.user_stop] = end_scenario

