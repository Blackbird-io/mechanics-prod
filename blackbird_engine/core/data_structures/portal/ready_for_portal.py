#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: Analysis.ReadyForPortal
"""

Module defines the ReadyForPortal mix-in class.

====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
ReadyForPortal        Schema subclass, makes instances from seeds, returns dict
====================  ==========================================================
"""




#imports
import copy

import BBExceptions

from .schema import Schema




#globals
#n/a

#classes
class ReadyForPortal(Schema):
    """

    ReadyForPortal objects inherit Schema attribute whitelist restrictions.
    ReadyForPortal class adds instance generation and update from seed objects
    (``rich`` Engine-oriented types like FullQuestion) and clean-dictionary
    output. 
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    n/a

    FUNCTIONS:
    from_engine()         returns new instance w attr values from seed
    to_portal()           runs from_engine, returns copy of instance dictionary 
    ====================  ======================================================
    """    
    def __init__(self,var_attrs):
        Schema.__init__(self,var_attrs)

    def from_engine(self, seed):
        """


        PortalObject.from_engine(seed) -> obj

        
        Method creates a new instance of the caller's class, then sets all
        attributes on that new instance to values from seed. Method skips
        instance attributes that seed does not define. 
        """
        cls = self.__class__
        new_instance = cls()
        for attr in new_instance.__dict__:
            try:
                seed_val = getattr(seed, attr)
                new_instance.__dict__[attr] = seed_val
            except AttributeError:
                continue
        return new_instance
        
    def to_portal(self, seed = None):
        """


        PortalObject.to_portal([seed = None]) -> dict

        
        Method returns a dictionary that follows the instance attribute pattern
        with values that track the seed. If ``seed`` is None, method uses
        instance. Otherwise, when caller specifies ``seed``, method runs
        from_engine() to compact the seed into an instance of the bottom class,
        and then delivers a dictionary tracking the instance.
        """
        if seed:
            prelim = self.from_engine(seed)
        else:
            prelim = self
        result = prelim.__dict__.copy()
        return result
        
    
