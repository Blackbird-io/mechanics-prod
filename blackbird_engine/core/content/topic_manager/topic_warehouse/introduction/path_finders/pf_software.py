#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: TW.Introduction.PathFinders.PF_Generic
"""

Content for topic that builds generic paths (same path for all industries).
Topic does not ask any questions. 

PathFinder topics create the path that InterviewController follows to build up
a model step by step. IC walks the path (visible through M.interview.path) and
asks Yenta to find the best-matching topic for each line.

PathFinder sets the initial path, NOT the definitive path. Topics that run after
PathFinder (downstream) can modify the initial path as more information becomes
available about the business. Downstream topics can add or delete steps, adjust
the relative priorities of each line, etc. For example, if a downstream topic
locates a healthcare business with a large portion of revenue coming from
Medicare, that topic can insert a "Fraud" line into the path to ensure further
analysis. 

PathFinder topcis usually run right after introductory topics complete general
information gathering and can differentiate one business from another somewhat
(usually by industry).
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
from data_structures.modelling._new_statement import Statement
from data_structures.modelling.line_item import LineItem
from tools import for_messages as message_tools

from . import shared_knowledge as SK




#globals
topic_content = True
name = "PathFinder for software companies"
topic_author = "Ilya Podolyako"
date_created = "2015-06-08"
extra_prep = False
#if extra_prep = True, TopicManager will run this module's prep() function
#after completing standard prep


#standard topic prep
user_outline_label = "Configure interview."
requiredTags = ["introduction",
                "ready for path"]
optionalTags = ["start",
                "configuration",
                "software",
                "saas",
                "enterprise software",
                "service-type business",
                "compensation is the most significant expense",
                "human-capital-intensive business",
                "personnel-intensive",
                "pathfinder"]
#
applied_drivers = dict()
formula_names = []
question_names = []
scenarios = dict()
work_plan = dict()

work_plan["introduction"] = 1
work_plan["path"] = 1

#drivers:
#n/a

#paths:
standard_path = Statement()
standard_path.extend(SK.standard_open.copy())
standard_path.extend(SK.standard_core.copy())
standard_path.extend(SK.standard_close.copy())
#
# Refine standard path
# 0. increase the quality requirements for structure
structure = standard_path.find_first("structure")
structure.guide.quality.set_standard(3) #max used to be 5

# 1. reduce the significance of product cost
cost = standard_path.find_first("cost")
cost.guide.priority.reset()
cost.guide.priority.increment(1)

# 2. add important details to opex
opex = standard_path.find_first("operating expense")
opex.guide.priority.reset()
opex.guide.priority.increment(1)
# opex details are more important here than the general category

# Opex details:
head_count = LineItem("employee count")
head_count.tag("all teams",
               "full-time employees",
               "head count",
               "part-time employees",
               "personnel",
               "staff",
               "staffing",
               "staffing structure",
               "team composition",
               "team structure")

base_comp = LineItem("base compensation")
base_comp.tag("compensation",
              "employee expense",
              "operating expense",
              "expense",
              "salaries",
              "cash expense")

bonus_cash = LineItem("cash bonus")
bonus_cash.tag("compensation",
               "employee expense",
               "operating expense",
               "expense",
               "cash expense",
               "incentive compensation",
               "bonus",
               "variable",
               "variable compensation",
               "cash bonus")

bonus_stock = LineItem("equity bonus")
bonus_stock.tag("compensation",
                "employee expense",
                "operating expense",
                "expense",
                "non-cash expense",
                "ebitda adjustment",
                "add-back",
                "cash flow add-back",
                "cash flow adjustment",
                "incentive compensation",
                "bonus",
                "variable",
                "variable compensation")

taxes = LineItem("employment taxes")
taxes.tag("employee expense",
          "payroll taxes",
          "workers' comp",
          "medicare")

benefits = LineItem("benefits")
benefits.tag("employee expense",
             "health insurance")

opex_details = [head_count,
                base_comp,
                bonus_cash,
                bonus_stock,
                taxes,
                benefits]
#
for line in opex_details:
    line.guide.priority.reset()
    line.guide.priority.increment(3)
    line.guide.quality.set_standard(3) #max used to be 5
    standard_path.add_line_to(line.copy(), "operating expense")

#3. increase quality requirements for sg&a, place it under opex
sga = standard_path.find_first("sg&a", remove=True)
sga.guide.quality.set_standard(4) #max used to be 6
standard_path.add_line_to(sga, "operating expense")

##sga.tag(opex.name) #<-------------------------------------------------------imperfect, just trying out
##sga.setPartOf(opex)

#4. add an AEBITDA line
adj_ebitda = LineItem("Adjusted EBITDA")
standard_path.add_top_line(adj_ebitda.copy(), after = "ebitda")






#scenarios
#
#define each scenario, then fill out scenarios dictionary at the bottom
#each scenario must conclude with either:
    #scenarios that ask a question - topic.wrap_scenario(Q)
    #scenarios that complete processing - topic.wrap_topic()
    #scenarios that respond to a user stop - topic.wrap_to_stop()

def scenario_1(topic):
    #opening scenario, begins topic analysis, may ask q1    
    apply_data(topic)
    topic.wrap_topic()

def apply_data(topic):
    #function performs substantive work on model in light of new data; can use
    #as-is
    #    
    model = topic.MR.activeModel
    model.tag("path set")
    model.unTag("ready for path")
    #
    intro_line = model.interview.focal_point
    intro_line.guide.quality.set_standard(4) #max used to be 6
    intro_line.guide.priority.reset()
    intro_line.guide.priority.increment(3)
    #
    private_path = Statement()
    private_path.append(intro_line)
    #if elaborating on intro, should do so here<<<<<<
    #
    new_steps = standard_path.copy()
    private_path.extend(new_steps)
    #
    model.interview.clear_cache()
    model.interview.set_path(private_path)

def end_scenario(topic):
    c = "Topic %s does not ask questions. Process should not be in "
    c += "end_scenario."
    c = c % topic.name
    raise BBExceptions.AnalyticalError(c)
    
scenarios[None] = scenario_1
scenarios[message_tools.USER_STOP] = end_scenario


