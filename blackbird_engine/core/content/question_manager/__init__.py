#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Engine
#Module: QuestionManager.__init__
"""

Module builds and administers a catalog of question objects from content modules
in QuestionWarehouse. The catalog stores FullQuestion objects for each content
module. These specify all of the details necessary to properly configure and
display the question to a user. 

Topic objects can ask questions when they need specific information about a
business. To do so, Topics use MiniQuestions. MiniQuestions provide a shortened
form that includes all of the attributes a Topic can customize (like the
``context`` dictionary for custom prompts) and skip other data. 

To add a question to the catalog, users should place a new module that follows
the question_template format in the Warehouse.

QuestionManager rebuilds the catalog at every launch. 

====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
catalog               instance of custom Catalog class w expanded issue() method 
id                    instance of Platform.ID; bbid set to "QuestionManager"

FUNCTIONS:
make_full()           turn MiniQuestion object into a FullQuestion object
make_mini()           turn FullQuestion object into a MiniQuestion for tweaks
make_portal()         turn Mini0Question object into an API-spec dictionary
make_question()       build FullQuestion object from a content module
populate()            walk warehouse, make questions, record in the catalog               

CLASSES:
LocalCatalog          subclass of Platform.Catalog that issues copies of entries
====================  ==========================================================
"""




#imports
import inspect

import BBExceptions

from data_structures.portal.full_question import FullQuestion
from data_structures.portal.mini_question import MiniQuestion
from data_structures.portal.portal_question import PortalQuestion
from data_structures.system.bbid import ID
from data_structures.system.protected_catalog import ProtectedCatalog
from tools.for_managers import walk_package

from . import question_warehouse as Warehouse




#globals
my_id = ID()
my_id.assign("QuestionManager")
local_catalog = ProtectedCatalog()

#functions
def make_full(mini_q, language = "English"):
    """


    make_full(mini_q[, language = "English"]) -> FullQuestion


    Function issues a matching object from catalog, updates it, and returns
    the result. QuestionManager.catalog.issue() always returns a copy of
    the matching entry, so result is always a copy of the original entry
    as well.

    Multilanguage support currently unavailable. In the future, the ``language``
    argument can provide a subkey for internationalized versions of the same
    question. 
    """
    full_q = local_catalog.issue(mini_q.id.bbid)
    #issue() returns a copy
    full_q.update(mini_q)
    #
    return full_q

def make_mini(full_q):
    """


    make_mini(full_q) -> MiniQuestion


    Function returns a MiniQuestion object that tracks the attribute values
    of the FullQuestion argument.

    NOTE: MiniQuestion attributes point to original FullQuestion attributes.
    Since QuestionManager.catalog.issue() returns copies, each FullQuestion
    in the Engine environment should have its own set of objects for
    stateful attribute values.

    NOTE2: Function uses instance.__dict__ to update MiniQuestion
    As a result, function will only update attributes defined at the
    MiniQuestion instance and skip any visible through the class or by
    inheritance. 
    """
    new_mini = MiniQuestion()
    for attr in new_mini.__dict__:
        new_mini.__dict__[attr] = getattr(full_q,attr)
    #
    return new_mini

def make_portal(mini_q, language = "English", web = False):
    """


    make_portal(mini_q, language = "English") -> dict()


    Function returns a dictionary that follows the PortalQuestion schema from
    the Engine-Wrapper API. Dictionary contains only built-in types and is
    compatible with the json module.
    """
    blank_pq = PortalQuestion()
    #
    if mini_q:
        full_q = make_full(mini_q, language)
        full_q.set_prompt()
    else:
        full_q = PortalQuestion()
    #
    result = blank_pq.to_portal(full_q, web)
    #
    return result
    #keeps PortalQuestion independent of QuestionManager
    #keeps FullQuestion independent of QuestionManager
    
def make_question(content_module, catalog = local_catalog):
    """


    make_question(content_module) -> FullQuestion


    Function creates a FullQuestion objects that follows the specifications of
    a content_module.

    Function manually sets FullQuestion attributes to the content_module values.
    Function assigns a bbid to the FullQuestion based on the name of the
    content_module. Function then registers the FullQuestion in
    QuestionManager.catalog under the question's bbid and name (as reverse key). 

    NOTE: Function does not follow prepare() delegation pattern.
    
    Content modules for questions are usually very simple. They limit their work
    to a couple assignment statements and avoid any imports, functions, or other
    routines.

    The simple nature of question content modules helps avoid erros. Humans
    writing questions can focus their attention on wording, not Python. To
    support this division of labor, QuestionManager handles all configuration
    steps directly in the ``make_question`` function.

    By contrast, TopicManager delegates a lot of Topic configuration to the
    content_module itself, by calling content_module.prepare() on "empty" Topic
    shells. The approach fits Topics better because Topics retain significant
    power in Blackbird: they always define their own rules (e.g., tags that
    trigger application) and routines (scenarios). Humans need to be a lot more
    fluent in logic, Python, and Blackbird to write Topics than to write
    Questions.

    Flexibility and power mean that Topic A can require very different resources
    (and configuration steps) from Topic B. Accordingly, topic
    content_module.prepare() gives topic authors direct control over those
    steps. The PortalQuestion schema defines tight boundaries for Question
    configuration, so even with direct, delegated configuration, a Question
    author would have a lot less control. 
    """
    new_question = FullQuestion()
    new_question.tags.setName(content_module.name)
    #
    #id
    new_question.id.set_namespace(my_id.bbid)
    new_question.id.assign(seed=new_question.tags.name)
    # Questions get an id within the QuestionManager namespace.
    #
    #tags
    new_question.tags.tag(*content_module.requiredTags, field = "req")
    new_question.tags.tag(*content_module.optionalTags, field = "opt")
    #
    #source
    location = inspect.getfile(content_module)
    new_question.source = location    
    #
    #array
    fancy = (content_module.input_type == "mixed" or 
             getattr(content_module, "element_details", False))
    if fancy:
        new_question.build_custom_array(content_module.element_details,
                                        content_module.input_type,
                                        content_module.input_sub_type)            
    else:
        new_question.build_basic_array(content_module.input_type,
                                       content_module.input_sub_type,
                                       content_module.active_elements)
    #
    #condition 
    gating_element = getattr(content_module, "gating_element", False)
    if gating_element: 
        new_question.set_condition(gating_element)
    #
    #other attributes
    simple_attrs = ["array_caption",
                    "comment",
                    "basic_prompt",
                    "custom_prompt",
                    "short",
                    "transcribe"]
    for attr in simple_attrs:
        attr_val = getattr(content_module, attr, None)
        if attr_val:
            setattr(new_question, attr, attr_val)
        else:
            continue
    #
    # Check that the question configuration makes sense. Call will raise error
    # if routine encounters a problem.
    new_question.check()
    #
    #register the question in the catalog
    reverse_lookup_keys = [new_question.tags.name, location]
    catalog.register(new_question, *reverse_lookup_keys)
    #
    return new_question    
    
def populate():
    """


    populate() -> None


    Function walks the QuestionWarehouse and applies make_question() to every
    module that specifies ``question_content`` to be True. Function then marks
    local_catalog as populated.

    To avoid key collisions on parallel imports, populate() performs a no-op
    if catalog is already populated. 
    """
    if not local_catalog.populated:
        question_count = walk_package(Warehouse, "question_content", make_question)
        local_catalog.populated = True
        c = ""
        c += "QuestionManager successfully populated catalog with %s questions."
        c = c % question_count
        print(c)
    else:
        pass
        



