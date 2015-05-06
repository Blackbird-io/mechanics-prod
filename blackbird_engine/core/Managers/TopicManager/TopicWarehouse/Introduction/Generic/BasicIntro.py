#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: Managers.TopicManager.TopicWarehouse.TopicTemplate
"""

Basic intro topic

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
scenario_1
scenario_2
scenario_3
scenario_4
scenario_5

CLASSES:
n/a
====================  ==========================================================
"""




#imports
import datetime
import time

import BBGlobalVariables as Globals

from DataStructures import Modelling




#globals
name = "simple introduction for generic model."
author = "IOP"
date = "03/26/2015"
#
topic_content = True
extra_prep = False
#set to True to have TopicManager run this module's prep after it finishes own config
#
requiredTags = []
optionalTags = ["Overview",
                "Start",
                "Automatic",
                "Default"]
#
applied_drivers = dict()
formula_names = []
question_names = ["company name?",
                  "company industry?",
                  "company start date?",
                  "user name?",
                  "user position?",
                  ]
work_plan = {}
#instead of using a work_plan, this topic manually increments overview in
#scenario 5 to track legacy topic architecture

#scenarios filled in at bottom of module, after any defs

def scenario_1(topic):
    #asks user about company name
    new_question = topic.questions["company name?"]
    topic.wrap_scenario(new_question)

def scenario_2(topic):
    R = topic.get_first_answer()
    M = topic.MR.activeModel
    M.setName(R)
    new_question = topic.questions["company industry?"]
    topic.wrap_scenario(new_question)

def scenario_3(topic):
    known_industries = []
    R = topic.get_first_answer()
    #pull out substantive response
    M = topic.MR.activeModel
    topBU = M.currentPeriod.content
    i_overview = topBU.financials.indexByName("Overview")
    line_overview = topBU.financials[i_overview]
    if R in known_industries:
        M.tag("known industry")
        line_overview.tag("known industry")
    else:
        M.tag("unknown industry")
        line_overview.tag("unknown industry")
    M.tag(R)
    line_overview.tag(R)
    M.header.profile["industry"] = R
    #
    new_question = topic.questions["user name?"]
    topic.wrap_scenario(new_question)

def scenario_4(topic):
    common_names = []
    R = topic.get_first_answer()
    M = topic.MR.activeModel
    M.header.profile["author name"] = R
    new_question = topic.questions["user position?"]
    if M.name:
        new_question.context["company_name"] = str(M.name)
    topic.wrap_scenario(new_question)

def scenario_5(topic):
    R = topic.get_first_answer()
    M = topic.MR.activeModel
    decision_people = ["ceo",
                       "coo",
                       "cfo",
                       "president",
                       "partner",
                       "member",
                       "director",
                       "investment professional",
                       "portfolio manager"]
    fin_people = ["ceo",
                  "cfo",
                  "president",
                  "controller",
                  "finance",
                  "accountant",
                  "audit",
                  "investment"]
    big_roles = set(decision_people + fin_people)
    R = R.casefold()
    M.header.profile["author role"] = R
    topBU = M.currentPeriod.content
    i_overview = topBU.financials.indexByName("Overview")
    line_overview = topBU.financials[i_overview]
    if R in decision_people:
        M.tag("author role: decision")
        line_overview.tag("author role: decision")
    if R in fin_people:
        M.tag("author role: finance")
        line_overview.tag("author role: finance")
    if R in big_roles:
        M.tag("author role: big")
        line_overview.tag("author role: big")
    #
    new_question = topic.questions["company start date?"]
    today_date_string = datetime.date.today.isoformat()
    new_question.input_array[0].r_max = today_date_string
    topic.wrap_scenario(new_question)

def scenario_6(topic):
    #
    M = topic.MR.activeModel
    R = topic.get_first_answer()
    #R is a string in YYYY-MM-DD format; split into integers so can create an
    #actual date object
    #
    adj_r = [int(x) for x in R.split("-")]
    date_of_birth = datetime.date(*adj_r)
    dob_in_seconds = time.mktime(date_of_birth.timetuple())
    #
    top_bu = M.currentPeriod.content
    top_bu.lifeCycle.set_dob(dob_in_seconds)
    #
    line_overview.guide.quality.increment(1)
    topic.wrap_topic()

def end_scenario(topic):
    pass
    #leave empty for now

scenarios = dict()
scenarios[None] = scenario_1
#
scenarios["company name?"] = scenario_2
scenarios["company industry?"] = scenario_3
scenarios["user name?"] = scenario_4
scenarios["user position?"] = scenario_5
secnarios["company start date?"] = scenario_6
#
scenarios[Globals.user_stop] = end_scenario



