#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2014
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: data_structures.guidance.step
"""

Module provides a representation of a discrete logical step that's compatible
with selection algorithms while remaining lightweight and flexible. You can use
the class by itself or as a mix-in to create stages and paths (ordered
containers of steps). 
====================  ==========================================================
Object                Description
====================  ==========================================================
DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
Step                  single logical step, compatible with selection algos
====================  ==========================================================
"""




#imports
import tools.for_printing as printing_tools

from .guide import Guide
from data_structures.system.print_as_line import PrintAsLine
from data_structures.system.relationships import Relationships
from data_structures.system.tags import Tags
from data_structures.system.tags_mixin import TagsMixIn
from data_structures.system.bbid import ID




#globals
#n/a

#classes
class Step(PrintAsLine, TagsMixIn):
    """

    Class for tracking logical steps. Has the tags and guide interface of
    LineItem but doesn't commit to a numeric value. Pretty lightweight and
    flexible.
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    guide                 instance of Guide
    relationships         instance of Relationships class

    FUNCTIONS:
    pre_format()          sets instance.formatted to a line with a checkbox
    ====================  ======================================================
    """
    DEFAULT_PRIORITY_LEVEL = 1
    DEFAULT_QUALITY_REQUIREMENT = 5
    
    def __init__(self, name=None,
                 priority=DEFAULT_PRIORITY_LEVEL,
                 quality=DEFAULT_QUALITY_REQUIREMENT):
        PrintAsLine.__init__(self)
        TagsMixIn.__init__(self, name)

        self.guide = Guide(priority, quality)
        self.relationships = Relationships(self)
        self.id = ID()

    def to_database(self, **kwargs):
        result = dict()
        result['tags'] = self.tags.to_database()
        result['guide'] = self.guide.to_database()

        return result

    @classmethod
    def from_database(cls, data):
        result = cls()
        result.tags = Tags.from_database(data['tags'])
        result.guide = Guide.from_database(data['guide'])

        return result

    def pre_format(self, **kargs):
        #custom formatting logic
        if self.tags.name:
            kargs["name"] = self.tags.name
        self.formatted = printing_tools.format_completed(self, **kargs)

    def register(self, namespace):
        self.id.set_namespace(namespace)
