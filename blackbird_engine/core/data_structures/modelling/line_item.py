#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: data_structures.modelling.line_item
"""

Module defines LineItem class. 
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
LineItem              storage for numerical values and tags
====================  ==========================================================
"""




#imports
import copy
import time

import BBExceptions
import BBGlobalVariables as Globals

from data_structures.guidance.guide import Guide
from data_structures.system.tags import Tags
from data_structures.system.print_as_line import PrintAsLine

from .equalities import Equalities




#globals
#n/a

#classes
class LineItem(PrintAsLine, Tags, Equalities):
    """
    Instances of this class become components of a BusinessUnit.Financials list.

    A lineitem's value should be specified through setValue(). setValue()
    requires a signature. Values specified at instance construction get signed
    by LineItem.__init__(). Some methods may decline to sign a lineitem. 

    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    _sign                 instance-level state for sign
    _value                instance-level state for value
    formatted             ``[name] ... [value]`` string for pretty printing
    guide                 instance of Guide object
    irrelevantAttributes  list, CLASS, attributes Eq.__eq__ always skips
    keyAttributes         list, CLASS, parameters for comparison by Equalities
    modifiedBy            list of (signature,time,value) tuples
    sign                  int, dynamic, 0 or 1
    skipPrefixes          list, Eq.__eq__ also skips attributes w these 
    value                 float, dynamic
    
    FUNCTIONS:
    __hash__              returns name if specified, otherwise allTags
    clear()               if modification permitted, sets value to None
    copy()                returns a new line w copies of key attributes
    class dyn_SignManager descriptor for sign
    class dyn_ValManager  descriptor for value
    extrapolate_to()      delegates to Tags.extrapolate_to()
    ex_to_default()       returns a Line.copy() of self w target parentObject
    ex_to_special()       delegates to Tags.ex_to_special()
    pre_format()          make the ``formatted`` string
    replicate()           make a copy and fix line name
    setValue()            sets value to input, records signature
    toggleSign()          change sign to 0 or 1
    ====================  ======================================================
    """
    #adjust Equalities parameters (name is requiredTags[0]):
    keyAttributes = ["value","sign","requiredTags","optionalTags"]

##
##    LineItem object currently runs on defined (``keyAttribute``) comparisons;
##    if using comprehensive attribute comparisons instead, make sure to specify
##    parentObject as an irrelevantAttribute. Otherwise, comparisons will loop:
##    the parentObj may itself have an __eq__ method that points back to this
##    lineItem. See Equalities docs for more info.
    
    def __init__(self, name = None, value = None):
        PrintAsLine.__init__(self)
        Tags.__init__(self, name)
        self._value = None
        self._sign = 1
        self.guide = Guide()
        self.modifiedBy = []
        if value != None:
            #BU.consolidate() will NOT increment items with value==None. On the
            #other hand, BU.consolidate() will increment items with value == 0.
            #Once consolidate() changes a lineitem, derive() will skip it. To
            #allow derivation of empty lineitems, must start w value==None.
            isig = Globals.signatures["LineItem.__init__"]
            self.setValue(value, isig)
    
    def __hash__(self):
        HH = self.name
        if not HH:
            HH = self.allTags
        return HH
        #most loose/simple: by name
            #but then will pull out wrong lineitems out of a dictionary
            #ie wrong values, etc.
            #will pull out lines that do NOT compare equal
            #may be useful for BU.drivers for direct registry
            #kind of like saying a Ford Taurus is a Ford Taurus, but may differ
            #in mileage, condition, color, etc.
        #or tighter: same as equal criteria?
 
    class dyn_ValManager:
        """

        Desciptor for LineItem.value class attribute.
        Returns value with the right sign.
        Prevents direct write access.
        """
        def __get__(self,instance,owner):
            if instance._value == None:
                return instance._value
            else:
                return instance._value * instance.sign

        def __set__(self,instance,value):
            c1 = "Direct write prohibited. ``value`` is a managed attribute."
            c2 = "Use setValue() to change."
            c = c1 + c2
            raise BBExceptions.ManagedAttributeError(c)

    #value is a managed class attribute    
    value = dyn_ValManager()

    class dyn_SignManager:
        """

        Descriptor for LineItem.sign manager.
        Routes gets to instance._sign.
        Prohibits direct write access.
        """
        def __get__(self,instance,owner):
            return instance._sign

        def __set__(self,instance,value):
            c1 = "Direct write prohibited. ``sign`` is a managed attribute."
            c2 = "Use toggleSign() method to change."
            c = c1 + c2
            raise BBExceptions.ManagedAttributeError(c)

    #sign is a managed class attribute    
    sign = dyn_SignManager()
    
    def clear(self):
        """


        L.clear() -> None


        Method sets self.value to None by running L.setValue() with the value
        override. Method also sets the instance's sign to positive.

        NOTE: Method is a no-op for instances that do not pass checkTouch()
        Tags.checkTouch() returns False if the instance has tags that completely
        prohibit modification.
        """
        sig = Globals.signatures["LineItem.clear"]
        if self.checkTouch():
            self.setValue(None,sig,overrideValueManagement=True)
            self.toggleSign(1)
            
    def copy(self, enforce_rules = True):
        """


        LineItem.copy(self[, enforce_rules = True]) -> LineItem


        Method returns a copy of the instance. Uses Tags.copy() to generate a
        shallow copy with independent tags objects. If enforce_rules is True,
        copy conforms to ``out`` rules.
        """
        newLine = Tags.copy(self,enforce_rules)
        newLine._value = copy.copy(self._value)
        newLine._sign = copy.copy(self._sign)
        newLine.guide = copy.deepcopy(self.guide)
        newLine.modifiedBy = self.modifiedBy[:]
        return newLine

    def extrapolate_to(self,target):
        """


        LineItem.extrapolate_to(target) -> LineItem


        Method extrapolates instance characteristics to target and returns a
        new object that combines both.

        NOTE: Method delegates all work to Tags.extrapolate_to (standard
        subroutine selection logic).
        """
        result = Tags.extrapolate_to(self,target)
        return result

    def ex_to_default(self,target):
        """


        LineItem.ex_to_default(target) -> LineItem


        Method creates a LineItem.copy() of instance. Method signs copy with
        extrapolation signature if copy.modifiedBy() doesn't already end with
        one.

        Copy continues to point to seed parentObject.
        """
        #basic behavior: copy instance, set to seed.parentObject, if any
        result = self.copy(enforce_rules = True)
        ex_d_sig = Globals.signatures["LineItem.ex_to_default"]
        if ex_d_sig not in result.modifiedBy[-1]:
            r_val = result.value
            result.setValue(r_val,ex_d_sig)
        return result

    def ex_to_special(self,target):
        """


        LineItem.ex_to_special() -> LineItem


        Method delegates all work to Tags.ex_to_special.

        Special extrapolation for LineItems returns a LineItem.copy of seed
        updated with new tags from the target. Method signs the result unless
        modifiedBy already ends with its signature.
        """
        result = Tags.ex_to_special(self,target)
        ex_s_sig = Globals.signatures["LineItem.ex_to_special"]
        if ex_s_sig not in result.modifiedBy[-1]:
            r_val = result.value
            result.setValue(r_val,ex_s_sig)
        return result        

    def replicate(self, compIndex=None, fixName=True):
        """


        LineItem.replicate() -> LineItem

        
        Method returns a copy of line instance.

        Method can be used to create named copies of unnamed line items during
        business unit consolidation. If ``fixName`` is True, method will create
        a name for unnamed instances and tag the returned copy (but not the
        source instance) accordingly. ``compIndex`` is the list position of the
        source business unit in its parent's components list. Method will
        combine a string showing the line came from bu #[compIndex] with the
        first three optional tags on the line.        
        """
        replica = LineItem.copy(self, enforce_rules = False)
        #NOTE: the original copy should be a true copy (ie without tag
        #substitution via rules enforcement). Goal is to preserve tags like
        #"hardcoded" or "do not touch". If enforce_rules is True, "do not touch"
        #would not transfer to the replica because the copy counts as an "out"
        #move. Then, if the original value was to somehow get reset to None,
        #the lineitem could get behind and the entire financials unit could lose
        #a special processing trigger.
        if fixName and replica.name is None:
            newName = "Unnamed Line (C%s): " % compIndex
            sep = "; "
            optTags = sep.join(line.optionalTags[:3])
            newName = newName + optTags
            replica.setName(newName)
        return replica
      
    def setValue(self, newValue, driverSignature, declineSignature = False,
                 overrideValueManagement = False):
        """


        L.setValue(newValue,driverSignature[,declineSignature = False
        [,overrideValueManagement = False]]) -> None


        Method sets line value. If the specified value is less than 0, method
        sets instance._value to abs(newValue) and adjusts the instance sign to
        -1. Method raises an error if the newValue is non-numeric unless
        ``overrideValueManagement`` is set to True
        
        Method records each valid call to instance.modifiedBy list unless
        ``declineSignature`` is set to True. Method does not record failed
        attempts.        
        """
        try:
            if newValue < 0:
                self.toggleSign(-1)
                newValue = abs(newValue)
            else:
                self.toggleSign(1)
            self._value = newValue
            if not declineSignature:
                self.modifiedBy.append((driverSignature, time.time(),
                                        newValue))
        except TypeError:
            if overrideValueManagement:
                self._value = newValue
                if not declineSignature:
                    self.modifiedBy.append((driverSignature, time.time(),
                                            newValue))
            else:
                label = "LineItem value must be numeric"
                raise BBExceptions.ValueFormatError(label)
            
    
    def toggleSign(self,newSign = None):
        """

        
        LineItem.toggleSign([newSign = None]) -> None


        Method sets instance._sign. Accepts values of either 1 or -1. If no sign
        specified on call, will flip the existing sign value to its negative.
        """
        if newSign == None:
            self._sign = self.sign * -1
        elif newSign == 1 or newSign == -1:
            self._sign = newSign
        else:
            c = "sign must be -1 or 1"
            raise BBExceptions.ValueFormatError(c)


