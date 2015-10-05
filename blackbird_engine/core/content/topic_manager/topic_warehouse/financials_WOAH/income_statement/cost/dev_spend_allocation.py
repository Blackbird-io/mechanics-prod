#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: TW.Financials.IS.cost.dev_spend_allocation
"""

Topic asks about the percent of development spend the company allocates
to product cost (versus SG&A/R&D). Topic adjusts model accordingly.
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
name = "development expense allocation to product cost"
topic_author = "Ilya Podolyako"
date_created = "2015-06-16"
extra_prep = False

#store tags this topic uses multiple times in variables to avoid typos
tg_product_modification = "modifies product unit"

#standard topic prep
user_outline_label = "Cost"
requiredTags = ["employee expense",
                "known employee expense",  #<------------------------- can remove this tag
                "software"]

optionalTags = ["cost",
                "commission",
                #
                "adjusts allocation of known value",
                "product cost",
                "income-neutral",
                "GAAP adjustment",
                "refines template",
                "sales team in place",
                "sg&a"]

applied_drivers = dict()
formula_names = []
question_names = []
scenarios = dict()
work_plan = dict()

formula_names = ["set line based on source value and multiplier.",
                 "product of line from named component."]

question_names = ["percent of development spend allocated to product cost?"] 

work_plan["employee expense"] = 1 
work_plan["cost"] = 1
work_plan["product"] = 1

#custom prep
def prepare(new_topic):
    #always return the topic
    return new_topic

#drivers:
#define driver shells to make sure they receive bbids and signatures
dr_cost = Driver()
dr_cost.setName("write portion of development expense to cost")
applied_drivers["allocate part of dev to cost"] = dr_cost
#
dr_dev = Driver()
dr_dev.setName("mirror allocation of development to cost")
applied_drivers["mirror dev cost allocation"] = dr_dev


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

    Function asks user about development cost allocation.

    This scenario performs a very limited amount of work: it pulls out the
    question object and sets it up for the user input.    
    """
    q_name = "percent of development spend allocated to product cost?"
    new_question = topic.questions[q_name]
    #
    #could check if product units include personnel. in multi-product version,
    #can plug in product names into the question's input_array.
    #
    topic.wrap_scenario(new_question)

def scenario_2(topic):
    """


    scenario_2(topic) -> None


    **closing scenario**

    Scenario concludes with wrap_topic()

    Function pulls out user's allocation policy, records it in work_space, and
    passes the data to apply_data() for processing.
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

    
    Function applies industry-standard allocation policy from Subject Knowledge
    to model. 
    """
    standard_data = SK.software["development expense allocation to product cost"]
    topic.apply_data(topic, standard_data)

def apply_data(topic, datapoint):
    """


    apply_data(topic, datapoint) -> None


    ``datapoint`` is annual stock bonus per team as a percentage of salary.

    [ ]
    Function adjusts product-level financials to allocate part of the
    development expense to cost. 
    
    When Blackbird fills out financials for a product unit, the product unit
    first picks up costs from daughter personnel units through consolidate().
    Product unit then runs derive() to compute its own lines.

    Product financials should therefore include the personnel-level development
    expense by the time the product unit starts to derive its own lines.
    
    """
    #Step 1. Unpack each of the objects used here as parts
    #(ordered from largest to smallest)
    #1.0. model
    model = topic.MR.activeModel
    #1.1. business units
    product_unit = model.time_line.current_period.content
    product_template = model.taxonomy.get("product")
    targets = [product_unit]
    if product_template:
        targets.append(product_template)
    #1.2. drivers
    dr_cost = topic.applied_drivers["allocate part of dev to cost"]
    dr_dev = topic.applied_drivers["mirror dev cost allocation"]
    #1.3. formulas
    f_multiplier = topic.formulas["set line based on source value and multiplier."]
    f_component = topic.formulas["product of line from named component."]
    #1.4. Lines
    cost = LineItem("cost")
    cost_adj = LineItem("development expense (allocation)")
    cost_adj.tag("development", field = "req")
    cost_adj.tag("adjustment",
                 "allocation",
                 "expense",
                 "expense allocation",
                 "GAAP differs from operating reality",
                 "personnel")
    dev_adj = cost_adj.copy()
    dev_adj.setName("allocation to product cost")
    dev_adj.tag("reduces development expense")
    #
    cost_adj.tag("increases product cost")
    #tag cost line after we make a copy; this tag does **not** go on dev
    #1.5. Configure objects
    dr_cost.setWorkConditions(cost_adj.name,
                              "cost")
    cost_adjustment_data = dict()
    cost_adjustment_data["component_name"] = "personnel"
    cost_adjustment_data["source_line_name"] = "total expense"
    cost_adjustment_data["source_multiplier"] = datapoint
    #
    dr_cost.configure(cost_adjustment_data,
                      f_multiplier)    
    #
    dr_dev.setWorkConditions(dev_adj.name,
                             None,
                             "development")
    dev_adjustment_data = dict()
    dev_adjustment_data["source_multiplier"] = -1
    dev_adjustment_data["source_line_name"] = "development expense (allocation)"
    #
    dr_dev.configure(dev_adjustment_data,
                     f_multiplier)
    
    #Step 2. Populate model with new information
    for product in targets:
        product.resetFinancials()
        fins = unit.financials
        fins.buildDictionaries()
        if cost.name not in fins.dNames:
            fins.add_top_line(cost.copy, after = "revenue")
        if cost_adj.name not in fins.dNames:
            fins.add_line_to(cost_adj.copy(), "cost")
        if dev_adj.name not in fins.dNames:
            fins.add_line_to(dev_adj.name(), "expense")
        unit.addDriver(dr_cost.copy())
        unit.addDriver(dr_dev.copy())

    #Step 3. Prepare model for further processing
    #3.1. Add tags to model
    #n/a
    #3.2. Update path if necessary
    #n/a
    #
    #THE END
        
scenarios[None] = scenario_1
#
scenarios["percent of development spend allocated to product cost?"] = scenario_2
#
scenarios[Globals.user_stop] = end_scenario

