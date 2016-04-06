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
from data_structures.modelling.driver import Driver
from data_structures.modelling.line_item import LineItem

from tools import for_messages as message_tools




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
                "team-specific analysis"]


applied_drivers = dict()
formula_names = []
question_names = []
scenarios = dict()
work_plan = dict()

formula_names = ["set line based on source value and multiplier.",
                 "set line to fixed monthly value."]

question_names = ["net subscription revenues after commission?"]

work_plan["bonuses"] = 1
work_plan["commission"] = 1
work_plan["employee expense"] = 1
work_plan["expense"] = 1
work_plan["operating expense"] = 1
work_plan["product"] = 1

#custom prep
def prepare(new_topic):
    #always return the topic
    return new_topic

#drivers:
product_commission = Driver()
product_commission.setName("product commission driver")
applied_drivers["product commission"] = product_commission
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

    Function asks user about commission paid on subscriptions. 
    """
    #
    q_name = "net subscription revenues after commission?"
    new_question = topic.questions[q_name]
    #
    topic.wrap_scenario(new_question)

def scenario_2(topic):
    """


    scenario_2(topic) -> None


    **closing scenario**

    Scenario concludes with wrap_topic()

    Function pulls out user's response about standard commission, records the
    response in work_space, and then passes the data on to apply_data() for
    implementation.
    """
    model = topic.MR.activeModel
    net_revenue = topic.get_first_answer()
    net_revenue = float(net_revenue)
    commission = 1 - net_revenue
    model.interview.work_space["commission_on_subscriptions"] = commission
    apply_data(topic, commission)
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


    ``datapoint`` is standard commission on subscription revenues, in percent.
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
    dr_average_commission = topic.applied_drivers["average commission"]
    dr_product_commission = topic.applied_drivers["product commission"]
    #1.3. formulas
    f_multiplier = topic.formulas["set line based on source value and multiplier."]
    f_fixed = topic.formulas["set line to fixed monthly value."]
    #1.4. lines
    l_average_commission = LineItem("commission (% of product revenue)")
    l_commissions = LineItem("commission")
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
    standard_commission = datapoint
    #1.7. adjust objects to fit each other
    dr_average_commission.setWorkConditions(l_average_commission.name)
    #
    materials = dict()
    materials["product_label_template"] = product_label_template
    materials["dr_average_commission"] = dr_average_commission
    materials["dr_product_commission"] = dr_product_commission
    materials["f_multiplier"] = f_multiplier
    materials["f_fixed"] = f_fixed
    materials["l_average_commission"] = l_average_commission
    materials["l_commissions"] = l_commissions
    materials["l_ee"] = l_ee
    materials["l_product_commission"] = l_product_commission
    
    
    #Step 2. Populate model with new information
    for product in all_products:
        unit_work(product, standard_commission, **materials)
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
              l_commissions,
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
    overview = product.financials.overview
    income = product.financials.income
    
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
    #add lines to product financials:
    overview.add_top_line(l_average_commission.copy())
    income.add_line_to(l_ee.copy(), "operating expense")    
    income.add_line_to(l_commissions.copy(), "operating expense", l_ee.name)
    income.add_line_to(l_own_commission.copy(), l_commissions.name)
    
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
scenarios["net subscription revenues after commission?"] = scenario_2
#
scenarios[message_tools.USER_STOP] = end_scenario

