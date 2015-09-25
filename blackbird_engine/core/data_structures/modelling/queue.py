#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: data_structures.modelling.queue
"""

Module defines Queue class, a list that automatically sorts AutoAlign objects.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
Queue                 list-type object that sorts collections of AutoAligns

====================  ==========================================================
"""




#imports
import copy
import BBExceptions

from BBGlobalVariables import *




#globals
#n/a

#classes
class Queue(list):
    """

    Queue objects are lists that can automatically sort certain objects.
    
    NOTE: changes to layout and relationships AutoAlign ordering attributes
    require ground-up revision of various Queue ordering algorithms.

    A queue is "aligned" if each item it contains is positioned such that the
    item's requirements for positioning are satisfied. It may be impossible to
    align lists of some items. For example, all items might stipulate that
    they should not go first. 

    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================
    DATA: 
    alignmentStages       dictionary of work in progress for sorting
    
    FUNCTIONS:
    checkAlignment()      checks for common conlict scenarios within instance
    alignItems()          reorders instance into longest aligned list + misfits
    canThisItemFit()      checks for common conflicts for new object
    ====================  ======================================================
    """
    def __init__(self):
        list.__init__(self)
        self.alignmentStages = {}

    def checkAlignment(self):
        """

        Queue.checkAlignment() -> tuple(bool,{})
        
        Method checks whether items in the queue all satisfy their AutoAlign
        conditions.
        
        One of four alignment errors can arise for a group of objects with
        AutoAlign attributes:
         (i)    No item in the queue is allowed to be first ("first position
                failure")
         (ii)   No item in the queue is allowed to be last ("last position
                failure")
         (iii)  Items other than the first must be first ("other first failure")
         (iv)   Items other than the last must be last ("other last failure")

        The method returns a tuple of the boolean result and a dictionary of
        any alignment problems it detects. bool is True if all items can be
        ordered in accordance with each item's active specifications (if any)
        without the occurence of any errors described above. bool is False
        otherwise. The dictionary provides keys for each of the problem types
        and bool values. 
        """
        #
        #UPGRADE-S: This really should run through exception logic
        #
        problem = {}
        problem["firstPositionFailure"] = False
        problem["lastPositionFailure"] = False
        problem["otherFirstsFailure"] = False
        problem["otherLastsFailure"] = False
        #if the item doesn't have an indicated attribute, assume it can go
        #anywhere. therefore intercept AttributeErrors and move on to the next
        #test
        if len(self) == 0:
            return (True,problem)
        try:
            if self[0].mustBeFirst != True and self[0].canBeFirst != True:
                problem["firstPositionFailure"] = True
        except AttributeError:
            pass
        try:
            if self[-1].mustBeLast != True and self[-1].canBeLast != True:
                problem["lastPositionFailure"] = True
        except AttributeError:
            pass
        #for tests of slices that may include more than one item, nest
        #exception handler in the loop to check all items
        for item in self[1:]:
            try:
                if item.mustBeFirst:
                    problem["otherFirstsFailure"] = True
            except AttributeError:
                continue   
        for item in self[:-1]:
            try:
                if item.mustBeLast:
                    problem["otherLastsFailure"] = True
            except AttributeError:
                continue
        if True in problem.values():
            #one of the Failures is real
            return (False, problem)
        else:
            #no Failure is real
            return (True, problem)      
      
    def alignItems(self):
        """

        Queue.alignItems([padToAlign = False,][trace= False]) -> []

        This method reorders items in an instance into the longest list that
        satisfies each item's autoAlign conditions. Method returns a list of
        items that do not fit into such a list. 

        Certain collections of items cannot be organized into any aligned queue.
        For example, if each item in a collection specifies that it cannot go
        first in a list, alignment is impossible. In such an event, alignItems()
        will return an empty queue and a misfits list that includes all of the
        objects in the instance.

        The method assumes most flexible state for missing attributes.
        The default for missing ``must`` attributes is therefore False and for
        ``can`` attributes it is True. E.g., if object.mustBeFirst does not
        exist, method assumes object does not have to go first.
        """
        alignedQueue = []
        misfits = []
        mandatoryLoners = []
        mandatoryFirsts = []
        optionalFirsts = []
        mandatoryLasts = []
        optionalLasts = []
        flexiblePosition = []
        middleOnly = []
        currentLength = len(self)
        #
        #legacy vars:
        padToAlign = False
        #If ``padToAlign`` is set to True, the method will try to avoid empty
        #queue solutions by adding None objects on either side of the list.
        #
        for item in self:
            #assume that unspecified positional attributes are False for
            #requirements (``must``) and True for options (``can``). E.g., if
            #obj.mustBeFirst is missing, object does NOT have to be first. 
            if getattr(item, "exclusivity", False):
                mandatoryLoners.append(item)
            elif getattr(item, "mustBeFirst", False):
                #item.exclusivity is not true, so at this point, know that only
                #one of must criteria is true
                mandatoryFirsts.append(item)
            elif getattr(item, "mustBeLast", False):
                mandatoryLasts.append(item)
            #at this point in the tree, the item does not specify any individual
            #positional requirements. item may still specify negative rules, ie,
            #``cannot be last, otherwise flexible``
            elif getattr(item, "canBeFirst", True):
                if getattr(item,"canBeLast",True):
                    flexiblePosition.append(item)
                else:
                    optionalFirsts.append(item)
            elif getattr(item, "canBeLast", True):
                optionalLasts.append(item)
                #``canBeFirst`` must be False here, otherwise item caught in
                #branch above
            else:
                middleOnly.append(item)
                #residual list
        if len(mandatoryLoners) >= 1:
            misfits = copy.copy(self)
            misfits.remove(mandatoryLoners[0])
            alignedQueue.append(mandatoryLoners[0])
            #if there is more than one item that must be exclusive, an aligned
            #Queue consists of the first exclusive item only. the  rest of the
            #items are misfits. 
        else:
            #the mandatoryLoners list contains 0 or 1 items and doesn't create
            #any conflicts on its own. if there is more than 1 item in any of
            #the other mandatory lists, a conflict exists. copy items #2 and
            #higher from the mandatory lists into the misfists list. 
            misfits.extend(mandatoryFirsts[1:])
            #slice avoids index error if list too short.
            if len(mandatoryFirsts) >= 1:
                #for first position, pick the first item that mustBeFirst
                #check for length of list first because a call to zero index on
                #an empty list returns an error
                alignedQueue.append(mandatoryFirsts[0])
                #alignedQueue is now at least 1 item long, so any items that
                #follow are not first
                alignedQueue.extend(optionalFirsts)
                alignedQueue.extend(middleOnly)
                alignedQueue.extend(flexiblePosition)
                alignedQueue.extend(optionalLasts)
                alignedQueue.extend(mandatoryLasts[:1])
                misfits.extend(mandatoryLasts[1:])
            elif len(optionalFirsts) >= 1:
                #if there are no items that mustBeFirst, pick the first item
                #that canBeFirst. items in optionalFirst cannot go last.  
                alignedQueue.extend(optionalFirsts)
                #alignedQueue is now at least 1 item long. 
                alignedQueue.extend(middleOnly)
                alignedQueue.extend(flexiblePosition)
                alignedQueue.extend(optionalLasts)
                alignedQueue.extend(mandatoryLasts[:1])
                misfits.extend(mandatoryLasts[1:])
            elif len(flexiblePosition) >= 1:
                #items in flexible position are eligible to go first
                alignedQueue.extend(flexiblePosition)
                #mustBeFirst and optionalFirst are known to be empty at this
                #point in the decision tree
                alignedQueue.extend(middleOnly)
                alignedQueue.extend(optionalLasts)
                alignedQueue.extend(mandatoryLasts[:1])
                misfits.extend(mandatoryLasts[1:])
            else:
                misfits.extend(middleOnly)
                misfits.extend(optionalLasts)
                misfits.extend(mandatoryLasts)
                #at this point in the decision tree, the only items in the
                #instance are ones that CANNOT go first (mandatoryFirsts,
                #optionalFirsts, and flexiblePosition are all empty)
        #queue now aligns in terms of forward-facing requirements, check reverse
        if len(alignedQueue) > 0:
            if getattr(alignedQueue[-1], "mustBeLast", False):
                pass
            elif getattr(alignedQueue[-1], "canBeLast", True):
                pass
            else:
                #no eligible last item, coherent queue cannot be constructed,
                #dump instance contents into misfits
                misfits.extend(alignedQueue)
                alignedQueue.clear()
        #check that the queue and misfits reconstruction did not generate any
        #new duplicate lineitems. a duplicate in the new world is something
        #that appears 2 or more times between misfits and alignedQueue. some
        #duplicate items may have existet in the instance originally, so need
        #to check that no new ones were added. 
##        existingDuplicates = copy.copy(self)
##        for item in set(self):
##            existingDuplicates.remove(item)
##            #removes first instance of every item from a copy of self
##        #now existingDuplicates contains only 2nd and on versions of every item
##        newDuplicates = misfits + alignedQueue
##        for item in set(misfits + alignedQueue):
##            newDuplicates.remove(item)
##            #remove the first instance of each unique item from the total
##            #universe
##        newDuplicatesCopy = newDuplicates[:]
##        for eD in existingDuplicates:
##            if eD in newDuplicatesCopy:
##                newDuplicatesCopy.remove(eD)
##            else:
##                continue
        #preserve state just in case        
        d1 = self.alignmentStages
##        d1["existingDuplicates"] = existingDuplicates
##        d1["newDuplicates"] = newDuplicates
        d1["alignedQueue"] = alignedQueue
        d1["misfits"] = misfits
        d1["mandatoryLoners"] = mandatoryLoners
        d1["mandatoryFirsts"] = mandatoryFirsts
        d1["optionalFirsts"] = optionalLasts
        d1["mandatoryLasts"] = mandatoryLasts
        d1["optionalLasts"] = optionalLasts
        d1["flexiblePosition"] = flexiblePosition
        d1["middleOnly"] = middleOnly
##        if newDuplicatesCopy != []:
##            comment = "Alignment seems to have created duplicates"
##            raise IOPMechanicalError(comment)
        #unless tracked into error, no duplication problems detected, queue
        #construction complete, replace instance contents w those currently
        #in alignedQueue and return misfits. 
        self.clear()
        self.extend(alignedQueue)
        return misfits

    def canThisItemFit(self, newItem):
        """

        Queue.canThisItemFit(newItem) -> bool
        
        Method checks if newItem will fit into the instance without violating
        mandatory ordering criteria of other items. Runs on ordered queues only.
        """
        if self.checkAlignment()[0] == False:
            comment = "Runs only on aligned queues."
            raise BBExceptions.StructureError(comment)
        if len(self) == 0:
            #if the Queue is empty, anything can fit
            return True
        elif len(self) > 0:
            if getattr(newItem,"exclusivity",False) == True:
                #if new item must be alone but queue is specified to have at
                #least 1 item in it
                return False
            elif (getattr(newItem,"autoAlign", False) == False and
                  not getattr(self[0],"exclusivity",False) == True):
                #autoAlign disabled on the item, order irrelevant, item can fit
                #anywhere. instance must align to get here, so if index 0 is not
                #exclusive, no other item is exclusive
                return True
            elif (f1(newItem,"mustBeFirst",False) == True and
                  f1(self[0],"mustBeFirst",False) == True):
                #both the new item and the first item in the instance have
                #specified that they must be first
                return False
            elif (f1(newItem,"mustBeLast",False) == True and
                  f1(self[-1],"mustBeLast", False) == True):
                #both the new item and the last item in the instance have
                #specified they must be last
                return False
            else:
                return True
