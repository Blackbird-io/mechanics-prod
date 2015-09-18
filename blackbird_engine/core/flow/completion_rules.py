#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: Controllers.completion_rules

"""

Module contains functions that evaluate whether Blackbird has completed work on
an object, based on that object's guide attributes.

All rules are completely stateless. 
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
check_quality()       True when quality is up to standard
check_quality_or_attention() True when quality is up to standard or attn is out

CLASSES:
n/a
====================  ==========================================================
"""




#imports
#n/a




#globals
def check_quality_only(item):
    """


    check_quality_only(item) -> bool


    Function returns True iff:
    (1) item quality is at or above item's own quality standard, or
    (2) item finished topic with catalog with no matches.

    Function marks complete = True on objects that pass and False on those that
    fail.
    """
    complete = False
    if item.guide.selection.finished_catalog:
        complete = True
    if not complete:
        standard = item.guide.quality.standard
        if item.guide.quality.current >= standard:
            complete = True    
    item.guide.complete = complete
    #
    return complete

def check_quality_or_attention(item):
    """


    check_quality_or_attention(item) -> bool


    Function returns True iff:
    (1) item quality is at or above item's own quality standard,
    (2) item attention spend is at or above item's own attention budget, or
    (3) item finished topic with catalog with no matches.

    Function marks complete = True on objects that pass and False on those that
    fail.
    """
    complete = False
    if item.guide.selection.finished_catalog:
        complete = True
    if not complete:
        quality_cap = item.guide.quality.standard
        attention_cap = item.guide.attention.budget
        #
        worked_out = False
        asked_out = False
        #
        if item.guide.quality.current >= quality_cap:
            worked_out = True
        if attention_cap:
            if item.guide.attention.current >= attention_cap:
                asked_out = True
        if any(worked_out, asked_out):
            complete = True
    #
    item.guide.complete = complete
    #
    return complete
