#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: Managers.TopicManager.TopicWarehouse.TopicTemplate
"""

Fins_retail topic

====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
applied_drivers
author
date
extra_prep
formula_names
name
optionalTags
question_names
requiredTags
scenarios
topic_content

FUNCTIONS:
scenario_1            make lines, insert into top fins, set interview path

CLASSES:
n/a
====================  ==========================================================
"""




#imports
import copy

import BBGlobalVariables as Globals

from DataStructures.Modelling.Financials import Financials
from DataStructures.Modelling.LineItem import LineItem




#globals
name = "financials configuration for retail models"
author = "IOP"
date = "03/26/2015"
#
topic_content = True
extra_prep = False
#
requiredTags = ["Retail",
                "Overview"]
optionalTags = ["Default Financials",
                "Simple",
                "Calibration",
                "Start"]
#
applied_drivers = dict()
formula_names = []
question_names = []
work_plan = {}

#define scenario functions first, then make a scenarios dictionary. 

def scenario_1(topic):
    """


    scenario_1(topic) -> None


    **Scenario concludes with wrap_topic()**
    
    Scenario creates a set of income statement lineitems, tags them with some
    descriptive tags, and inserts them into top-level financials.

    Scenario then Model's interview path and default financials to a copy of
    the filled out financials. 
    """
    M = topic.MR.activeModel
    topBU = M.currentPeriod.content
    top_fins = topBU.financials
    top_fins.buildDictionaries()
    #
    structure = LineItem("Structure")
    structure.tag("Deterministic", field = "req")
    structure.setPartOf(top_fins)
    structure.guide.priority.increment(3)
    structure.guide.quality.setStandards(2,5)
    #
    i_end_intro = top_fins.indexByName("|bb|end Introduction")
    top_fins.insert(i_end_intro,structure)
    #
    revenue = LineItem("Revenue")
    revenue.tag("GAAP","Operations")
    cogs = LineItem("Cost")
    cogs.tag("GAAP","Operations","COGS","excludes d&a")
    opex = LineItem("Operating Expense")
    opex.tag("GAAP","Operations","excludes d&a")
    sga = LineItem("SG&A")
    sga.tag("GAAP","Operations","excludes d&a")
    ebitda = LineItem("EBITDA")
    ebitda.tag("Operations")
    #
    income_lines = [revenue,cogs,opex,sga,ebitda]
    for L in income_lines:
        L.setPartOf(top_fins)
        L.guide.priority.increment(3)
        L.guide.quality.setStandards(1,5)
    #
    i_end_is = top_fins.indexByName("|bb|end Income Statement")
    for L in income_lines[::-1]:
        top_fins.insert(i_end_is,L)
        #insert last one first so can keep using same index
    i_ovw = top_fins.indexByName("Overview")
    line_overview = top_fins[i_ovw]
    line_overview.guide.quality.increment(1)
    #
    template_fins = top_fins.copy()
    path_fins = top_fins.copy()
    M.setDefaultFinancials(template_fins)
    M.interview.setPath(path_fins)
    M.interview.clearCache()
    topic.wrap_topic()   

scenarios = dict()
#
scenarios[None] = scenario_1
#
scenarios[Globals.user_stop] = scenario_1




