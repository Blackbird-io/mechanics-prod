#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: TW.Structure.Deterministic.StoreLocationSearch
"""

Topic asks user about time to find a new location for lease. 

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
from tools import for_messages as message_tools

from .. import SharedKnowledge as SubjectKnowledge




#globals
name = "software function"
topic_author = "IOP"
date_created = "2015-06-06"
topic_content = True
extra_prep = False


#standard prep
requiredTags = ["saas"]
optionalTags = ["subscriptions",
                "introduction",
                "context only",
                "free-form text",
                "for transcript",
                "for external review",
                "model stays the same",
                "lazy"]
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
scenarios[message_tools.USER_STOP] = end_scenario

