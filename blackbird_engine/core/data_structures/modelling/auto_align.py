#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: data_structures.modelling.auto_align
"""

Module defines AutoAlign class, which allows for automatic ordering (in some
limited situations). 
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
AutoAlign             mix in class that allows for easy list ordering

====================  ==========================================================
"""




#imports
import copy
import time
import BBExceptions

from BBGlobalVariables import *




#globals
#n/a

#classes
class AutoAlign:
    """

    Mix-in class that allows instances to be automatically ordered by a Queue
    object.

    Positional attributes are related, with affirmative requirements implying
    a negative result on the related option. Blackbird objects therefore expect
    to see AutoAlign.canBeFirst == False when AutoAlign.mustBeFirst == True. The
    Queue class uses this convention when organizing lists of AutoAlign objects.
    The relationship is policy. It is not rigidly enforced. 
    
    ``exclusivity`` is a dynamic attribute managed by a desciptor.

    Exclusivity is automatically True iff instance.mustBeFirst == True and
    instance.mustBeLast == True. That is, if an object must be both first and
    last in a list, it must be the only object in the list.

    Setting exclusivity to True automatically changes the ``must`` attributes to
    True and the ``can`` attributes to False. Turning exclusivity to False
    automatically changes the ``must`` attributes to False **without** altering
    the ``can`` attributes. The descriptor prohibits instance.exclusivity values
    other than True or False.

    NOTE: If all positional attributes on object are set to False, the list
    containing the object must be at least 3 items long to align.

    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA: 
    autoAlign             bool; if False, object can be located anywhere
    mustBeFirst           bool; if True, object must be first in a list
    mustBeLast            bool; if True, object must be last in a list
    canBeFirst            bool; if False, object may NOT be first
    canBeLast             bool: if False, object may NOT be last
    exclusivity           bool; if True, object must be the only item in a list

    FUNCTIONS:
    toggleAutoAlign()     set instance.autoAlign to bool negative
    resetAlignment()      set positional attributes to default (flexible) state
    toggleExclusivity()   set exclusivity to bool negative
    
    ====================  ======================================================
    """
    def __init__(self):
        self.autoAlign = True
        self.mustBeFirst = False
        self.mustBeLast = False
        self.canBeFirst = True
        self.canBeLast = True

    def __str__(self):
        res = ""
        width = 30
        l0 = "-"*width+"\n"
        l1 = "ID:             %s\n" % id(self)
        l2 = "autoAlign:      %s\n" % self.autoAlign
        l3 = "exclusivity:    %s\n" % self.exclusivity
        l4 = "\n"
        l5 = "mustBeFirst:    %s\n" % self.mustBeFirst
        l6 = "mustBeLast:     %s\n" % self.mustBeLast
        l7 = "canBeFirst      %s\n" % self.canBeFirst
        l8 = "canBeLast       %s\n" % self.canBeLast
        l9 = "="*width+"\n"
        res = l0+l1+l2+l3+l4+l5+l6+l7+l8+l9
        return res

    def toggleAutoAlign(self):
        """

        AutoAlign.toggleAutoAlign() -> None

        Method sets self.autoAlign to the boolean negative of its prior value.
        """
        self.autoAlign = not self.autoAlign

    def resetAlignment(self):
        """

        AutoAlign.resetAlignment() -> None
        
        Method sets alignment attributes to their default, maximally flexible
        values (``must`` to False and ``can`` to True).
        """
        self.mustBeFirst = False
        self.mustBeLast = False
        self.canBeFirst = True
        self.canBeLast = True

    class dynamicExclusivityManager:
        def __get__(self,instance,owner):
            if instance.mustBeFirst and instance.mustBeLast:
                return True
            else:
                return False
        def __set__(self,instance,value):
            if value == True:
                instance.mustBeFirst = True
                instance.mustBeLast = True
                instance.canBeFirst = False
                instance.canBeLast = False
            elif value == False:
                instance.mustBeFirst = False
                instance.mustBeLast = False
            else:
                instance.mustBeFirst = False
                instance.mustBeLast = False
                comment = "Attribute must have a boolean value."
                raise BBExceptions.ValueFormatError(comment)

    exclusivity =  dynamicExclusivityManager()

    def toggleExclusivity(self):
        """

        AutoAlign.toggleExclusivity() -> None
        
        Method sets exclusivity to the boolean negative of its prior value.
        """
        currentStatus = self.exclusivity
        self.exclusivity = not currentStatus
