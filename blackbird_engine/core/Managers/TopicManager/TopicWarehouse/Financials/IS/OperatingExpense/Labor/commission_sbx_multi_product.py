#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: TW.Financials.IS.OpEx.Labor.commission_multi_product_sbx
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

from data_structures.modelling.driver import Driver
from data_structures.modelling.line_item import LineItem




#globals
topic_content = True
name = "variable commission across multiple products"
topic_author = "Ilya Podolyako"
date_created = "2015-06-15"
extra_prep = False

#store tags this topic uses multiple times in variables to avoid typos
tg_known_products = "known product names"
tg_multi_product = "multiple products"
tg_product_rev = "revenue from product sales"
tg_var_commission = "variable commission across products"
#
tg_biz_dev = "business development"
tg_f_sales = "function of product sales"
tg_cash_comp = "cash compensation"
tg_incentive_comp = "incentive compensation"
tg_industry_comp = "industry-specific compensation scale"
tg_known_commission = "known commission"
tg_product_modification = "modifies product unit"
tg_single_product = "describes resources associated with one product"
tg_variable_comp = "variable compensation"
#
tg_distorts_cf = "blackbird may distort cash flow"
tg_smooths_cf = "blackbird smooths out cash flow"
tg_chunky_cf = "chunky cash flow"

#standard topic prep
user_outline_label = "Commission"
requiredTags = ["employee expense",
                tg_multi_product,
                tg_known_products,
                tg_var_commission,
                "subscriptions"]

optionalTags = ["commission",
                "product",
                tg_product_rev,
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
                "team-specific analysis"]


applied_drivers = dict()
formula_names = []
question_names = []
scenarios = dict()
work_plan = dict()

formula_names = ["set line based on source value and multiplier.",
                 "set line to fixed monthly value."]

question_names = ["commission on subscription revenues for open products?"]

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
team_commission = Driver()
team_commission.setName("team commission driver")
applied_drivers["team commission"] = team_commission
#
avg_comx = Driver()
avg_comx.setName("average commission driver")
applied_drivers["average commission"] = avg_comx
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

    Function asks user about commission paid for top 5 products (by
    size). 
    """
    #
    q_name = "commission on subscription revenues for open products?"
    new_question = topic.questions[q_name]
    #
    model = topic.MR.activeModel
    #
    current_period = model.time_line.current_period
    product_bbids = current_period.ty_directory["product"]
    all_products = current_period.get_units(product_bbids)
    products = sorted(all_products,
                      key = operator.attrgetter("size"),
                      reverse = True)    
    #
    input_array = new_question.input_array
    ask_about = len(input_array)
    ask_about = min(ask_about, len(products))
    #if there are fewer products than element slots, limit accordingly
    for i in range(ask_about):
        element = input_array[i]
        element._active = True
        #when topic gets this question object, elements 2-5 will be
        #inactive.
        element.main_caption = products[i].name
        element.r_min = 0
        element.r_max = 0.50
        element.shadow = 0.05
    #
    topic.wrap_scenario(new_question)

def scenario_2(topic):
    """


    scenario_2(topic) -> None


    **closing scenario**

    Scenario concludes with wrap_topic()

    Function pulls out user response for the commission associated with each
    product, records the response in work_space, and then passes the data on to
    apply_data() for implementation.
    """
    model = topic.MR.activeModel
    portal_question = topic.MR.activeQuestion
    input_array = portal_question["input_array"]
    portal_response = topic.MR.activeResponse
    #
    commission_by_product = dict()
    #
    for i in range(len(input_array)):
        product_name = input_array[i]["main_caption"]
        raw_commission = portal_response[i]["response"]
        #raw_commission is a list of one decimal
        commission = float(raw_commission[0])
        commission_by_product[product_name] = commission
    #
    model.interview.work_space["commission_by_product"] = commission_by_product
    apply_data(topic, commission_by_product)
    topic.wrap_topic()

def end_scenario(topic):
    """


    end_scenario(topic) -> None


    **end scenario**

    Scenario concludes with force_exit().
    
    Function applies standard commission data to model. 
    """
    standard_data = knowledge_re_sales.commissions
    #should pick out applicable data by industry and size
    #
    topic.apply_data(topic, standard_data)

def apply_data(topic, datapoint):
    """


    apply_data(topic, datapoint) -> None


    ``datapoint`` is a number that shows commission (in percent) per product.
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
    #1.2. drivers
    dr_average_commission = topic.applied_drivers["average commission"]
    dr_team_commission = topic.applied_drivers["team commission"]
    #1.3. formulas
    f_multiplier = topic.formulas["set line based on source value and multiplier."]
    f_fixed = topic.formulas["set line to fixed monthly value."]
    #1.4. lines
    l_average_commission = LineItem("commission (% of product revenue)")
    l_commissions = LineItem("commissions")
    l_ee = LineItem("employee expense")
    l_product_commission = LineItem("commission (product)")
    l_product_commission.tag("accrual",
                          "ratable",
                          tg_chunky_cf,
                          tg_cash_comp,
                          tg_incentive_comp,
                          tg_variable_comp,
                          #
                          tg_distorts_cf,
                          tg_smooths_cf,
                          "year-end")
    #1.5. labels
    product_label_template = "commission (%s)"
    #1.6. data
    generic_commission = datapoint.get("other")
    if not generic_commission:
        generic_commission = sum(datapoint.values)/len(datapoint.values)
        #assume that generic commission is the unweighted mean of all others
    #1.7. adjust objects to fit each other
    dr_average_commission.setWorkConditions(l_average_commission.name)
    #
    materials = dict()
    materials["product_label_template"] = product_label_template
    materials["dr_average_commission"] = dr_average_commission
    materials["dr_team_commission"] = dr_team_commission
    materials["f_multiplier"] = f_multiplier
    materials["f_fixed"] = f_fixed
    materials["l_average_commission"] = l_average_commission
    materials["l_commissions"] = l_commissions
    materials["l_ee"] = l_ee
    materials["l_product_commission"] = l_product_commission
    
    
    #Step 2. Populate model with new information
    #2.1. Update each product with its specific commission
    updated_product_bbids = set()
    for (product_name, product_commission) in datapoint.items():
        product_bbid = company.components.by_name.get(product_name)
        if product_bbid:
            product = company.components[product_bbid]
            unit_work(product, product_commission, **materials)
            updated_product_bbids.add(product_bbid)
        else:
            continue
    #
    all_product_bbids = current_period.ty_directory["product"]
    remaining_product_bbids = all_product_bbids - updated_product_bbids
    for bbid in remaining_product_bbids:
        product = company.components[bbid]
        unit_work(product, generic_commission, **materials)
    #
    unit_work(product_template_unit, generic_commission, **materials)
    #Step 3. Prepare model for further processing
    #3.1. Add tags to model
    #n/a
    #3.2. Update path if necessary
    #n/a
    #
    #THE END
    
    
def unit_work(product,
              commission,
              product_label_template,
              #
              l_average_commission,
              l_commission,
              l_ee,
              l_product_commission,
              #
              dr_average_commission,
              dr_product_commission,
              #
              f_fixed,
              f_multiplier):
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
    overview_data = dict()
    overview_data["fixed_monthly_value"] = commission
    #
    product_data = dict()
    product_data["source_line_name"] = "subscriptions"
    product_data["source_multiplier"] = commission
    #
    #team-specific lines
    l_own_commission = l_product_commission.copy()
    l_own_commission.setName(product_label)
    #
    #team-specific drivers
    dr_own_average = dr_average_commission.copy()
    dr_own_average.configure(overview_data, f_fixed)
    #
    dr_own_commission = dr_product_commission.copy()
    dr_own_commission.setWorkConditions(product_label)
    dr_own_commission.configure(product_data, f_multiplier)
    #
    #add lines to product financials
    product.financials.add_line_to(l_average_commission.copy(), "overview")
    if l_ee.name not in product.financials.dNames:
        product.financials.add_line_to(l_ee.copy(),
                                       "operating expense")
    if l_commissions.name not in product.financials.dNames:
        product.financials.add_line_to(l_commissions.copy(),
                                       "operating expense",
                                       l_ee.name)
    product.financials.add_line_to(l_own_commission.copy(),
                                   l_commissions.name)
    #
    #add drivers
    product.addDriver(dr_own_commission)
    product.addDriver(dr_own_average)
    #
    #add tags
    product.tag(tg_known_commission,
                tg_distorts_cf,
                tg_smooths_cf)
    #
    
scenarios[None] = scenario_1
#
scenarios["commission on subscription revenues for open products?"] = scenario_2
#
scenarios[Globals.user_stop] = end_scenario

