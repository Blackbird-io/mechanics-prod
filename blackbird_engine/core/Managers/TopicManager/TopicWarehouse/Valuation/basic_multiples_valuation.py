#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: TW.Valuation.BasicMultiplesValuation
"""

Module defines content for a topic that performs basic enterprise value analysis
on a built-in model.

NOTE: Analytics topics should generally have only one scenario
Scenarios are keyed by question, and analytics topics generally won't have
questions. 

This topic is a one-size-fits-all analytics module that:

1) performs a very basic enteprise value calculation,
2) locates applicable market color, and
3) uses standard tools to build a name-specific credit landscape

The topic accomplishes task 1 by locating current monthly top-level EBITDA,
annualizing it, and multiplying it by a specific EV-to-EBITDA multiple. The
topic selects the multiple by locating a matching industry in market color.

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
prepare
scenario_1
scenario_2

CLASSES:
n/a
====================  ==========================================================
"""




#imports
import BBGlobalVariables as Globals

from DataStructures.Markets.company_value import CompanyValue
from DataStructures.Markets.CR_Scenario import CR_Scenario





#globals
topic_content = True
name = "Basic Multiples Valuation"
topic_author = "Ilya Podolyako"
date_created = "2015-04-11"
extra_prep = False
#if extra_prep = True, TopicManager will run this module's prep() function
#after completing standard prep

#standard topic prep
user_outline_label = "Enterprise Value Analysis - Internal"
requiredTags = []
optionalTags = ["Valuation",
                "Default",
                "Basic",
                "Retail"]
#
applied_drivers = dict()
formula_names = []
question_names = []
scenarios = dict()
work_plan = dict()

#formulas and questions intentionally left blank. topic does not use drivers.
#topic does not ask questions. 

work_plan["Enteprise Value"] = 1
work_plan["Analytics"] = 1
work_plan["Credit Capacity"] = 1
work_plan["Color"] = 1

#drivers: intentionally left blank

#scenarios
#
#define each scenario, then fill out scenarios dictionary at the bottom
#each scenario must conclude with either:
    #scenarios that ask a question - topic.wrap_scenario(Q)
    #scenarios that complete processing - topic.wrap_topic()
    #scenarios that respond to a user stop - topic.wrap_to_stop()

def scenario_1(topic):
    #1) Compute EV
    #For now, run on current period unless know otherwise
    M = topic.MR.activeModel
    ref_date = M.time_line.current_period.end
    market_conditions = topic.CM.get_color(ref_date)
    #
    topBU = M.currentPeriod.content
    topBU.fillOut()
    fins = topBU.financials
    atx = topBU.valuation
    if not atx:
        clean_atx = CompanyValue()
        topBU.setAnalytics(clean_atx)
        atx = topBU.valuation
    i_ebitda = fins.indexByName("EBITDA")
    line_ebitda = fins[i_ebitda]
    #line is monthly, multiply by 12 for simplicity, though could do day-by-day
    #annualization (or week-by-week)
    annual_ebitda = line_ebitda.value * 12
    #Part 1 pending
    #
    #2) Locate industry color
    #this topic theoretically runs for either retail or generic
    i_ovw = fins.indexByName("Overview")
    line_overview = fins[i_ovw]
    k = None
    if "retail" in line_overview.allTags:
        k = "retail"
    specColor = market_conditions[k]
    specCurve = specColor.price_curves["x_ebitda"]
    #Part 2 done
    #
    #finish up Part 1
    m = specColor.ev_x_ebitda
    ev = m * annual_ebitda 
    #Part 1 done
    #
    #3) Make a name-specific credit landscape
    #Use standard tools from Credit Capacity module
    sc1 = CR_Scenario()
    stdTerm = specColor.term
    sc1.changeElement("term",stdTerm)
    #build size landscape
    atx.credit.lev_loans.build_main(specCurve, annual_ebitda, sc1, store = True)
    #
    #trim the landscape boundaries to fit min/max sanity check
    debt_x_ebitda = specColor.debt_x_ebitda
    ltv_max = specColor.ltv_max
    cc_hi = min(ltv_max*ev, debt_x_ebitda*annual_ebitda)
    cc_hi = max(0, cc_hi)
    cc_hi = round(cc_hi,6)
    cc_lo = 2000000
    atx.credit.lev_loans.trim("size", lo_bound = cc_lo, hi_bound = cc_hi)
    #
    clean_size_landscape = atx.credit.lev_loans["size"]
    by_price = atx.credit.lev_loans.pivot([clean_size_landscape], store = True)
    atx.credit.lev_loans.label(surface = by_price)
    atx.credit.combine()
    #manually record work
    atx.credit.guide.quality.increment(2)
    atx.guide.quality.increment(2)
    #Part 3 done
    #
    topic.record_on_exit = False
    topic.wrap_topic()

scenarios[None] = scenario_1
scenarios[Globals.user_stop] = scenario_1
#
