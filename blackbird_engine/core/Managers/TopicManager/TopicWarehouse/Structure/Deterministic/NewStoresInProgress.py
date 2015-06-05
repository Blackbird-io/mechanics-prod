#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: TW.Structure.Deterministic.StoreLocationSearch
"""

Topic asks about stores in progress and adds in gestating business units
accordingly.

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
name = "stores in progress"
topic_author = "IOP"
date_created = "2015-06-02"
topic_content = True
extra_prep = False


#standard prep
requiredTags = ["retail",
                "ready for growth analysis"
                "medium analysis"] #--------------------------------------------------------------

optionalTags = ["In-Progress",
                "signed leases",
                "Not Yet Built",
                "LifeCycle",
                "Structure",
                "Growth"]

applied_drivers = dict()
scenarios = dict()
    #ks are question names, None, or user_stop
    #values are scenario functions
work_plan = dict()

formula_names = []
question_names = ["stores in progress?"]
work_plan["structure"] = 1
work_plan["growth"] = 1

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
    new_Q = topic.questions["stores in progress?"]
    new_Q.input_array[0].r_max = 100
    new_Q.input_array[0].r_step = 1
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
    spec_stores = round(topic.get_first_answer())
    M.interview.work_space["stores_in_progress"] = spec_stores
    apply_data(topic, spec_months)
    topic.wrap_topic()

def apply_data(topic, datapoint):
    """


    apply_data(topic, datapoint) -> None
    

    ``datapoint`` : number of stores in progress
    
    Function creates and inserts datapoint-many new stores into top unit in
    current period. Each new store is a copy of the standard operating template
    in model taxonomy. Function distributes the stores uniformly throughout the
    gestation period. 
    """
    model = topic.MR.activeModel
    top_bu = model.current_period.content
    bu_template = model.taxonomy["operating"].standard
    age_increment = bu_template.life.gestation / datapoint
    for i in range(datapoint):
        new_store = bu_template.copy()
        est_conception = Globals.ref_date - (age_increment * (i + 1))
        new_store.life.date_of_conception = est_conception
        new_store.tag("in-progress",
                      "leased not opened")
        label = "New Store (%s) #%s" % (new_store.life.date_of_birth.year, i)
        new_store.set_name(label)
        top_bu.add(new_store)
    top_bu.life.brood = datapoint
    #
    #add to milestones? not specific enough for store-level verification. can
    #add a milestone at final dob + 10% re new stores opened (or total store
    #count).
    #
    model.tag("stores in progress")
        
def end_scenario(topic):
    """


    end_scenario(topic) -> None


    **end scenario**

    Scenario concludes with wrap_to_end()

    On user interrupt, scenario assumes that 0 stores are in progress and runs
    apply_data() accordingly. 
    """
    assumption = 0
    apply_data(topic, assumption)
    topic.wrap_to_end()

#
scenarios[None] = scenario_1
#
scenarios["stores in progress?"] = scenario_2
#
scenarios[Globals.user_stop] = end_scenario

