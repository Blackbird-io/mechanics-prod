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

from data_structures import modelling
from data_structures.modelling.business_unit import BusinessUnit

from ..structure.standard_financials import basic_fins




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
                "Introduction",
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
    response = topic.get_first_answer()
    model = topic.MR.activeModel
    model.setName(response)
    model.stage.work_space["company_name"] = response
    new_question = topic.questions["company industry?"]
    #
    topic.wrap_scenario(new_question)

def scenario_3(topic):
    known_industries = []
    user_industry = topic.get_first_answer()
    model = topic.MR.activeModel
    if user_industry in known_industries:
        model.tag("known industry")
    else:
        model.tag("unknown industry")
    model.tag(user_industry)
    model.interview.work_space["industry"] = user_industry
    #
    new_question = topic.questions["user name?"]
    topic.wrap_scenario(new_question)

def scenario_4(topic):
    common_names = []
    R = topic.get_first_answer()
    M = topic.MR.activeModel
    M.interview.work_space["author name"] = R
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
    M.interview.work_space["author role"] = R
    if R in decision_people:
        M.tag("author role: decision")
    if R in fin_people:
        M.tag("author role: finance")
    if R in big_roles:
        M.tag("author role: big")
    #
    new_question = topic.questions["company start date?"]
    if M.name:
        new_question.context["company_name"] = str(M.name)
    today_date_string = datetime.date.today().isoformat()
    new_question.input_array[0].r_max = today_date_string
    topic.wrap_scenario(new_question)

def scenario_6(topic):
    #
    model = topic.MR.activeModel
    response = topic.get_first_answer()
    #R is a string in YYYY-MM-DD format; split into integers so can create an
    #actual date object
    #
    adj_r = [int(x) for x in response.split("-")]
    date_of_birth = datetime.date(*adj_r)
    #
    company = BusinessUnit(model.name, fins = basic_fins.copy())
    estimated_conception = date_of_birth - company.life.gestation
    company.life.date_of_conception = estimated_conception
    #
    basic_unit = company.copy()
    basic_unit.setName("Basic Unit Template")
    #basic unit shares company's life characteristics and fins, but doesn't
    #have a type
    #
    company.type = "company"
    model.time_line.current_period.set_content(company)
    model.taxonomy["standard"] = basic_unit
    #
    fp = model.interview.focal_point
    fp.guide.quality.increment(1)
    model.tag("ready for path")
    #
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
scenarios["company start date?"] = scenario_6
#
scenarios[Globals.user_stop] = end_scenario



