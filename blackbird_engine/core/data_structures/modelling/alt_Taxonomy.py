#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: DataStructures.Modelling.Taxonomy
"""

Module defines Taxonomy class.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
Taxonomy              organizes objects into standards and child sub-types
====================  ==========================================================
"""



#imports
from collections import defaultdict



#globals
#n/a

#classes
class Taxonomy(defaultdict):
    """

    The Taxonomy class uses a dictionary to organize objects into one standard
    type and zero or more child sub-types in the same form. 

    Class provides a customized dict that:
     -- contains a .standard attribute
     -- returns itself for missing keys
     -- records a new instance of the class for every defined key

    That is, every key in a Taxonomy object also points to a child tree. The
    .standard for that key contains the value for that node. Calling
    ``x[k].standard`` on a Taxonomy object **always** returns a value: either
    the standard for x, if k is not in x.keys(), or the standard for x[k]
    othwerwise. 

    Common use patterns (pseudo-code):

    >>> saas_model = Model()
    >>> "operating" in saas_model.taxonomy.keys():
    False
    >>> saas_model.taxonomy["operating"]
    <Taxonomy obj 0>
    >>> saas_model.taxonomy["operating"].standard
    <business unit "default">
    >>> saas_model.taxonomy["operating"] = BusinessUnit(name = "ops")
    >>> saas_model.taxonomy["operating"]
    <Taxonomy obj 1>
    >>> saas_model.taxonomy["operating"].standard
    <business unit "ops">
    
    
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    standard              obj; standard value for the node
    
    FUNCTIONS:
    __setitem__()         set self[k] to Taxonomy(v) via instance class    
    ====================  ======================================================
    """
    def __init__(self, standard = None):
        self.standard = standard

    def __missing__(self, k):
        """


        Taxonomy.__getitem__(k) -> obj


        If ``k`` in instance.keys(), method returns value for k; otherwise,
        method returns instance.

        Method guarantees no KeyError on instance[k].standard calls. 
        """
        return self

    def __setitem__(self, k, v):
        """


        Taxonomy.__setitem__(k, v) -> None


        Method sets instance[k] to a child taxonomy with standard set to v. The
        child taxonomy is a new instance of the caller's .__class__. 
        """
        child = Taxonomy()
        child.standard = v
        defaultdict.__setitem__(self, k, child)
