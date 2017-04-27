# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL
# Blackbird Environment
# Module: data_structures.modelling.book_mark
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

from data_structures.system.tags import Tags

from .line_item import LineItem




#globals
#Tags class carries a pointer to the tag manager; access individual tags
#through that pointer
BLACKBIRD_STAMP = "|BB|"

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
    set_name()             method sets instance name w "|BB|" prefix
    ====================  ======================================================
    """
    bmPrefix = BLACKBIRD_STAMP
    
    def __init__(self, bmName = None, *tags):
        LineItem.__init__(self)
        # self.tags.add(*self.bmTags)
        self.tags.add(BLACKBIRD_STAMP)
        if bmName:
            self.set_name(bmName)
        if tags:
            self.tags.add(*tags)
        
    def set_name(self,newName):
        """


        BookMark.set_name(newName) -> None


        Method adds the BLACKBIRD_STAMP prefix to the name and then sets the
        instance name accordingly. 
        """
        if newName:
            newName = self.bmPrefix + newName

        Tags.set_name(self.tags, newName)
