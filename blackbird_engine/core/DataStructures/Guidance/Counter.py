#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2014
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: DataStructures.Guidance.Counter

"""
This module defines the Counter class.
====================  ==========================================================
Object                Description
====================  ==========================================================
DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
Counter               simple gauge objects
====================  ==========================================================
"""




#imports
#n/a




#globals
#n/a

#classes
class Counter:
    """
    Simple gauge class. Allows for two-way incrementation (up or down),
    depending on step specified in self.increment().

    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================
    current               tracks current value
    cutOff                max value (optional)

    increment()           increases current value by step, up to cutOff
    reset()               sets current value to 0
    ====================  ======================================================
    """
    def __init__(self,start = 0, cutOff = None):
        self.current = start
        self.cutOff = cutOff

    def increment(self, step = 1):
        """
        C.increment([step]) ->  None

        Sets self.current to the sum of the existing value and the increment. If
        instance specifies a cutOff and the new value is greater than the
        cutOff, sets self.current to the cutOff value.
        
        By default ``step`` equals 1.
        """
        newVal = self.current + step
        if self.cutOff:
            if newVal < self.cutOff:
                self.current = newVal
            else:
                self.current = cutOff
        else:
            self.current = newVal

    def reset(self):
        """
        C.reset() -> None

        Resets self.current to 0.
        """
        self.current = 0
