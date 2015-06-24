#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Engine
#Module: DataStructures.Tools.Parsing
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

import BBExceptions
from BBGlobalVariables import *




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

##def monthStartTime(currentTime):
##    """
##    Returns the UTC time for the first day of the month that the currentTime occurs in.
##    Specifically, returns the time in seconds for the second after midnight on Day 1 of the month.
##    """
##    #gives you a time.struct_time object that's iterable
##    currentTimeTuple = time.localtime(currentTime)
##    #gives you a list of items in the current time tuple, so you can change them
##    currentTimeList = [x for x in currentTimeTuple]
##    #gives you a copy of the currentTimeList to work on
##    currentMonthStartList = copy.deepcopy(currentTimeList)
##    #month starts when the date is equal to 1
##    currentMonthStartList[2] = 1
##    #set hour, min, and seconds to 0
##    #by zeroing out currentMonthStartList[3:6]
##    for i in range(len(currentMonthStartList)):
##        if i>=3 and i<6:
##            currentMonthStartList[i] = 0
##    #now currentMonthStartList should look like: [yy, mm, 1, 0, 0, 0, ?, ?]
##    #last two items in the list are the day in the year and DST variables
##    #let library conform those as necessary
##    currentMonthStartTuple = time.struct_time(currentMonthStartList)
##    #turn the struct into a seconds to make incrementation easier
##    currentMonthStartSeconds = time.mktime(currentMonthStartTuple)
##    return currentMonthStartSeconds
##
##  DELETE WHEN TESTED <--------------------------------------------------------

##def missingAttributeCatcher(obj,attr,plug):
##    """
##    A function for returning default values in event that an attribute is missing.
##    The function attempts to run getattr(obj,attr).
##    If an AttributeError arises, returns plug.
##
##    NOTE: getattr requires that the desired attribute name be specified as a string.
##    """
##    try:
##        return getattr(obj,attr)
##    except AttributeError:
##        return plug
##
##  DELETE WHEN TESTED <--------------------------------------------------------

##def valueReplacer(test,plug,*badValues):
##    result = test
##    if result in badValues:
##        result = plug
##    return result
##
##  DELETE WHEN TESTED <--------------------------------------------------------

##
##def checkNameIntegrity(containerObject, nameDictionary = None, returnAll = False):
##    """
##    A function for checking whether items in a container share names.
##    Returns a tuple of (bool, {1}, {2}), where:
##        -- bool is True if no items share a name other than None, and False otherwise
##        -- {1} is a dictionary of items with duplicative names in the format of [item.name]:[item1,...]
##        -- {2} is a dictionary of all item names for the container in the format of [item.name]:[item1,...]
##    Function uses the missingAttributeCatcher exception handler to classify items without a .name as having name = None.
##    Function returns True even if more than one item in the container has a None name.
##    
##    User can provide a pre-built name dictionary for the container to increase speed.
##
##    Setting returnAll to True ensures return of the three-item tuple above.
##    Setting returnAll to False returns a two item tuple (bool, {1})
##    """
##    allNames = {}
##    if nameDictionary:
##        allNames = nameDictionary
##    status = True
##    duplicateNames = {}
##    f1 = missingAttributeCatcher
##    for item in containerObject:
##        nameOrNone = f1(item,"name",None)
##        if nameOrNone in allNames.keys():
##            allNames[nameOrNone].append(item)
##            if nameOrNone != None and len(allNames[nameOrNone]) >= 2:
##                status = False
##                duplicateNames[item.name] = allNames[item.name]
##                #ok to call item.name above because block only trigerred if nameOrNone is not None
##                #that is, item.name did not generate an attribute error
##        else:
##            allNames[nameOrNone] = [item]
##    if returnAll:
##        return (status, duplicateNames, allNames)
##    else:
##        return (status, duplicateNames)
##
##  DELETE WHEN TESTED <--------------------------------------------------------


def locateByName(container,startingMark,endingMark):
    """
    iterates through container, returns tuple of locations
    """
    options = iter(container)
    startMarkIndex = None
    endMarkIndex = None
    while startMarkIndex == None or endMarkIndex == None:
        item = options.__next__()
        #may raise an error if the bookmarks are not found before container is exhausted
        #will raise error if iterating through list where items dont have a name attr
        if item.name == BLACKBIRDSTAMP + startingMark:
            startMarkIndex = container.index(item)
        elif item.name == BLACKBIRDSTAMP + endingMark:
            endMarkIndex = container.index(item)
        else:
            continue
    return (startMarkIndex, endMarkIndex)
#NOTE: ABOVE FUNCTION IS NOT FLEXIBLE AND SHOULD BE REVISITED
##  DELETE WHEN TESTED <--------------------------------------------------------

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
        raise BBExceptions.StructureError("no matching object found")
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

def provideListOfNames(container, missing = "ATTRIBUTE ERROR!"):
    result = []
    for item in container:
        result.append(missingAttributeCatcher(item,"name",missing))
    return result
##  DELETE WHEN TESTED <--------------------------------------------------------
    
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

def listAttributes(obj):
    """
    Function identifies the object's non-system attributes.
    Returns a list of strings, each of which is an attribute name. 
    """
    allAttributes = dir(obj)
    result = []
    for attr in allAttributes:
        if attr.startswith("__"):
            continue
        else:
            result.append(attr)
    return result

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
    
