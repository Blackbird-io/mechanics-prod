#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: data_structures.valuation.pattern
"""

Module that defines the Pattern class, which combines fixed-order, keys, and
some LineItem attributes.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
Pattern               general architecture for ordered dict-style objects
====================  ==========================================================
"""




#imports
import time
import copy

import bb_exceptions

from data_structures.modelling.line_item import LineItem




#globals
#n/a

#classes
class Pattern(dict, LineItem):
    """

    The Pattern class provides object storage. Pattern instances provide:
    
    -- a fixed-order perspective on contents via .ordered attribute
    -- high speed access through keys
    -- most substantive LineItem attributes

    To maintain a common interface among Financials and Valuation objects, the
    Pattern class descends from ModelComponents.LineItem. Instances of Pattern
    have a lot fewer constraints than a LineItem, so the class then modifies
    a number of LineItem methods to make them more flexible. The Pattern class
    excludes LineItem attributes that do not make sense for an object without
    value constraints. 

    NOTE: Pattern instances run standard dict-class .__eq__ logic on comparisons

    NOTE2: Pattern is hashable through name and tags, via LineItem.__hash__
    Standard dictionary objects are not hashable because they are mutable, but a
    Pattern instance is supposed to have a more consistent, predictable
    composition than a normal dictionary. So a Pattern instance covering
    enterprise value for Business A would hash as the same as another instance
    covering enterprise value for Business B. In other words, the instances
    would look like the same "sort" of thing. Pattern A == Patern B would still
    return False unless they had identical components, however. 
    
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    dynamicOrdered        descriptor for assembling self.ordered w updated vals
    log                   list of tuples (attrName, time.time(),obj)
    o_keys                static list of keys for ordered view
    ordered               dynamic list of values associated w function keys
    trackChanges          bool, toggles whether changeElement records to log
    
    FUNCTIONS:
    addElement()          adds a key:val item to self and ordered
    applyStandard()       sets each key to a deepcopy of standard value
    changeElement()       replaces the val for a given key in self and ordered
    fromkeys()            adds each key in object to self with default values
    setValue()            calls LineItem.setValue, override value mgmt
    resetValue()          sets self.value to None
    resetLog()            sets self.log to empty list
    ====================  ======================================================
    """

    def __init__(self,name = None,value = None):
        dict.__init__(self)
        LineItem.__init__(self,name)
##        self._o_functions = []
        self.o_keys = []
        self.setValue(value,"__init__") #<--------------------------------------------------------------------------------------------------------------------------------------------------- conform to sig policy
        self.log = []
        self.trackChanges = False
        
#remove unnecessary attributes
##    del toggleSign
##    del dynamicValueManager
##    del dynamicSignManager
##    del sign
##    del _sign
        
    def __eq__(self,comparator):
        return dict.__eq__(self,comparator)

    def __setattr__(self,attrName,attrVal):
        if attrName in self.keys():
            self.changeElement(attrName,attrVal)
        else:
            object.__setattr__(self,attrName,attrVal)

    def addElement(self,attrName,obj):
        """

        Pattern.addItem(attrName,obj) -> None

        Method:
        1) sets instance[attrName] to obj
        2) sets instance.attrName to obj
        3) sets obj.tags.parentObject to self
        4) appends a function to self._o_functions that always returns
        self[attrName]

        NOTE: repeatedly adding the same element will mean that it appears more
        than once in self.ordered

        NOTE2: _o_functions each have a ``key`` attribute that shows the key
        they get in self. 
        """
        self[attrName] = obj
        setattr(self,attrName,obj)
        try:
            obj.setPartOf(self)
        except Exception:
            pass
        self.o_keys.append(attrName)
        
    def applyStandard(self,standard_value):
        """

        Pattern.applyStandard(standard_value) -> None

        Method sets each key in self to a **deepcopy** of the standard_value
        argument.
        """
        keys = list(self.keys())[:]
        #use a slice as insurance in case the content-setting logic below somehow
        #changes key order while working (possible if Pattern.changeElement()
        #revised in the future).
        for k in keys:
            content = copy.deepcopy(standard_value)
            self.changeElement(k,content)

    def changeElement(self,attrName,obj):
        """

        Pattern.changeElement(attrName,obj) -> None

        If attrName in instance.keys(), method changes the value of the attrName
        key to obj and changes self.attrName to obj. Otherwise (if attrName is
        not an existing key), method raises KeyError.

        If instance.trackChanges is true, method appends a new entry in the form
        of 3-tuple (attrName, time.time(),obj) to instance.log.
        """
        if attrName in self.keys():
            self[attrName] = obj
            object.__setattr__(self,attrName,obj)
            if self.trackChanges:
                logEntry = (attrName,time.time(),obj)
                self.log.append(logEntry)
        else:
            label = "attrName not in self.keys()"
            raise KeyError(label)
            #exception consistent w missing keys

    class dynamicOrdered:
        """

        Descriptor that assembles an ordered list of instance contents

        ====================  ======================================================
        Attribute             Description
        ====================  ======================================================

        DATA:
        target                name of target attribute ("ordered" or "o_keys")

        FUNCTIONS:
        __get__               calls every o_func in order, returns a list of results               
        __set__               raises bb_exceptions.ManagedAttributeError
        __del__               raises bb_exceptions.ManagedAttributeError
        ====================  ======================================================
        """
        def __init__(self,attr):
            self.target = attr
            
        def __get__(self,instance,owner):
            fresh = []
            for k in instance.o_keys:
                try:
                    obj = instance[k]
                except KeyError:
                    #cant call the item
                    obj = k
                fresh.append(obj)
            return fresh
        
        def __set__(self,instance,value):
            label = "Managed attribute, direct write prohibited"
            raise bb_exceptions.ManagedAttributeError(label)

        def __del__(self,instance):
            label = "Managed attribute, deletion prohibited"
            raise bb_exceptions.ManagedAttributeError(label)

    ordered = dynamicOrdered("ordered")

    def fromkeys(self,obj,defaultValue=None):
        """

        Pattern.fromkeys(obj[,defaultValue = None]) -> Pattern

        Method populates instance with keys from obj. Each value is set to the
        **actual** object provided as defaultValue. To create independent copies
        of the default value, run fromkeys() and then applyStandard().

        ``obj`` should be iterable. Method returns the filled in instance. 
        """
        for field in obj:
            self.addElement(field,defaultValue)
        return self

    def resetLog(self):
        self.log = []
    
    def resetValue(self):
        """

        Pattern.resetValue() -> None

        Method sets instance value to None
        """
        self.setValue(None,"resetValue()")
        #<-------------------------------------------------------------------------------------------------------------------------------------------------------------need signature mgmt
        
    def setValue(self, newValue, driverSignature):
        """

        Pattern.setValue() -> None
                
        Method delegates to LineItem.setValue() with value management
        suppressed. 
        """
        LineItem.set_value(self, newValue, driverSignature, override=True)

