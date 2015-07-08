#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: Controllers.selection_rules

"""

Module contains functions that select a focal point object from a pool of peers.
All rules are completely stateless. 
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
for_attentive_breadth spreads available attention between highest priority objs
for_attentive_depth   cuts off work when no more attention left
for_quality           picks first object that needs work

CLASSES:
n/a
====================  ==========================================================
"""




#imports
#n/a




#globals
def for_attentive_breadth(level, model):
    """


    for_attentive_breadth(level, model) -> fp


    **attention-sensitive routine**
    
    Function selects a focal point from level.
    Function returns ``None`` when all items in level are complete.

    Function sets the interview completion rule to ``quality_and_attention``.

    Function imposes attention rationing if the total quality need for the
    level exceeds the remaining attention budget for the model. Function
    computes quality need as the difference between an object's quality
    standard and existing quality.

    Function assumes that one unit of attention is comparable to one unit of
    quality. 

    When attention requirements exceed availability, function splits available
    attention ratably between level items that still need work. Function sets
    this attention budget on each item.
    
    Function applies the completion rule to each object in level, starting at
    the level.last position. Function stops as soon as it finds an object that
    fails the rule. Function marks complete = True on all objects that pass.
    """
    fp = None
    rule = completion_rules.quality_and_attention
    model.interview.set_completion_rule(rule)
    #
    remaining = range(level.last, len(level))
    #
    a_budget = model.interview.attention.budget
    a_current = model.interview.attention.current
    a_allowance = a_budget - a_current
    a_allowance = max(0, a_allowance)
    #allowance must be greater than or equal to zero
    #
    total_need = 0
    for i in remaining:
        item = level[i]
        q_standard = item.guide.quality.standard
        q_current = item.guide.quality.current
        item_need = q_standard - q_current
        item_need = max(0, item_need)
        #positive need only
        total_need += item_need
    #
    rationing = False
    attention_cap = None
    if total_need > available_attention:
        rationing = True
        attention_cap = available_attention / len(remaining)
    #
    for i in remaining:
        item = level[i]
        item.guide.attention.budget = attention_cap
        #cap is None unless necessary to ration
        #
        if rule(item):
            #work on item is complete
            item.guide.complete = True
            continue
        else:
            #
            item.guide.complete = False
            fp = item
            level.last = i
            break
    #
    return fp

def for_attentive_depth(level, model):
    """


    for_attentive_depth(level, model) -> fp


    **attention-sensitive routine**
    
    Function selects a focal point from level.
    Function returns ``None`` when all items in level are complete.

    Function will skip rule analysis and return None when model is out of
    attention. Otherwise, function will delegate work to for_quality.
    """
    #
    #run quality selection as usual, stop when run out of attention
    #
    fp = None
    #
    remaining = range(level.last, len(level))
    #
    a_budget = model.interview.attention.budget
    a_current = model.interview.attention.current
    a_available = a_budget - a_current
    a_available = max(0, a_allowance)
    #allowance must be greater than or equal to zero
    if a_available:
        fp = for_quality(level, model)
    else:
        #no op if out of attention, keep fp blank
        pass
    #
    return fp

def for_quality(level, model):
    """


    for_quality(level, model) -> fp

    
    Function selects a focal point from level.
    Function returns ``None`` when all items in level are complete.

    Function sets the interview completion rule to ``quality_only``. 

    Function applies the completion rule to each object in level, starting at
    the level.last position. Function stops as soon as it finds an object that
    fails the rule. Function marks complete = True on all objects that pass. 
    """
    fp = None
    #
    rule = completion_rules.quality_only
    model.interview.set_completion_rule(rule)
    #
    remaining = range(level.last, len(level))
    for i in remaining:
        item = level[i]
        if rule(item):
            item.guide.complete = True
            continue
        else:
            #if item is not complete
            item.guide.complete = False
            fp = item
            level.last = i
            break
    #
    return fp
