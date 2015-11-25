#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: Analysis.MiniQuestion
"""

Module defines MiniQuestion class.

====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
MiniQuestion          A compact template for customizing questions in a Topic
====================  ==========================================================
"""




#imports
import bb_exceptions

from data_structures.system.bbid import ID
from data_structures.system.tags import Tags




#globals
#n/a

#classes
class MiniQuestion:
    """

    The MiniQuestion object provides an abbreviation of FullQuestion that
    Topics can easily identify and customize. To reduce risk of error,
    MiniQuestion objects restrict attribute creation through normal assignment
    commands.

    When a controller creates a MiniQuestion object from a FullQuestion, the
    MiniQuestion will include an input_array filled with 5 InputElement objects
    of the question's type. By default, only the first InputElement is active.
    Topics should manually activate additional elements if they would like
    Portal to display them to user.     
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    context               dict; Topics can fill in if 
    id                    instance of Platform.ID; equals FullQuestion
    input_array           list of typed input elements; only array[0] active
    progress              int; completion indicator for interview, 0<= p <=100
    tags                  instance of Platform.Tags; usually FullQuestion.tags
    topic_name            string; should be filled in by Topics for display
    
    FUNCTIONS:
    n/a
    ====================  ======================================================
    """
    def __init__(self):
        self.__dict__["id"] = ID()
        self.__dict__["tags"] = Tags()
        #above are generally read-only
        self.__dict__["input_array"] = []
        self.__dict__["context"] = dict()
        self.__dict__["progress"] = None
        self.__dict__["topic_name"] = None

    def __setattr__(self,attr,value):
        #no new vars
        if attr in self.__dict__:
            object.__setattr__(self,attr,value)
        else:
            c = "MiniQuestion class acts as template, restricts new attributes."
            raise bb_exceptions.ManagedAttributeError(c)

    
    
