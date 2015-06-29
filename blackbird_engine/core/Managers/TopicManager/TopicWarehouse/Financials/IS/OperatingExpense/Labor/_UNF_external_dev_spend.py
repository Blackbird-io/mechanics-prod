#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: TW.Financials.IS.OpEx.Labor.commission_sbx
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
tg_product_rev = "revenue from product sales"
#
tg_f_sales = "function of product sales"
tg_cash_comp = "cash compensation"
tg_incentive_comp = "incentive compensation"
tg_industry_comp = "industry-specific compensation scale"
tg_known_commission = "known commission"
tg_product_modification = "modifies product unit"
tg_variable_comp = "variable compensation"
#
tg_distorts_cf = "blackbird may distort cash flow"
tg_smooths_cf = "blackbird smooths out cash flow"
tg_chunky_cf = "chunky cash flow"

#standard topic prep
user_outline_label = "Commission"
requiredTags = ["subscriptions",
                tg_product_rev]

optionalTags = ["commission",
                "product",
                "revenue from product sales",
                #
                "all current",
                "assumes simple comission structure",
                "assumes current pay",
                "assumes no deferred elements",
                "assumes no clawback",
                #
                "bonus",
                "cash bonus",
                "expense",
                "employee expense",
                "sales compensation",
                "sales incentives",
                "sales team",                
                tg_cash_comp,
                tg_incentive_comp,
                tg_industry_comp,
                tg_variable_comp,
                #
                tg_distorts_cf,
                "no deferred",
                #
                "percent of revenue",
                "percent of product sales",
                "performance-based",
                "points",
                "recurring expense",
                "refines template",
                #
                "operating expense",
                "selling",
                "selling expense",
                "selling, general & administrative",
                "sg&a",
                #
                "smooths cash flow",
                "smoothing assumptions",
                "software",
                "team-specific analysis"] #<--------------------- adjust tags. should be cost? or sg&a
#<----------------------------------------------------------------------------single product only


applied_drivers = dict()
formula_names = []
question_names = []
scenarios = dict()
work_plan = dict()

formula_names = ["inflation-adjusted monthly expense from known annual start."]

question_names = ["annual spend on development and design contractors?"]

work_plan["expense"] = 1
work_plan["operating expense"] = 1
work_plan["product"] = 1
work_plan["cost"] = 1

#custom prep
def prepare(new_topic):
    #always return the topic
    return new_topic

#drivers:
product_commission = Driver()
product_commission.setName("product commission driver")
applied_drivers["product commission"] = product_commission
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

    Function asks user about annual spend on development and design contractors. 
    """
    #
    q_name = "annual spend on development and design contractors?"
    new_question = topic.questions[q_name]
    #
    topic.wrap_scenario(new_question)

def scenario_2(topic):
    """


    scenario_2(topic) -> None


    **closing scenario**

    Scenario concludes with wrap_topic()

    Function pulls out user response for external development spend, records the
    response in work_space, and then passes the data on to apply_data() for
    implementation.
    """
    model = topic.MR.activeModel
    external_dev_spend = topic.get_first_answer()
    external_dev_spend = float(external_dev_spend)
    work_space = model.interview.work_space
    work_space["annual_external_development_spend"] = external_dev_spend
    apply_data(topic, external_dev_spend)
    topic.wrap_topic()

def end_scenario(topic):
    """


    end_scenario(topic) -> None


    **end scenario**

    Scenario concludes with force_exit().
    
    Function applies standard development spend data to model. 
    """
    standard_data = knowledge_re_software.dev_spend
    #should pick out applicable data by industry and size
    #
    topic.apply_data(topic, standard_data)

def apply_data(topic, datapoint):
    """


    apply_data(topic, datapoint) -> None


    ``datapoint`` is annual spend on external developers and designers, in
    dollars.
    """
    #Step 1. Unpack each of the objects used here as parts
    #(ordered from largest to smallest)
    #1.0. model
    model = topic.MR.activeModel
    current_period = model.time_line.current_period
    #1.1. business units
    company = current_period.content
    product_ids = current_period.ty_directory["product"]
    all_products = current_period.get_units(product_ids)
    product_template_unit = model.taxonomy["product"]["standard"]
    all_products.append(product_template_unit)
    #1.2. drivers
    dr_dev_spend = topic.applied_drivers["dev spend"]
    #1.3. formulas
    f_monthly = topic.formulas["set line to inflation-adjusted monthly value."]
    #1.4. lines
    l_average_commission = LineItem("commission (% of product revenue)")
##    l_commissions = LineItem("commission")
##    l_ee = LineItem("employee expense")
    l_product_commission = LineItem("external development")
    l_product_commission.tag("accrual",
                          "ratable",
                          "critical expense",
                          "year-end")
    #1.5. labels
    product_label_template = "external development(%s)"
    #1.6. data
    shared_data = dict()
    shared_data["ref_year"] = company.life.ref_date.year
    shared_data["annual_inflation"] = MarketColor.annualInflation
    annual_spend = datapoint
    #1.7. adjust objects to fit each other
    #
    materials = dict()
    materials["product_label_template"] = product_label_template
    materials["dr_dev_spend"] = dr_dev_spend
    materials["f_monthly"] = f_monthly
    materials["l_average_commission"] = l_average_commission
    
    
    #Step 2. Populate model with new information
    for product in all_products:
        unit_work(product, annual_spend, **materials)
    #Step 3. Prepare model for further processing
    #3.1. Add tags to model
    #n/a
    #3.2. Update path if necessary
    #n/a
    #
    #THE END
    
    
def unit_work(product,
              annual_spend,
              product_label_template,
              #
              shared_data,
              #
              l_dev,
              #
              dr_dev,
              #
              f_monthly):
    """


    unit_work(product,
              commission,
              product_label_template,
              l_average_commission,
              l_commission,
              l_ee,
              l_product_commission,
              dr_average_commission,
              dr_product_commission,
              f_fixed,
              f_multiplier) -> None 


    Function manages repetitive work.

    Function inserts a commission rate line into overview and a product.
    Function also inserts lines necessary to create the following tree:
      -operating expense
       -employee expense
        -commission
         -commission ([product name])

    Function then inserts drivers that fill out the rate and product commission.
    """
    #
    product.financials.buildDictionaries()
    product_label = product_label_template % product.name
    #
    product_data = shared_data.copy()
    #
    #team-specific lines
    l_own_dev = l_dev.copy()
    l_own_dev.setName(product_label)
    #
    #team-specific drivers
    dr_own_dev = dr_dev.copy()
    dr_own_dev.setWorkConditions(product_label)
    dr_own_dev.configure(product_data, f_monthly)
    #
    #add lines to product financials
    product.financials.add_line_to(l_own_dev.copy(),
                                   "operating expense")
    #
    #add drivers
    product.addDriver(dr_own_dev)
    #
    #add tags
    product.tag(tg_known_commission,
                tg_distorts_cf,
                tg_smooths_cf) #<---------------------------------------------------------------------------fix these tags
                #may be i should put these into the company and not the product?
    #
    
scenarios[None] = scenario_1
#
scenarios["annual spend on development and design contractors?"] = scenario_2
#
scenarios[Globals.user_stop] = end_scenario

