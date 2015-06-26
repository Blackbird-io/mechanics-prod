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
import BBGlobalVariables as Globals

from DataStructures.Modelling.LineItem import LineItem
from DataStructures.Modelling.Financials import Financials

from . import SharedKnowledge as SK




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

work_plan["intro"] = 1

#drivers:
#n/a

#paths:
standard_path = Financials(populate = False)
standard_path.extend(SK.standard_open.copy())
standard_path.extend(SK.standard_core.copy())
standard_path.extend(SK.standard_close.copy())
#
#refine standard path
#1. reduce the significance of product cost
cost_i = standard_path.indexByName("cost")
cost = standard_path[cost_i]
cost.guide.priority.reset()
cost.guide.priority.increment(1)
#
opex_i = standard_path.indexByName("operating expense")
opex = standard_path[opex_i]
opex.guide.priority.reset()
opex.guide.priority.increment(1)
#opex details are more important here than the general thing
#
employee_expense = LineItem("Employee Expense")
employee_expense.tag(
                     "base compensation",
                     "bonus",
                     "compensation",
                     "full-time employees",
                     "incentive compensation",
                     "part-time employees",
                     "personnel",
                     "salaries",
                     "staff",
                     "staffing",
                     "stock compensation",
                     #
                     "payroll taxes",
                     "health insurance",
                     "benefits")
employee_expense.guide.priority.reset()
employee_expense.guide.priority.increment(3)
employee_expense.guide.quality.setStandards(4,5)
standard_path.add_line_to(employee_expense.copy(), "operating expense")



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
    while not model.interview.point_standard(intro_line):
        intro_line.guide.quality.increment()
    #
    private_path = Financials(populate = False)
    private_path.append(intro_line)
    #if elaborating on intro, should do so here<<<<<<
    #should replace intro with the actual used line
    #
    new_steps = standard_path.copy()
    private_path.extend(new_steps)
    next_step = private_path[1]
    #expect next_step to be structure
    #
    model.interview.clear_cache()
    model.interview.set_path(private_path)
    model.interview.set_focal_point(next_step)

def end_scenario(topic):
    c = "Topic %s does not ask questions. Process should not be in "
    c += "end_scenario."
    c = c % topic.name
    raise BBExceptions.AnalyticalError(c)
    
scenarios[None] = scenario_1
scenarios[Globals.user_stop] = end_scenario


