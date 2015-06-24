#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: Managers.TopicManager.TopicWarehouse.TopicTemplate
"""

A template for topic content modules. Includes all parameters available for
customization. 

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
import Managers.TopicManager.TopicWarehouse

##from Managers.TopicManager import SharedKnowledge as GeneralKnowledge
##from TopicWarehouse.ParentDirectory import SharedKnowledge as SubjectKnowledge
##from DataStructures.Modelling.Model import Model
##from DataStructures.Modelling.BusinessUnit import BusinessUnit
##from DataStructures.Modelling.Driver import Driver




#globals
topic_content = True
name = "Template topic content module"
topic_author = "Karen Von Neumann"
date_created = "2015-04-02"
extra_prep = False
#if extra_prep = True, TopicManager will run this module's prep() function
#after completing standard prep
PrivateKnowledge = None

#standard topic prep
user_outline_label = "Label that summarizes topic for user."
requiredTags = []
optionalTags = []
#
applied_drivers = dict()
formula_names = []
question_names = []
scenarios = dict()
work_plan = dict()

formula_names = ["formula 1",
                 "formula 2",
                 "indy 500"]
question_names = ["is this a template question?",
                  "is this a real?"]
work_plan["big sky line item"] = 1

GK = GeneralKnowledge
SK = SubjectKnowledge
PK = PrivateKnowledge

#custom prep
def prepare(new_topic):
    #always return the topic
    return new_topic

#drivers:
#create each driver object used in Topic and place in applied_drivers to make
#sure they receive proper signatures and ids. Provide data and formulas
#during runtime through scenarios. At that point, topic will carry dictionaries
#that point to all relevant objects. 
#
#Driver for Car Expense:
driver_car = Driver()
driver_car.setName("Jeeves, the fancy car driver")
driver_car.setWorkConditions(None,None,"Rolls-Royce Phantom")
driver_car.canBeFirst = True
driver_car.canBeLast = False
applied_driver["Car Driver"] = driver_car
#
#Driver for Boat
#...

#scenarios
#
#define each scenario, then fill out scenarios dictionary at the bottom
#each scenario must conclude with either:
    #scenarios that ask a question - topic.wrap_scenario(Q)
    #scenarios that complete processing - topic.wrap_topic()
    #scenarios that respond to a user stop - topic.wrap_to_stop()

def scenario_1(topic):
    #opening scenario, begins topic analysis, may ask q1
    pass

def scenario_2(topic):
    #process response to q1, ask q2
    pass

def scenario_3(topic):
    #process response to q2
    pass

def end_scenario(topic):
    #user pressed stop interview in middle of question
    pass

scenarios[None] = scenario_1
scenarios[Globals.user_stop] = end_scenario
#

#Conventions and general notes:
#-- Topics point to a Messenger object at ``MR``
#
#-- Topics must store drivers in applied_drivers. If they do not, TopicManager
#   will be unable to assign the drivers the bbid and signature they need to
#   operate on a BusinessUnit. 
#
#-- scenarios can use sub-scenarios to implement conditional logic.
#   sub-scenarios can wrap through the standard topic methods. if they do, the
#   parent scenario will usually conclude without further logic, unless it
#   wishes to modify the child outcome. 
#
#-- generally, revenue drivers should go in ground-level units. you can select
#   the ground-level units for a particular period by calling
#   period.selectBottomUnits()
#
#-- each unit should get its own driver object, so make sure to use
#   driver.copy() to create a new instance prior to injection
#
#-- scenarios can use only local variables or names explicitly defined in the
#   content module; scenarios will not be able to see any objects generated at
#   run time unless they are stored on the model (topics and scenarios are
#   stateless)
#
#-- be mindful of how user content fits into the structure of the response
#   object for your question type. if your topic is asking simple text or number
#   you can extract the answer by calling Topic.getFirstAnswer() or
#   getSecondAnswer().
#    
#-- topics, questions, and formulas have names with spaces. otherwise, names
#   should look like variables and use underscores. that goes for driver data
#   and question context
#
#-- dates travel in blackbird in either "YYYY-MM-DD" string format or as a POSIX
#   timestamp (float in seconds)
#
#-- topics should map scenarios to the questions whose responses they handle by
#   question name; question manager will then use that mapping to build up live
#   dictionaries keyed by bbid.



