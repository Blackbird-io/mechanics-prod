# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL

# Blackbird Environment
# Module: data_structures.system.tags
"""

Module defines Tags class and provides certain related functions.

====================  =========================================================
Attribute             Description
====================  =========================================================

DATA:
N/A

FUNCTIONS:
N/A

CLASSES:
Tags                  composition class that provides tagging and naming
====================  =========================================================
"""




# imports
import copy
import bb_exceptions

from tools.parsing import deCase




# globals
# n/a

# classes
class Tags:
    """

    Object that carries identifying tags throughout the Blackbird environment.

    Tags are stored in two sets: ``required`` and ``optional``. Sets may
    overlap.

    Matchmaking functions (external to a BusinessUnit) MUST match ALL
    ``required`` tags to a target object.

    Matchmaking functions (external to a BusinessUnit) do not have to
    match any of the ``optional`` tags for the match to be valid.

    New tags are added to the optional list by default. Removing a tag from an
    object removes it from both required and optional lists simultaneously.
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    all                   property; set of all optional and required tags
    name                  property; name of object described by instance
    optional              property; set of all optional tags
    required              property; set of all required tags

    FUNCTIONS:
    copy()                returns a copy of an object with own tag lists
    extrapolate_to()      returns a Tags.copy()
    inherit_from()        adds tags on a different object to instance
    set_name()            sets instance.reqTags[0]
    add()                 adds tag to object, if parameters allow
    remove()               removes all instances of tag from object
    ====================  ======================================================
    """
    def __init__(self, name=None):
        self._optional = set()
        self._required = set()
        self._name = None
        self.set_name(name)

    @property
    def name(self):
        return self._name

    @property
    def optional(self):
        return self._optional.copy()

    @property
    def required(self):
        return self._required.copy()

    @property
    def all(self):
        return self._required | self._optional

    def copy(self):
        """


        Tags.copy() -> obj


        Method returns a shallow copy of the instance.
        """
        result = Tags(self.name)
        self._copy_tags_to(result)

        return result

    def extrapolate_to(self, target):
        """


        Tags.extrapolate_to(target) -> obj

        --``target`` is another instance of Tags

        Method provides a way to cross-pollinate tags between objects. Method
        returns a shallow copy of the seed (caller) instance. The seed tags
        provide the template. The method then adds new tags from target, one
        field at a time (new items in target._optional go on result._optional).
        """
        seed = self
        result = Tags.copy(seed)
        target._copy_tags_to(result)

        return result

    def inherit_from(self, source):
        """


        Tags.inherit_from() -> None

        --``source`` is another Tags instance from which to inherit tags

        Method adds tags found on the source to self as optional tags.

        This method evaluates tags as casefolded objects to the extent possible.
        """

        # source tags is now **unordered**
        for tag in source.all:
            self.add(tag)

    def set_name(self, name):
        """


        Tags.set_name(name) -> None

        --``name`` is the new name for the object described by Tags instance

        Method for setting the name of an object.
        """

        self._name = deCase(name)

    def add(self, *newTags, field="opt"):
        """


        Tags.add() -> None

        --``*newTags`` is a list of tags to include on the instance

        The ``field`` argument regulates tag placement on the instance:
        -- "req" means tags will be added to instance._required
        -- "opt" [ default ] means tags will be added to instance._optional

        NOTE: Method automatically **decases** all tags.

        Tags should generally be optional. When in doubt, add more tags.
        """
        attrs = {}
        attrs["r"] = attrs["req"] = attrs["required"] = "_required"
        attrs["o"] = attrs["opt"] = attrs["optional"] = "_optional"
        attrs[0] = attrs["_required"] = attrs["r"]
        attrs[1] = attrs["_optional"] = attrs["o"]

        real_thing = getattr(self, attrs[field])

        for tag in newTags:
            # NOTE: automatically decase tags!
            tag = deCase(tag)
            real_thing.add(tag)

    def remove(self, badTag):
        """


        Tags.remove(badTag) -> None

        --``badTag`` tag to remove from instance

        Method to remove tags from an instance.
        """

        if badTag in self._required:
            self._required.remove(badTag)

        if badTag in self._optional:
            self._optional.remove(badTag)

    #*************************************************************************#
    #                          NON-PUBLIC METHODS                             #
    #*************************************************************************#
    def _copy_tags_to(self, target):
        """


        Tags._copy_tags_to(target) -> None

        --``target`` is another instance of Tags on which to transplant tags

        NOTE: Method changes target **in place**.

        Method copies tags from instance to target, attribute by attribute.
        """
        fields = ["_required", "_optional"]
        for attr in fields:
            source_tags = getattr(self, attr)
            for tag in source_tags:
                target.add(tag, field=attr)
