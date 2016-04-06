#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Engine
#Module: tools.parsing

"""

Module provides convenience functions for parsing user data. 
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
date_from_iso()       convert ``YYYY-MM-DD`` string into datetime.date object
seconds_from_iso()    convert ``YYYY-MM-DD`` string into seconds since Epoch

CLASSES:
n/a
====================  ==========================================================
"""




#imports
import copy
import datetime
import time

import bb_exceptions
from bb_settings import *




#globals
#n/a

#functions
def monthsToSeconds(months):
    secondsPerMonth = 365/12*24*60*60
    seconds = months * secondsPerMonth
    return seconds

def secondsToMonths(seconds):
    secondsPerMonth = 365/12*24*60*60
    months = seconds / secondsPerMonth
    return months    

##def locateByName(container,startingMark,endingMark):
##    """
##    iterates through container, returns tuple of locations
##    """
##    options = iter(container)
##    startMarkIndex = None
##    endMarkIndex = None
##    while startMarkIndex == None or endMarkIndex == None:
##        item = options.__next__()
##        #may raise an error if the bookmarks are not found before container is exhausted
##        #will raise error if iterating through list where items dont have a name attr
##        if item.name == BLACKBIRDSTAMP + startingMark:
##            startMarkIndex = container.index(item)
##        elif item.name == BLACKBIRDSTAMP + endingMark:
##            endMarkIndex = container.index(item)
##        else:
##            continue
##    return (startMarkIndex, endMarkIndex)
###NOTE: ABOVE FUNCTION IS NOT FLEXIBLE AND SHOULD BE REVISITED
####  DELETE WHEN TESTED <--------------------------------------------------------

def locateByTag(container, *targetTags):
    """
    returns index of first location of object that includes the target tag(s)
    """
    criteria = set(targetTags)
    location = None
    for item in container:
        if criteria.issubset(set(item.allTags)):
            location = container.index(item)
            break
        else:
            continue
    else:
        location = -1
    return location
##  DELETE WHEN TESTED <--------------------------------------------------------

def findByTag(container, *targetTags):
    """
    returns first object that includes the target tag(s)
    if no match found raises error
    """
    criteria = set()
    for tag in targetTags:
        criteria.add(tag.casefold())
    result = None
    for item in container:
        if criteria.issubset(set(item.allTags)):
            result = item
            break
        else:
            continue
    else:
        raise bb_exceptions.StructureError("no matching object found")
    return result

def excludeByTag(container, *badTags):
    """
    Method returns a shallow copy of the container and its contents, minus objects with bad tags. 
    badTags catchall picks up one or more specified bad tags by position.
    Works on list-type containers carrying tagged objects
    """
    WIP = copy.copy(container)
    #keep original objects in container cause need to return them
    #use slice of WIP because its length may change
    for item in WIP[:]:
        applicableBadTags = set(badTags) & set(item.allTags)
        #intersection between the item's tags and badtags
        if not applicableBadTags == set():
            #if any tags in badTags are also in item's tags
            WIP.remove(item)
    return WIP

def includeByTag(container, *goodTags):
    """
    Method returns a copy of the container with only objects carrying good tags
    Works on list-type containers carrying tagged objects
    """
    WIP = copy.copy(container)
    WIP.clear()
    #empty container
    #all ancillary container features preserved
    for item in container:
        if set(goodTags).issubset(item.allTags):
            WIP.append(item)
        else:
            continue
    return WIP

##def provideListOfNames(container, missing = "ATTRIBUTE ERROR!"):
##    result = []
##    for item in container:
##        result.append(missingAttributeCatcher(item,"name",missing))
##    return result
####  DELETE WHEN TESTED <--------------------------------------------------------
    
def padAndZip(*thingsToZip, padding = None, trace = False):
    """
    zips any number of iterables together
    returns a list with a length equal to the number of items in longest iterable
    the items in the list are tuples of the same-turn item in each iterable
    iterates through each item in thingsToZip
    if any one of those items runs out, inserts padding in its place
    if trace is True, returns a tuple of ([],[])
    l1 is a raw list, with frozen StopIteration() exceptions in place where an iterable ran out
    l2 is a padded list
    if trace is False, returns only the padded list
    """
    frozenE = StopIteration()
    rawZip = []
    allIters = [iter(x) for x in thingsToZip]
    def nextOrCaughtError(x):
        result = None
        try:
            result = next(x)
        except StopIteration as Y:
            result = Y
        finally:
            return result
    control = True
    while control:
        newItem = tuple(nextOrCaughtError(x) for x in allIters)
        for y in newItem:
            if y.__class__ != frozenE.__class__:
                #if any item in the new tuple is other than a stopiteration exception
                #ie if any thing in thingsToZip is still going
                #keep making new tuples
                rawZip.append(newItem)
                break
        else:
            #everything in the tuple is a stopiteration error
            #all things done
            control = False
    paddedZip = []
    for rawItem in rawZip:
        paddedItem = []
        for piece in rawItem:
            if piece.__class__ == frozenE.__class__:
                paddedItem.append(padding)
            else:
                paddedItem.append(piece)
        paddedZip.append(tuple(paddedItem))
    if trace:
        return (rawZip, paddedZip)
    else:
        return paddedZip

##def listAttributes(obj):
##    """
##    Function identifies the object's non-system attributes.
##    Returns a list of strings, each of which is an attribute name. 
##    """
##    allAttributes = dir(obj)
##    result = []
##    for attr in allAttributes:
##        if attr.startswith("__"):
##            continue
##        else:
##            result.append(attr)
##    return result

def stripCase(obj,attr = "allTags"):
    """
    returns a list of caseless equivalents for all items in obj.attr
    obj.attr must be iterable
    if attr is specified as None, function iterates through obj itself
    if an item cannot be casefolded, function will append original version of the item
    """
    caseLess = []
    if attr:
        material = getattr(obj,attr,None)
    else:
        material = obj
    for o in material:
        oLess = o
        try:
            oLess = o.casefold()
        except AttributeError:
            pass
        caseLess.append(oLess)
    return caseLess

def deCase(obj):
    """

    If the object supports casefolding, returns casefolded object; otherwise,
    returns the object without modification. 
    """
    result = obj
    try:
        cLess = obj.casefold()
        result = cLess
    except AttributeError:
        pass
    return result


def seconds_from_iso(string):
    """


    seconds_from_iso(string) -> float


    Function takes a string in "YYYY-MM-DD" format and returns a POSIX timestamp
    representing seconds since Epoch. Function ignores any whitespace around the
    POSIX data. 
    """
    calendar = date_from_iso(string)
    to_time = calendar.timetuple()
    result = time.mktime(to_time)
    #
    return result

def date_from_iso(string):
    """


    date_from_iso(string) -> datetime.date


    Function takes a string in "YYYY-MM-DD" format and returns an instance of
    datetime.date. Function ignores any whitespace around the POSIX data. 
    """
    elements = [int(x) for x in string.split("-")]
    result = datetime.date(*elements)
    #
    return result

def seconds_from_years(yrs):
    """


    seconds_from_years(yrs) -> int or float


    Function returns value corresponding to the number of seconds in ``yrs``,
    assuming a 365-day year.
    """
    result = yrs * 365 * 24 * 60 * 60
    return result

def walk(d):
    for k in sorted(d.keys()):
        yield d[k]

    
