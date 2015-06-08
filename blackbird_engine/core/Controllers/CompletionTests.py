#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: Controllers.CompletionTests
"""

Module definesf functions that evaluate whether Blackbird has completed analysis
of a particular object based on that object's guide attributes. 
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
t_min_quality         returns True if obj's quality at least equals min standard
t_max_quality         returns True if obj's quality at least equals max standard
t_max_or_allowance    returns True if obj's quality is below lower of max or
                      attention allowance

CLASSES:
n/a
====================  ==========================================================
"""




#imports
#n/a




#globals
#n/a

#classes
#n/a

#functions
def t_min_quality(item):
    """


    t_min_quality(item) -> bool


    Expects item to have a properly configured ``guide`` attribute.

    Function returns True if item's current quality equals or exceeds its
    minimum quality standard. Also returns True if item.guide.selection records
    dry run (no matching topics).
    """
    result = False
    currentQ = item.guide.quality.current
    standard = item.guide.quality.minStandard
    if currentQ == None:
        result = False
    elif currentQ >= standard:
        result = True
    if item.guide.selection.finished_catalog:
        result = True
    return result

def t_max_quality(item):
    """


    t_max_quality(item) -> bool
    

    Function returns True if item's current quality equals or exceeds its
    maximum quality standard.

    Expects item to have a properly configured ``guide`` attribute.
    """
    result = False
    currentQ = item.guide.quality.current
    standard = item.guide.quality.maxStandard
    if currentQ == None:
        result = False
    elif currentQ >= standard:
        result = True

def t_max_or_allowance(item):
    """


    t_max_or_allowance(item) -> bool

    
    Function returns True if item's current quality equals or exceeds the
    lower of its maximum quality standard or its attention allowance.

    Expects item to have a properly configured ``guide`` attribute.
    """
    result = False
    currentQ = item.guide.quality.current
    if currentQ >= item.guide.quality.maxStandard:
        result = True
    elif currentQ >= item.guide.attention.allowance:
        result = True
    return result
