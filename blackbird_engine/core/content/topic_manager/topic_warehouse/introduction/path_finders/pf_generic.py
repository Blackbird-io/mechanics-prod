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
from tools import for_messages as message_tools

from . import shared_knowledge as SK




#globals
topic_content = True
name = "Generic PathFinder topic: standard path, all industries"
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
                "generic",
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
standard_path = Statement()
standard_path.extend(SK.standard_open.copy())
standard_path.extend(SK.standard_core.copy())
standard_path.extend(SK.standard_close.copy())



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
    while not model.interview.completion_rule(intro_line):
        intro_line.guide.quality.increment()
    #
    private_path = Statement()
    private_path.append(intro_line)
    #
    new_steps = standard_path.copy()
    private_path.extend(new_steps)
    next_step = private_path.get_ordered()[1]
    #``intro`` should be at 0; expect next_step to be structure
    #
    model.interview.set_path(private_path)
    model.interview.set_focal_point(next_step)

def end_scenario(topic):
    c = "Topic %s does not ask questions. Process should not be in "
    c += "end_scenario."
    c = c % topic.name
    raise BBExceptions.AnalyticalError(c)
    
scenarios[None] = scenario_1
scenarios[message_tools.USER_STOP] = end_scenario


