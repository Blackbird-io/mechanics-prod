#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: TW.Introduction.PathFinders.PathFinderTemplate
"""

This module provides a template for PathFinder topics.

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

PathFinder topics usually run right after introductory topics complete general
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

from DataStructures.Modelling.Financials import Financials
from DataStructures.Modelling.LineItem import LineItem

from . import SharedKnowledge as SK




#globals
topic_content = True
name = "Template PathFinder topic content module"
topic_author = "Ada Lovelace"
date_created = "2015-06-08"
extra_prep = False
#if extra_prep = True, TopicManager will run this module's prep() function
#after completing standard prep
PrivateKnowledge = None

#standard topic prep
user_outline_label = "Label that summarizes topic for user."
requiredTags = ["intro",
                "industry name",
                "ready for path"]
optionalTags = []
#
applied_drivers = dict()
formula_names = []
question_names = []
scenarios = dict()
work_plan = dict()

question_names = ["are you a very big business?"]
work_plan["intro"] = 1

GK = GeneralKnowledge
SK = SubjectKnowledge
PK = PrivateKnowledge

#custom prep:
def prepare(new_topic):
    #always return the topic
    return new_topic

#drivers:
#n/a

#paths:
standard_path = Financials(populate = False)
#
standard_path.extend(SK.standard_open)
standard_path.extend(SK.standard_core)
standard_path.extend(SK.standard_close)

detailed_path = standard_path.copy()
#deep-ish copy of standard path
unique_detail = LineItem("unique detail")
common_pitfall = LineItem("common pitfall")
unique_detail.tag("rebates in different time periods")
common_pitfall.tag("inventory shrink")
detailed_path.add_to("revenue", unique_detail)
detailed_path.add_to("cogs", common_pitfall)



#scenarios
#
#define each scenario, then fill out scenarios dictionary at the bottom
#each scenario must conclude with either:
    #scenarios that ask a question - topic.wrap_scenario(Q)
    #scenarios that complete processing - topic.wrap_topic()
    #scenarios that respond to a user stop - topic.wrap_to_stop()

def scenario_1(topic):
    #opening scenario, begins topic analysis, may ask q1
    #new_q = topic.questions["are you a very big business?"]
    #topic.wrap_scenario(new_q)
    pass

def scenario_2(topic):
    ##process response to q1 through apply_data()
    ##sample code below:
    #
    #response = topic.get_first_response()
    #datapoint = False
    #if response == "True":
        #datapoint = True
    #apply_data(topic, datapoint)
    #topic.wrap_topic()
    pass

def end_scenario(topic):
    ##user pressed stop interview in middle of question, limp home on
    ##assumptions
    #datapoint = False
    #apply_data(topic, datapoint)
    #topic.wrap_to_end
    pass

def apply_data(topic, datapoint):
    #function performs substantive work on model in light of new data; can use
    #as-is
    #
    intro_line = model.interview.focal_point
    model = topic.MR.activeModel
    model.tag("path set")
    model.unTag("ready for path")
    while not model.interview.point_standard(intro_line):
        intro_line.quality.increment()
    #
    vip_status = datapoint
    #
    private_path = Financials(populate = False)
    private_path.append(intro_line)
    #
    new_steps = standard_path.copy()
    if vip_status:
        new_steps = detailed_path.copy()
    private_path.extend(new_steps)
    next_step = private_path[1]
    #expect next_step to be structure
    model.interview.set_path(private_path)
    model.interview.set_focal_point(next_step)
    
    
scenarios[None] = scenario_1
scenarios["are you a very big business?"] = scenario_2
scenarios[Globals.user_stop] = end_scenario

#Conventions and general notes:
# -- n/a


