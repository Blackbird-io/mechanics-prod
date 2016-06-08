#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Engine
#Module: tools.for_tag_operations

"""

Module includes convenience functions for identifying objects based on the tags
they carry. 
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
build_basic_profile() return a set of target tags, used as simple criteria
build_combo_profile() return a set of tags from target and model
get_tagged()          return objects from container that have specified tags

CLASSES:
n/a
====================  ==========================================================
"""




#imports
# n/a




#globals
#n/a

#functions
def build_basic_profile(target):
    """


    build_basic_profile(target) -> set()


    Return set of all tags on target, with None stripped out. 
    """
    try:
        criteria = set(target.tags.all)
    except AttributeError:
        raise
    criteria = criteria - {None}
    #
    return criteria

def build_combo_profile(target, model):
    """


    build_combo_criteria(target, model) -> set()


    Return the set of all tags found on target, target's parent, target's
    grandparent, and the model.

    When target is a LineItem, target's parent will usually be a line or a
    Financials object and its grandparent will usually be a line, Financials
    object, or a BusinessUnit. 
    """
    #
    parent_rels = getattr(target, "relationships", None)
    if parent_rels:
        parent = getattr(parent_rels, "parent")
    else:
        parent = None

    grandpa_rels = getattr(parent, "relationships", None)
    if grandpa_rels:
        grandpa = getattr(grandpa_rels, "parent")
    else:
        grandpa = None

    parent_tags = getattr(parent, "tags", None)
    tags_up_one = getattr(parent_tags, "all", [])

    grandpa_tags = getattr(grandpa, "tags", None)
    tags_up_two = getattr(grandpa_tags, "all", [])

    try:
        criteria = set(target.tags.all)
    except AttributeError:
        raise

    criteria = criteria | set(tags_up_one) | set(tags_up_two)
    criteria = criteria | set(model.tags.all)
    criteria = criteria - {None}
    #
    return criteria

def get_tagged(container, *tags, catch_blank_ids = True):
    """


    get_tagged(container, *tags) -> dict()
    

    Return an {bbid:obj} dict of objects that have each of the specified tags.

    Container must be an iterable. If ``catch_blank_ids`` is True, function will
    store all matching objects that are missing a bbid in a set at the None key. 

    NOTE: Function evaluates ``tags`` as a set, so it will not differentiate
    between objects that carry that tag once and those that do so more than
    once. 
    """
    criterion = set(tags)
    result = dict()
    for obj in container:
        obj_profile = build_basic_profile(obj)
        missing = criterion - obj_profile
        if missing:
            continue
        else:
            try:
                k = obj.id.bbid
                result[k] = obj
            except AttributeError:
                #easier to catch missing error than two layers of getattr
                #or use some inspect function.
                if catch_blank_ids:
                    blanks = result.setdefault(None, set())
                    #if None is already a key, pull its set, otherwise add None
                    #as a key with an empty set
                    blanks.add(obj)
    #
    return result
    
def get_product_names(model, question):
    pass
    ####should be in interview tools
   ##return a list of product names, top to bottom by size, that fits
   ##the input_element array; only runs when model is tagged "real names"
