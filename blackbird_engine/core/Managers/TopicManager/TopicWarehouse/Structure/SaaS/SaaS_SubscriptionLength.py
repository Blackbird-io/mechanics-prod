#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: TW.Structure.Deterministic.StoreLocationSearch
"""

Configure a standard subscription. A subscription is a business unit with
very simple financials (?). Has a revenue line, a prepaid revenue line on
liabilities, a cash line on assets. The unit has a size component so it ca`n
cover multiple customers. Formulas use the "size" factor as a multiplier.

Alternative is to have customer relationship have a tenure. Then when contract
expires, customer can become dead? 

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
from datetime import date, timedelta

import BBGlobalVariables as Globals

from .. import SharedKnowledge as SubjectKnowledge


#globals
name = "saas subscription length"
topic_author = "IOP"
date_created = "2015-06-06"
topic_content = True
extra_prep = False


#standard prep
requiredTags = ["saas",
                "structure"]
optionalTags = ["subscriptions",
                "subscription length",
                "contract duration",
                "term of services",
                "contract length",
                "contracted revenues",
                "context only"]
applied_drivers = dict()
scenarios = dict()
    #ks are question names, None, or user_stop
    #values are scenario functions
work_plan = dict()

formula_names = []
question_names = ["software function?"]
work_plan["overview"] = 1
work_plan["product"] = 1

SK = SubjectKnowledge

#scenarios
#
#define scenario functions, then fill out scenarios dictionary
#scenarios must end with either:
    #scenarios that ask a question - topic.wrap_scenario()
    #scenarios that complete processing - topic.wrap_topic()
    #scenarios that respond to a user stop - topic.wrap_to_end()
#
def scenario_1(topic):
    """


    scenario_1(topic) -> None


    **opening**

    Scenario concludes with wrap_scenario(Q)
    
    Ask user about software function.
    """
    M = topic.MR.activeModel
    new_Q = topic.questions["what does your software do?"]
    topic.wrap_scenario(new_Q)

def scenario_2(topic):
    """


    scenario_2(topic) -> None


    **closing**
    
    Scenario concludes with wrap_topic().

    Receive user response about software function.  Retrieve data,
    record in work_space.
    """
    long_desc = topic.get_first_response()
    M.interview.work_space["product_function"] = long_desc
    topic.wrap_topic()

def end_scenario(topic):
    """


    end_scenario(topic) -> None


    **ending**

    Scenario concludes with wrap_to_end().

    No-op here.
    """
    topic.wrap_to_end()

#
scenarios[None] = scenario_1
#
scenarios["software function?"] = scenario_2
#
scenarios[Globals.user_stop] = end_scenario

