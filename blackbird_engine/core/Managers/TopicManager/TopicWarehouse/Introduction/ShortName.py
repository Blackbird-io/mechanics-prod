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
question_names = ["is this a template question?"]
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
    """


    scenario_1(topic) -> None


    **opening scenario**

    Scenario concludes with wrap_scenario(question).

    Function asks question. 
    """
    #opening scenario, begins topic analysis, may ask q1. can configure
    #question based on model data.
    pass
    #if short name == model.name, don't bother
    #

def scenario_2(topic):
    """


    scenario_2(topic) -> None


    **closing scenario**

    Scenario concludes with wrap_topic()

    Function pulls out user response and [. . . ]
    """
    #pull out user response, process as necessary; store in work_space, then
    #run apply_data(topic, adj_response). then wrap_topic.
    #
    #ALL SUBSTANTIVE WORK SHOULD TAKE PLACE IN apply_data()
    pass

def end_scenario(topic):
    """


    end_scenario(topic) -> None

    **end scenario**

    Scenario concludes with wrap_to_end().
    
    [] 
    """
    pass

def apply_data(topic, datapoint):
    """


    apply_data(topic, datapoint) -> None


    [describe substantive work that topic does to model based on data]
    """
    #function performs substantive work on model in light of new data

def prep_data(topic):
    """

    do all the hard work here

    make a short name

for intro, add a short-name module. when gets name:
   take name. that's full_name
   general: 
        if first word is "the", drop it
   
   make acronym:
        if first word is "the", drop it
 	drop anything after the comma
        split by space
        take first letter of each word
   if last word before comma is "company" or "management":
        "trading"
        "construction"
        "distribution"
        "analytics"
        "group"
        "firm"
        "bank"
        "sellers"
	"capital"  -> should lead to question about whether you are in the business of investing
	"securities" -> are you in the business of investing? 
		#if so, say this is for borrowers. 
		#ask if they want to go through the process for a particular company
			#if yes, start modelling that company
			#if no, kick out of the interview. 
        
        use first word as short_name
         
        e.g., 
          Ford Motor Company
          SAC Capital Management, 
          First Recovery Group, 
          Blackbird Logical Applications
          Clearwater Analytics
        but:
          International Business Machines, 

	other ones:
	   Cravath, Swaine & Moore, LLP
	   Kirkland & Ellis, LLP
	   Lindsay Goldberg, LLC
	   Garrison Securities
        
   ask if it's ok to use the short_name as the company name
        if not, use full name

    
    """
    model = topic.MR.activeModel
    full_name = model.name
    short_name = None
    #pre-processing:
        #drop first word iff:
            #the
        #find last comma, drop anything to the right of it
            #so cravath, swaine & moore, llp -> drops "llp"
            #can tag as "legal entity: "
                #can translate into "limited liability company", corporation, etc.
                #
        #make a list of words:
            #get rid of any commas
            #split remainder by space
        #make a list of major words
            #filter out single-char strings ["a"]
            #filter our "and"
        #drop 
        #
    ##if ever get to 0 words, stop processing
    ##
    #rule 1: 1-2 major words
        #if name is 2 words or less:
            #take first 2 major words and everything between them
            #[Kirkland & Ellis, LLP] -> "Kirkland & Ellis"
            #
        #if name is one word:
            #take the one word
    #rule 2: 3+ words
        #if name 


scenarios[None] = scenario_1
scenarios["is this a real question?"] = scenario_2
scenarios[Globals.user_stop] = end_scenario



