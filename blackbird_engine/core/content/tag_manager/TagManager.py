#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: alt_TagManager.TagRule
"""

Module defines TagManager class.

====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
TagManager            dictionary of ModeRules keyed by event code
====================  ==========================================================
"""




# Imports
import bb_exceptions

from .TagRule import TagRule




# Constants
# n/a

# Classes
class TagManager(dict):
    def __init__(self):
        self.catalog = {}
        self.directory = {}
        self.rules = {}

    def addRule(self,tag):
        self.rules[tag] = TagRule()
   
    def registerTag(self,tag,*ks, overwrite = False):
        """

        TagManager.registerTag(tag,*ks, overwrite = False) -> None
        """
        ks = set(ks)
        ks.add(str(tag))
        known = ks & set(self.catalog.keys())
        for known_k in known:
            if self.catalog[known_k] != tag:
                c = "Key %s points to a different tag." % known_k
                raise bb_exceptions.TagRegistrationError(c)
            else:
                pass
                #this tag already registered to this key
        new = ks - known
        for new_k in new:
            self.catalog[new_k] = tag


        
    
      
    
