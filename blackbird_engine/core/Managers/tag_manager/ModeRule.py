#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: alt_TagManager.ModeRule
"""

Module defines ModeRule class.

====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
ModeRule              instructions for how a tag should behave in an event
====================  ==========================================================
"""





#no imports here





class ModeRule:
    """

    Most tags in the Blackbird environment do not have any rules associated
    with them. These "normal" tags can be applied to any object, inherited from
    that object by another object, copied, etcetera.

    Some tags, however, serve as markers for very specific processing or other
    important characteristics. For example, the special extrapolation tag
    requires that an object be built up attribute by attribute, with potentially
    significant recursion. The Blackbird Engine treats these tags with special
    care and applies them to objects in accordance with specific rules.

    The ModeRule class describes the most basic element of such rules. A tag may
    have several different ModeRules: one for inheritance up a structure chain
    ("up" rules), one for copies ("out" rules), one for operations at its
    current host object ("at" rules).

    A ModeRule is composed of the following instructions:
    -- ``allow`` specifies whether Tags.tag() can place the tag on an object in
    these circumstances.
    -- ``cotag`` lists tags that Tags.tag() must apply to an object in addition
    to the trigger tag.
    -- ``detag`` lists tags that Tags.tag() must remove from an object upon
    encountering a trigger tag.
    -- ``error`` lists tags that, if found on the object, will cause a
    TagConflictError.

    NOTE: Users should take great care when specifying rules other than
    ``allow`` or ``errror`` to make sure these do not create circular
    references (tag A adding tag B adding tag A).

    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    cotag                 list; additional tags Tags.tag() must apply to target
    detag                 list; tags that processor must remove from target
    error                 list; tags that cause an error if found w trigger
    place                 bool; is Tags.tag() permitted to add the trigger tag
    
    FUNCTIONS:
    n/a
    ====================  ======================================================
    """
    def __init__(self):
        self.cotag = None
        self.detag = None
        self.error = None
        self.place = True
        
