#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: Controllers.PriorityLevel
"""

Module defines PriorityLevel class. Instances of PriorityLevel hold items of
comparable importance to a given analysis. These objects also provide methods
to quickly estimate how much effort the user will have to put in to finish all
of the items in the container. 
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
class PriorityLevel   list subclass with annotation attributes
====================  ==========================================================
"""




#imports
#n/a




#globals
#n/a

#classes
class PriorityLevel(list):
    """

    Container object (subclass of list) that provides for storage and annotation.
    Supports all built-in list operations.

    Provides several analytical methods that enable common tasks. Generally,
    these methods require that all items in self have a ``guide`` attribute with
    a properly configured Guide object.

    Object also provides state-retention attributes that track major milestones
    in focus selection. 
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    finished              bool, has analysis completed on all items in this
                          level; definition of 'complete' intentionally left
                          open to interpretation / external control
    iLastTouched          index of item last processed
    projCost_MaxComplete  attention need to get all items to max complete
    projCost_MinComplete  attention need to get all items to min complete
    spendToDate           total attention expended on all items to date
    started               bool, has analysis started on any items in this level

    METHODS:
    checkAll()            check if all items satisfy some function F
    checkMaxComplete()    checks if all items are max complete
    checkMinComplete()    checks if all items are min complete
    sumAll()              return cumulative output of function F for each item
    getCostToMax()        estimate attention to get all items to max complete
    getCostToMin()        estimate attention to get all items to min complete
    getSpendToDate()      return sum of current attention for all items
    reset()               revert to defaults for annotation attributes    
    ====================  ======================================================
    """
    def __init__(self):
        list.__init__(self)
        self.started = False
        self.finished = False
        self.iLastTouched = None
        self.spendToDate = None
        self.projCost_MinComplete = None
        self.projCost_MaxComplete = None

    def reset(self):
        """


        PL.reset() -> None


        Method restores default values for attributes.
        """
        self.started = False
        self.finished = False
        self.iLastTouched = None
        self.spendToDate = None
        self.projCost_MinComplete = None
        self.projCost_MaxComplete = None

    def checkMinComplete(self):
        """


        PL.checkMinComplete() -> bool

        
        Returns True if test_MinComplete is True for each item in self, False
        otherwise.

        Exepcts all items to have a properly configured ``guide`` attribute.
        """
        result = True
        for i in self:
            if not test_MinComplete(i):
                result = False
                break
        return result

    def checkMaxComplete(self):
        """


        PL.checkMaxComplete() -> bool


        Returns True if test_MaxComplete is True for each item in self, False
        otherwise.

        Expects all items to have a properly configured ``guide`` attribute.
        """
        result = True
        for i in self:
            if not test_MaxComplete(i):
                result = False
                break
        return result

    def checkAll(self,F):
        """


        PL.checkAll(F) -> bool

        
        Returns True if F(i) is True for each item in self, False otherwise.

        Expects all items to have a properly configured ``guide`` attribute.
        """
        result = True
        for i in self:
            if not F(i):
                result = False
                break
        return result

    def sumAll(self,F):
        """


        PL.sumAll(F) -> int


        Returns sum of F(i) for all i in self.
        """
        result = 0
        for i in self:
            result = result + F(i)
        return result

    def getSpendToDate(self):
        """


        PL.getSpendToDate() -> int

        
        Returns sum of current attention expended for all items in self.

        Expects all items to have a properly configured ``guide`` attribute.
        """
        def f1(i):
            val = i.guide.attention.current
            if val == None:
                val = 0
            return val
        self.spendToDate = self.sumAll(f1)
        return self.spendToDate

    def getCostToMin(self):
        """


        PL.getCostToMin() -> int

        
        Returns sum of min quality thersholds specified for each item.

        Expects all items to have a properly configured ``guide`` attribute.
        """
        def f1(i):
            val = i.guide.quality.minStandard
            return val
        self.projCost_MinComplete = self.sumAll(f1)
        return self.projCost_MinComplete

    def getCostToMax(self):
        """


        PL.getCostToMax() -> int


        Returns sum of max quality thersholds specified for each item.

        Expects all items to have a properly configured ``guide`` attribute.
        """
        def f1(i):
            val = i.guide.quality.maxStandard
            return val
        self.projCost_MaxComplete = self.sumAll(f1)
        return self.projCost_MaxComplete
