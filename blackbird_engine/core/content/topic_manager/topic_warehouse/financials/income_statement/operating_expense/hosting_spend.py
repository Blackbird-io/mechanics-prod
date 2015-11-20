#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: TW.Financials.IS.OpEx.Labor.hosting_spend
"""

Topic asks about the company's monthly hosting spend. 
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

from data_structures.modelling.driver import Driver
from data_structures.modelling.line_item import LineItem




#globals
topic_content = True
name = "monthly hosting spend"
topic_author = "Ilya Podolyako"
date_created = "2015-06-29"
extra_prep = False

#store tags this topic uses multiple times in variables to avoid typos
tg_product_rev = "revenue from product sales"

#standard topic prep
user_outline_label = "Hosting"
requiredTags = ["internet"]

optionalTags = ["product",
                "web",
                "software",
                "e-commerce",
                "saas",
                "software-as-a-service",
                "SaaS",
                "software as a service",
                "hosting",
                "internet",
                "online",
                "utilities",
                "core infrastructure",
                "core services",
                "critical services",
                "critical infrastructure",
                #
                "web-based",
                "web app",
                #
                "cost",
                "company",
                "company-level",
                "expense",
                "top-level",
                "technical expense",
                "r&d",
                "research & development",
                "research and development",
                "recurring expense",
                #
                "operating expense",
                "selling, general & administrative",
                "sg&a"]


applied_drivers = dict()
formula_names = []
question_names = []
scenarios = dict()
work_plan = dict()

formula_names = ["inflation-adjusted monthly value."]

question_names = ["monthly hosting spend for whole company?"]

work_plan["expense"] = 1
work_plan["operating expense"] = 1
work_plan["product"] = 1
work_plan["cost"] = 1
work_plan["hosting"] = 1
work_plan["sg&a"] = 1
work_plan["utilities"] = 1

#custom prep
def prepare(new_topic):
    #always return the topic
    return new_topic

#drivers:
dr_host = Driver()
dr_host.setName("hosting spend driver")
applied_drivers["hosting spend"] = dr_host
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
    q_name = "monthly hosting spend for whole company?"
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
    hosting_spend = topic.get_first_answer()
    hosting_spend = float(hosting_spend)
    work_space = model.interview.work_space
    work_space["monthly_hosting_spend"] = hosting_spend
    apply_data(topic, hosting_spend)
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


    ``datapoint`` is monthly hosting spend, in dollars.

    Function adds hosting line and driver to the top-level (company) unit. 
    """
    #Step 1. Unpack each of the objects used here as parts
    #(ordered from largest to smallest)
    #1.0. model
    model = topic.MR.activeModel
    current_period = model.time_line.current_period
    market_conditions = topic.CM.get_color(current_period.end)
    #1.1. business units
    company = current_period.content
    #1.2. drivers
    dr_host = topic.applied_drivers["hosting spend"]
    dr_host = dr_host.copy()
    #1.3. formulas
    f_monthly = topic.formulas["inflation-adjusted monthly value."]
    #1.4. lines
    l_host = LineItem("hosting")
    l_host.tag("accrual")
    #1.5. labels
    #n/a
    #1.6. data
    data = dict()
    data["ref_year"] = company.life.ref_date.year
    data["annual_inflation"] = market_conditions.inflation.annual
    data["base_monthly_value"] = datapoint
    #1.7. adjust objects to fit each other
    dr_host.setWorkConditions(l_host.name)
    dr_host.configure(data, f_monthly)
    
    #Step 2. Populate model with new information
    company.financials.income.add_line_to(l_host, "operating expense")
    company.addDriver(dr_host)
    
    #Step 3. Prepare model for further processing
    #3.1. Add tags to model
    #n/a
    #3.2. Update path if necessary
    #n/a

    #THE END
    
scenarios[None] = scenario_1
#
scenarios["monthly hosting spend for whole company?"] = scenario_2
#
scenarios[Globals.user_stop] = end_scenario

