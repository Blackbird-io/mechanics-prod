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
from datetime import date, timedelta

import BBGlobalVariables as Globals

from .. import SharedKnowledge as SubjectKnowledge




#globals
name = "store pre-opening period"
topic_author = "IOP"
date_created = "2015-06-02"
topic_content = True
extra_prep = False


#standard prep
requiredTags = ["Retail",
                "known search period for new store",
                "medium depth of analysis"] #--------------------------------------------------------------
optionalTags = ["Growth",
                "LifeCycle",
                "Structure",
                "Pre-Opening Period",
                "New Store Prep"]
applied_drivers = dict()
scenarios = dict()
    #ks are question names, None, or user_stop
    #values are scenario functions
work_plan = dict()

formula_names = []
question_names = ["time to open leased store?"]
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

    Scenario concludes with wrap_scenario(Q)
    
    Ask user about time to open a newly leased store. 
    """
    M = topic.MR.activeModel
    new_Q = topic.questions["time to open leased store?"]
    new_Q.input_array[0].r_max = 60
    topic.wrap_scenario(new_Q)

def scenario_2(topic):
    """


    scenario_2(topic) -> None


    **closing**
    
    Scenario concludes with wrap_topic().

    Recieve user response about pre-opening period length. Retrieve data,
    record in work_space, pass data to apply_data() for substantive work.
    """
    #
    spec_months = float(topic.get_first_answer())
    M.interview.work_space["months_to_open_leased_store"] = spec_months
    apply_data(topic, spec_months)
    topic.wrap_topic()

def apply_data(topic, datapoint):
    """

    blah
    """
    model = topic.MR.activeModel
    period = timedelta(datapoint * Globals.days_in_month)
    model.taxonomy.standard.life.gestation = period
    #
    #apply descriptive tags
    model.tag("known pre-opening period")
    model.tag("known standard gestation")
    #
    #apply tags that hook downstream topics
    model.tag("ready for growth analysis")
        
def end_scenario(topic):
    assumed_months = SK.standard_preopen_length
    apply_data(topic, assumed_months)
    topic.wrap_to_end()

#
scenarios[None] = scenario_1
#
scenarios["time to open leased store?"] = scenario_2
#
scenarios[Globals.user_stop] = end_scenario

