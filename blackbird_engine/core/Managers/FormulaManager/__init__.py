#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Engine
#Module: FormulaManager.__init__
"""

Module builds and administers a catalog of formulas from content modules in
FormulaWarehouse.

The Modelling.Driver module imports FormulaManager and populates the catalog.
From there, FormulaManager primarily serves Driver operations. The
FormulaManager serves a secondary, supporting role for TopicManager, where
FormulaManager delivers actual Formula objects that Topics can use in the
drivers they create. 

====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
catalog               instance of Platform.Catalog;by_name also keyed by func
id                    instance of Platform.ID; bbid set to "FormulaManager"

FUNCTIONS:
make_formula()        create a Formula object from a content module
populate()            create and record all Topics in TopicWarehouse in catalog               

CLASSES:
n/a
====================  ==========================================================
"""





#imports
import BBExceptions

from data_structures.system.catalog import Catalog
from data_structures.system.bbid import ID
from data_structures.modelling.formula import Formula
from tools.for_managers import walk_package

from . import FormulaWarehouse as Warehouse





#globals
local_catalog = Catalog()
id = ID()
id.assignBBID("FormulaManager")

#functions
def make_formula(content_module, catalog = local_catalog):
    """


    make_formula(content_module) -> Formula


    Method starts with a clean Formula instance. Module then:
     -- names and tags the formula with per content spec
     -- assigns the formula an id within the FormulaManager namespace_id
     -- adds the formula function from the content module.
     -- adds the required_data list from the content module.
     
    Method concludes by registering formula in catalog under its name and
    function object.     
    """
    formula = Formula()
    #
    if not content_module.name:
        c = "Cannot add nameless formulas to catalog."
        raise BBExceptions.CatalogError(c)
    formula.tags.setName(content_module.name)
    formula.id.setNID(id.namespace_id)
    formula.id.assignBBID(formula.tags.name)
    formula.func = content_module.func
    if not formula.func:
        c = "Content module %s does not define a valid formula."
        c = c % formula.tags.name
        raise BBExceptions.CatalogError(c)
    #
    formula.required_data = content_module.required_data
    reverse_keys = [formula.tags.name, formula]
    catalog.register(formula, *reverse_keys)
    return formula
    
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
        formula_count = walk_package(Warehouse, "formula_content", make_formula)
        local_catalog.populated = True
        c = ""
        c += "FormulaManager successfully populated catalog with %s formulas."
        c = c % formula_count
        print(c)
    else:
        pass
    
    

    


