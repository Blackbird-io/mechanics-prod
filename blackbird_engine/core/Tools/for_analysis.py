#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Engine
#Module: DataStructures.Tools.ForManagers
"""

Module provides convenience functions for common content management tasks
handled by xManager modules (e.g., TopicManager, QuestionManager, etc.). 

====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
walk_package()        walk dir tree and apply action to modules that pass check

CLASSES:
n/a
====================  ==========================================================
"""




#imports
import operator



#globals
#n/a

#functions
def get_tagged_objects(pool, *tags):
    """
    returns a dict of objects by id

    pool must be an iterable container of objects
    returns a dict of matching objects by bbid

    #<----------------------------------compare to yenta methods
    #put doc strings in those methods
    """
    #make a set from tags
    criterion = set(tags)
    results = dict()
    for obj in pool:
        obj_profile = build_basic_profile(obj)
        missing = criterion - obj_profile
        if missing:
            continue
        else:
            try:
                k = obj.id.bbid
            except AttributeError:
                k = None
            v = results.setdefault(k, set())
            v.add(obj)
    
def get_product_names(model, question):
    pass
    ####should be in interview tools
   ##return a list of product names, top to bottom by size, that fits
   ##the input_element array; only runs when model is tagged "real names"



    
