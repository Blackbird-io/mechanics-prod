#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Engine
#Module: TopicManager.__init__
"""

Module builds and administers a catalog of Topic objects from content modules
in TopicWarehouse. 
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
local_catalog         instance of Platform.Catalog;by_name also keyed by content
id                    instance of Platform.ID; bbid set to "TopicManager"

FUNCTIONS:
clean_questions()     put clean mini questions on a topic
load_drivers()        id and validate content drivers, put them on topic
load_formulas()       put formulas on topic from catalog based on content spec
load_questions()      put questions on topic from catalog based on content spec
load_scenarios()      build a topic scenario dictionary keyed by question id
make_topic()          create a Topic object that applies logic in content module  
populate()            create and record all Topics in TopicWarehouse in catalog               

CLASSES:
LocalCatalog          subclass of Catalog that cleans questions on every call
====================  ==========================================================
"""




#imports
import inspect

import BBExceptions
import BBGlobalVariables as Globals

import content.color_manager as ColorManager
import content.formula_manager as FormulaManager
import content.question_manager as QuestionManager

from data_structures.system.bbid import ID
from data_structures.system.catalog import Catalog
from data_structures.system.topic import Topic
from tools.for_managers import walk_package

from . import topic_warehouse as TopicWarehouse




#globals
ColorManager.populate()
FormulaManager.populate()
QuestionManager.populate()

id = ID()
id.assignBBID("TopicManager")
#globals continued at the end of module

#classes
class LocalCatalog(Catalog):
    """

    Class customizes Platform.Catalog. Provides a specialized issue method that
    puts a new set of clean mini questions on every topic instance prior to
    release. 
    ==========================  ================================================
    Attribute                   Description
    ==========================  ================================================

    DATA:
    n/a

    FUNCTIONS:
    issue()                     returns topic with clean mini questions
    ==========================  ================================================
    """
    def __init__(self):
        Catalog.__init__(self)

    def issue(self, key):
        """


        LocalCatalog.issue(key) -> topic


        Method retries a topic through Catalog.issue(), clears the topic's
        ``questions`` attribute and then refills the topic with new instances of
        the mini questions it originally carried.

        Throwing away mini questions after every use ensures that Blackbird
        doesn't pollute new interviews with prior objects customizing the same
        question module.
        """
        topic = Catalog.issue(self, key)
        q_names = sorted(topic.questions.keys())
        del topic.questions
        clean_questions(topic, q_names)
        #
        return topic

#globals (continued)
local_catalog = LocalCatalog()

#functions
def clean_questions(topic, question_names, outline_label = None):
    """


    clean_questions(topic, question_names) -> None


    Function sets topic.questions to a blank dictionary, then populates the
    dictionary with MiniQuestion objects.

    Function walks through ``question_names``. For each name, function locates
    a matching FullQuestion object in QuestionManager.catalog and condenses the
    FullQuestion into a MiniQuestion using QuestionManager.make_mini(). Function
    then adds the MiniQuestion to topic's ``questions`` dictionary, keyed under
    question's **name** for ease of access.
    """
    topic.questions = dict()
    for question_name in question_names:
        full_question = QuestionManager.local_catalog.issue(question_name)
        mini_question = QuestionManager.make_mini(full_question)
        if outline_label:
            mini_question.topic_name = outline_label
        topic.questions[question_name] = mini_question

def load_drivers(topic, content_module):
    """


    load_drivers(topic, content_module) -> None


    Function records items in content_module's ``applied_drivers`` dictionary
    in topic.applied_drivers. Before making the recording, function assigns
    bbids and signatures to each driver.

    INACTIVE: Method only records drivers that validate against formula catalog.
    Right now, Driver.validate() requires a bbid for the formula that driver
    will use. Topic authors do not have an easy way to locate bbids prior to
    runtime.
    """
    topic.applied_drivers = dict()
    if not topic.id.bbid:
        c = "Topic %s does not have proper bbid. Cannot load drivers."
        c = c % topic.tags.name
        raise BBExceptions.IDAssignmentError(c)
    else:
        for (driver_name, driver_obj) in content_module.applied_drivers.items():
            driver_obj.id.setNID(topic.id.bbid)
            driver_obj.id.assignBBID(driver_name)
            new_sig = ("Driver: ..." + str(topic.id.bbid)[-6:]
                       + " " + str(driver_name))
            driver_obj.setSignature(new_sig)
##            if driver_obj.validate():
##                topic.applied_drivers[driver_name] = driver_obj
##            else:
##                c = "Driver ``%s`` in topic ``%s`` failed to validate."
##                c = c % (driver_name, content_module.name)
##                raise BBExceptions.CatalogError(c)
            topic.applied_drivers[driver_name] = driver_obj
            
def load_formulas(topic, content_module):
    """


    load_formulas(topic, content_module) -> None


    Function sets topic.formulas to a blank dictionary, then populates the
    dictionary with formula objects that content_module references.

    Function walks through content's ``formula_names`` list. For each name,
    function locates the matching formula object in FormulaManager.catalog.
    Function then adds the matching formula object to topic's ``formulas``
    dictionary, keyed under formula's **name** (for ease of access by
    content drivers).
    """
    topic.formulas = dict()
    for formula_name in content_module.formula_names:
        formula_bbid = FormulaManager.local_catalog.by_name[formula_name]
        formula = FormulaManager.local_catalog.issue(formula_bbid)
        topic.formulas[formula_name] = formula

def load_questions(topic, content_module):
    """


    load_questions(topic, content_module) -> None


    Function populatesf topic with questions named in content module. Function
    delegates work to clean_questions().
    """
    q_names = content_module.question_names
    q_label = getattr(content_module, "user_outline_label", None)
    clean_questions(topic, q_names, q_label)

def load_scenarios(topic, content_module):
    """


    load_scenarios(topic, content_module) -> None


    Function records items in content_module's ``scenarios`` dictionary in
    topic.scenarios.

    Content modules in the TopicWarehouse key scenarios based on the name of the
    question whose response the scenario handles. By contrast, Topic.process()
    needs to select scenarios based on the bbid of an incoming question.

    This function looks up question objects in the topic's ``questions``
    dictionary and records known scenarios under their ids. As a result, this
    function requires that the topic object have a built-out ``questions``
    dictionary. Function will also raise an error if number of scenarios on
    topic at completion does not properly match expectations. 
    """
    topic.scenarios = dict()
    #
    #handle the special keys first
    start_scenario = content_module.scenarios.pop(None)
    end_scenario = content_module.scenarios.pop(Globals.user_stop)
    topic.scenarios[None] = start_scenario
    topic.scenarios[Globals.user_stop] = end_scenario
    #
    #now move the keys that support bbids
    for (question_name,scenario) in content_module.scenarios.items():
        question_bbid = topic.questions[question_name].id.bbid
        topic.scenarios[question_bbid] = scenario
    #
    #validate
    scenes = len(topic.scenarios)
    qs = len(topic.questions)
    expected = qs + 2
    if scenes != expected:
        c = "Number of scenarios does not match number of questions."
        raise BBExceptions.CatalogError(c)
    #
    #a topic that does not ask any questions will have 1 scenario, keyed to
    #both None and user_stop. Since two keys point to the same scenario,
    #len(scenarios) for that topic will be 2. a topic that asks one question
    #will have len(scenarios) == 3: one scenario to open analysis, one to
    #process response, and a third for user_stop. a topic that asks 2 questions
    #will have 4 scenarios: one to open, two to process each response, and one
    #to handle a user_stop. and so on. 
    #
        
def make_topic(content_module, catalog = local_catalog):
    """


    make_topic(content_module) -> Topic


    Method constructs and registers a Topic object with content from the
    content_module.

    Algorithm:
     -- create clean instance of Topic
     -- set topic name to content module's name
     -- tag topic with tags specified in content module
     -- record content workplan on topic through add_work_item()
     -- set topic namespace id to TopicManager's bbid
     -- assign topic a bbid derived from its name
     -- fill topic.formulas with objects using load_formulas
     -- fill topic.questions with objects using load_questions
     -- fill topic.scenarios with objects using load_scenarios
     -- fill topic.drivers with objects using load_drivers
     -- if content module requires extra prep, run module's prepare()
    
    After method finishes assembling the content-ful topic, method registers it
    in the local catalog.
    """
    if not content_module.name:
        c = "cant add nameless modules"
        raise BBExceptions.CatalogError(c)
    #
    #make clean shell
    new_topic = Topic()
    #
    #tag
    new_topic.tags.setName(content_module.name)
    new_topic.tags.tag(*content_module.requiredTags, field = "req")
    new_topic.tags.tag(*content_module.optionalTags, field = "opt")
    for (line, contribution) in content_module.work_plan.items():
        new_topic.add_work_item(line, contribution)
    #
    #id
    new_topic.id.setNID(id.namespace_id)
    new_topic.id.assignBBID(new_topic.tags.name)
    #
    #source (uses relative path for cwd)
    location = inspect.getfile(content_module)
    new_topic.source = location
    #
    #load moving pieces (logic for run-time)
    load_formulas(new_topic, content_module)
    #always load formulas first; the topic's drivers expect to see objects
    #in the dictionary so they can track their bbid
    load_questions(new_topic, content_module)
    load_scenarios(new_topic, content_module)
    load_drivers(new_topic,content_module)
    #
    #let module do more prep if necessary
    if content_module.extra_prep:
        new_topic = content_module.prepare(new_topic)
    #
    #wrap
    reverse_lookup_keys = [new_topic.tags.name, content_module, location]
    catalog.register(new_topic, *reverse_lookup_keys)
    return new_topic

def populate():
    """


    populate() -> None


    Function walks the TopicWarehouse and applies make_topic() to every module
    that specifies topic_content to be True. Function then marks local_catalog
    as populated.

    To avoid key collisions on parallel imports, populate() performs a no-op
    if catalog is already populated.
    """
    if not local_catalog.populated:
        topic_count = walk_package(TopicWarehouse, "topic_content", make_topic)
        local_catalog.populated = True
        c = ""
        c += "TopicManager successfully populated catalog with %s topics."
        c = c % topic_count
        print(c)
    else:
        pass


