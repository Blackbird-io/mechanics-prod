#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: data_structures.system.protected_catalog
"""

Module defines ProtectedCatalog class that returns copies of values, not the
original. ProtectedCatalog also features expanded key look-up functionality.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
ProtectedCatalog      catalog that issues copies of values, not originals
====================  ==========================================================
"""




#imports
from .catalog import Catalog as StandardCatalog




#globals
#n/a

#classes
class ProtectedCatalog(StandardCatalog):
    """

    Class customizes Platform.Catalog. Provides a specialized issue method that
    looks up questions by both name and bbid and returns a copy of the matching
    entry. FullQuestion objects are stateful in ``input_array`` and ``context``.
    Issuing a copy instead of the original makes sure that the Engine can ask
    two or more custom versions of the same question in parallel processes.     
    ==========================  ================================================
    Attribute                   Description
    ==========================  ================================================

    DATA:
    n/a

    FUNCTIONS:
    issue()                     returns copy of entry with matching id or name
    ==========================  ================================================
    """
    def __init__(self):
        StandardCatalog.__init__(self)

    def issue(self,key):
        """


        Catalog.issue(key) -> FullQuestion


        Method locates catalog entry and returns its copy. ``key`` can be either
        object name or bbid. 
        """
        result = None
        entry = None
        try:
            #assume key is bbid
            entry = StandardCatalog.issue(self, key)
        except KeyError:
            #key not in main table, check if it's a name
            q_bbid = self.by_name[key]
            entry = StandardCatalog.issue(self, q_bbid)
        result = entry.copy()    
        #
        return result
