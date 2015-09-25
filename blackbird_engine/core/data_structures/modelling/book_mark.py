#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: data_structures.modelling.book_mark
"""

Module defines BookMark class. BookMarks are specialized LineItems that mark
relative position of other lineitems across financials. Financials objects can
use bookmarks to determine where to place copies of lineitems.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
BookMark              specialized lineitems that serve as position markers
====================  ==========================================================
"""




#imports
import copy
import time

import BBExceptions
import BBGlobalVariables as Globals

from data_structures.system.tags import Tags

from .line_item import LineItem




#globals
#Tags class carries a pointer to the tag manager; access individual tags
#through that pointer
BLACKBIRDSTAMP = Tags.tagManager.catalog["bb"]
bookMarkTag = Tags.tagManager.catalog["bm"]
skipTag = Tags.tagManager.catalog["skip"]

#classes
class BookMark(LineItem):
    """

    Special type of LineItem that always carries a bookMarkTag, whose name
    always starts with a bmPrefix. Default tags and bmPrefix are specified at
    class level.

    Bookmark LineItems all have a name that begins with the Blackbird stamp
    specified in globals ("|BB|"). Bookmark LineItems are tagged "SKIP" and
    "bookMark". MatchMaker generally skips items tagged "SKIP" when searching
    for matching groupings.
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================
    DATA:
    bmTags                book mark and skip tags from tagCatalog
    bmPrefix              BLACKBIRDSTAMP from tagCatalog
    
    FUNCTIONS:
    setName()             method sets instance name w "|BB|" prefix
    ====================  ======================================================
    """
    bmTags = [bookMarkTag,skipTag]
    bmPrefix = BLACKBIRDSTAMP
    
    def __init__(self, bmName = None, *tags):
        LineItem.__init__(self)
        self.tag(*self.bmTags)
        self.tag(BLACKBIRDSTAMP)
        if bmName:
            self.setName(bmName)
        if tags:
            self.tag(*tags)
        
    def setName(self,newName):
        """


        BookMark.setName(newName) -> None


        Method adds the BLACKBIRDSTAMP prefix to the name and then sets the
        instance name accordingly. 
        """
        if newName:
            newName = self.bmPrefix + newName
        Tags.setName(self,newName)
