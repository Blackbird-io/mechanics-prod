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
test_MinComplete      returns True if obj's quality at least equals min standard
test_MaxComplete      returns True if obj's quality at least equals max standard
test_MaxOrAllowance   returns True if obj's quality is below lower of max or
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
def test_MinComplete(item):
    """


    test_MinComplete(item) -> bool


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

def test_MaxComplete(item):
    """


    test_MaxComplete(item) -> bool
    

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

def test_MaxOrAllowance(item):
    """


    test_MaxOrAllowance(item) -> bool

    
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
