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
from DataStructures.Modelling.BusinessUnit import BusinessUnit

from .. import SharedKnowledge as SubjectKnowledge


#globals
name = "store location search period"
topic_author = "IOP"
date_created = "2015-06-02"
topic_content = True
extra_prep = False


#standard prep
requiredTags = ["Retail"]
optionalTags = ["Growth",
                "LifeCycle",
                "Structure",
                "Location Search",
                "New Store Prep"]
applied_drivers = dict()
scenarios = dict()
    #ks are question names, None, or user_stop
    #values are scenario functions
work_plan = dict()

formula_names = []
question_names = ["time to sign new store lease?"]
work_plan["structure"] = 1
work_plan["growth"] = 1

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

    Ask user about time to find a new property. 
    """
    M = topic.MR.activeModel
    new_Q = topic.questions["time to sign new store lease?"]
    new_Q.input_array[0].r_max = 60
    topic.wrap_scenario(new_Q)

def scenario_2(topic):
    """


    scenario_2(topic) -> None


    Scenario concludes with wrap_scenario(Q).

    Get answer about search length. Set to life.search. Ask about time
    to open.
    """
    #
    M = topic.MR.activeModel
    spec_months = int(topic.get_first_answer())
    M.interview.work_space["months_to_find_property"] = spec_months
    #f should do all substantive work
    apply_data(topic, spec_months)
    topic.wrap_topic()

def apply_data(topic, datapoint):
    """
    function expects datapoint to be an integer count of months necessary for
    company to find a new store location. 
    """
    model = topic.MR.activeModel
    model.taxonomy.standard.life.search = timedelta(search_in_months)
    model.tag("known search period for new store")
    #next topic requires this tag to run
        
def end_scenario(topic):
    assumed_months = SK.standard_search_length
    apply_data(topic, assumed_months)
    topic.wrap_to_end()

#
scenarios[None] = scenario_1
#
scenarios["time to sign new store lease?"] = scenario_2
#
scenarios[Globals.user_stop] = end_scenario

