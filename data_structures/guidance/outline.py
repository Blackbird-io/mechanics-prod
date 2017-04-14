#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2014
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: data_structures.guidance.outline

"""
This module defines the Outline class, which organizes content, usually in the
form of Step or LineItem objects, into an ordered container that provides the
Engine a roadmap for analysis. 
====================  ==========================================================
Object                Description
====================  ==========================================================
DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
Outline               container for organizing steps into a path
====================  ==========================================================
"""




#imports
import time

from .step import Step
from .guide import Guide


from ..modelling.statement import Statement
from ..modelling.line_item import LineItem
from ..modelling.link import Link

from data_structures.system.tags import Tags



#globals
#n/a

#classes
class Outline(Step):
    """

    This class provides a foundation for processing roadmaps. Instances start
    out empty, but usually come to include a path of one or more Step objects.

    Instance.protocol_key controls how the interviewer will approach the
    outline. The key must match one of the protocols that the interviewer knows.
    By default, the value is 0, which requires maximum quality analysis for each
    logical step.     
    ==========================  ================================================
    Attribute                   Description
    ==========================  ================================================

    DATA:
    attention_budget            integer representing total attention resources
    completion_rule             pointer to function that checks completion
    focal_point                 criterion for MatchMaker's selection
    protocol_key                num; which interview protocol should apply
    track_progress              bool; whether inst supports progress tracking
    work_space                  unmanaged scrap paper for Topic or other state
    
    FUNCTIONS:
     
    clear_cache()               clear focal point, rule and levels
    set_attention_budget()      set attentionBudget to new value
    set_completion_rule()       attach a new completion rule to instance
    set_focal_point()           attach a pointer to the current focal point
    set_path()                  set path to argument or empty Statement 
    ==========================  ================================================
    """
    def __init__(self, name=None):
        Step.__init__(self, name)
        self.attention_budget = None
        self.completion_rule = None
        self.focal_point = None
        self.path = None
        self.protocol_key = 0
        self.track_progress = False
        self.work_space = {}

    @classmethod
    def from_portal(cls, portal_data, link_list):
        new = cls(None)
        new.__dict__.update(portal_data)

        # rebuild the path
        new.path = Statement.from_portal(portal_data['path'], None)
        for line in portal_data['path']['lines']:
            if line['link']:
                new_link = Link.from_portal(line, new.path)
                # link_list.append(new_link)
                # new.path.append(new_link)
            else:
                LineItem.from_portal(line, new.path)

        # find the right step to assign as focal point
        if new.focal_point:
            fp = new.path.find_first(new.focal_point)
            new.focal_point = fp

        new.tags = Tags.from_portal(portal_data['tags'])
        new.guide = Guide.from_portal(portal_data['guide'])

        return new

    def to_portal(self):
        data = dict()
        data['guide'] = self.guide.to_portal()
        data['tags'] = self.tags.to_portal()
        data['attention_budget'] = self.attention_budget

        # need to implement completion rule serialization eventually
        data['completion_rule'] = self.completion_rule

        data['focal_point'] = self.focal_point.name if self.focal_point else None
        data['path'] = self.path.to_portal()
        data['protocol_key'] = self.protocol_key
        data['track_progress'] = self.track_progress
        data['work_space'] = self.work_space

        return data

    def clear_cache(self):
        """


        Outline.clear_cache() -> None


        Method clears instance ``completion_rule``, ``focal_point``, and
        ``levels`` attributes.
        """
        self.completion_rule = None
        self.focal_point = None

    def set_attention_budget(self,aB):
        """


        Outline.set_attention_budget(aB) -> None


        Method sets instance attention budget.
        """
        self.attention_budget = aB
        

    def set_completion_rule(self, rule):
        """


        Outline.set_completion_rule(rule) -> None


        Method sets instance.completion_rule to argument. Rule should be a
        callable that takes one argument and returns bool (True iff the
        argument is complete).
        """
        self.completion_rule = rule

        
    def set_focal_point(self, fP):
        """


        Outline.set_focal_point(fP) -> None


        Method sets instance.focal_point.
        """
        self.focal_point = fP

    def set_path(self, new_path=None):
        """


        Outline.build_path() -> None


        Method sets instance.path to new_path or an empty Statement.
        Method always sets autoSummarize to False. 
        """
        if new_path:
            self.path = new_path
        else:
            self.path = Statement()
        self.path.autoSummarize = False
        

