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
Tags                  mix-in class that provides tagging, naming, and belonging
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

    Tags are stored in two lists: ``required`` and ``optional``. Lists may
    overlap and may contain items more than once.

    Matchmaking functions (external to a BusinessUnit) MUST match ALL
    ``required`` tags to a target object.

    Matchmaking functions (external to a BusinessUnit) do not have to
    match any of the ``optional`` tags for the match to be valid.

    New tags are added to the optional list by default. Removing a tag from an
    object removes it from both required and optional lists simultaneously.

    Each Tags object has one special tag: ``name``.

    "name" tag:
    Dynamic attributes of each Tags object. Special tag should be modified
    through its respective attribute (Tags.name) or associated methods.

    The "name" tag is stored in required[0]; the object's name is the value
    of required[0].

    NOTE: Direct changes to required[0] (instance-level state for ``name``) are
    not recommended.

    For ``name``, the dynamicSpecialTagManager descriptor routes gets and sets
    of the attribute to the right slot in ``required``. The descriptor also
    transforms deletions of ``name`` attribute to None value in the proper
    position of ``required``.

    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    all                   list; dynamic, returns requiredTags+optionalTags
    name                  name of instance, dynamic, value of requiredTags[0]
    optional              list; dynamic, returns _optionalTags
    required              list; tags required for matching
    spacer_req            string; CLASS, separates req tags from optional in all
    spacer_opt            string; CLASS, separates _opt from _inh tags in opt

    FUNCTIONS:
    copy()                returns a copy of an object with own tag lists
    extrapolate_to()      returns a Tags.copy()
    inherit_from()        adds tags on a different object to instance
    set_name()            sets instance.reqTags[0]
    tag()                 adds tag to object, if parameters allow
    untag()               removes all instances of tag from object
    ====================  ======================================================
    """
    # class attributes:
    BLACKBIRD_STAMP = "|BB|"
    spacer_opt = BLACKBIRD_STAMP+"endOwnOptionalTags"
    spacer_req = BLACKBIRD_STAMP+"endRequiredTags"

    def __init__(self, name=None):
        self._optional = []
        self.required = [None]

        # self.name is requiredTags[0] so list should have minimum length of 1;
        # actual values set through methods
        self.set_name(name)

    class _dyn_OptTManager:
        """

        Descriptor class that compiles and returns a list of optional tags on an
        instance. On __get__, class returns a list of optional and inherited
        tags on an instance, separated by a spacer.
        """

        def __get__(self, instance, owner):
            oTags = instance._optional + [instance.spacer_opt]
            return oTags

        def __set__(self, instance, value):
            c = "Direct write to ``optionalTags`` prohibited."
            raise bb_exceptions.ManagedAttributeError(c)

    # dynamic class attribute:
    optional = _dyn_OptTManager()

    class _dyn_AllTManager:
        """

        Descriptor class that compiles and returns a list of all tags on an
        instance.
        """

        def __get__(self, instance, owner):
            allTags = instance.required + [instance.spacer_req]
            allTags = allTags + instance.optional
            return allTags

        def __set__(self, instance, value):
            c = "Direct write to ``allTags`` prohibited."
            raise bb_exceptions.ManagedAttributeError(c)

    # allTags is a Tags class attribute managed by the descriptor above
    all = _dyn_AllTManager()

    class _dyn_SpecTManager:
        """

        Descriptor class that handles ``name`` attribute.
        """

        def __init__(self, targetAttribute):
            self.target = targetAttribute

        def __get__(self, instance, owner):
            if self.target == "name":
                return instance.required[0]

        def __set__(self, instance, value):
            if self.target == "name":
                instance.required[0] = value

        def __delete__(self, instance):
            if self.target == "name":
                instance.required[0] = None

    # Tags.name is a dynamic class attribute linked to
    # self.required and managed by the descriptor above
    name = _dyn_SpecTManager(targetAttribute="name")

    def copy(self):
        """


        Tags.copy([ = True]) -> obj


        Method returns a shallow copy of the instance. If ```` is
        True, copy follows ``out`` rules.
        """
        result = copy.copy(self)
        self._copy_tags_to(result)

        return result

    def extrapolate_to(self, target):
        """


        Tags.ex_to_special(target[, mode = "at"]) -> obj


        Method provides a way to cross-pollinate tags between objects. Method
        returns a shallow copy of the seed (caller) instance. The seed tags,
        after passing through rules, provides the template. The method
        then adds new tags from target one field at a time (new items in
        target._optional go on result._optional).

        Method does not look at target.required[0]. Method applies target
        tags in sorted() order.

        The optional ``mode`` argument describes the set of rules Tags.tags.tag()
        applies when moving target tags to result.
        """
        seed = self
        result = Tags.copy(seed)
        # maintain all tags on seed
        fields = ["required", "_optional"]
        for attr in fields:
            targ_tags = getattr(target, attr)
            if attr == "required":
                targ_tags = targ_tags[1:]
            targ_tags = set(targ_tags)
            r_res_tags = getattr(result, attr)
            res_tags = set(r_res_tags)
            new_tags = targ_tags - res_tags
            new_tags = sorted(new_tags)
            # sort the new tags into a stable order to ensure consistency
            # across runtime
            result.tag(*new_tags, field=attr)
        return result

    def inherit_from(self, source, noDuplicates=True):
        """


        Tags.inherit_from() -> None


        Method adds tags found on the source to self as inherited tags. Method
        skips source.required[0] (name and partOf).

        If ``noDuplicates`` is True, method will not copy any source tags that
        the instance already carries. In this mode, a SINGLE existing tag will
        block inheritance of ALL matching objects.

        If ``noDuplicates`` is False, method will copy all source tags as is.
        That is, the instance and source occurrences will be additive.

        This method evaluates tags as casefolded objects to the extent possible.
        """
        sourceTags = source.required[1:] + source.optional[:]

        if noDuplicates:
            sourceTags = set(sourceTags) - set(self.all)

        # source tags is now **unordered**
        sourceTags = sourceTags
        sourceTags = sorted(sourceTags)
        # turn sourceTags into a sorted list to make sure tags are always added
        # in the same order; otherwise, pseudo-random order of tags in a set
        # wrecks HAVOC on comparisons
        self.tag(*sourceTags)

    def set_name(self, newName):
        """


        T.tags.set_name(newName) -> None


        Method for setting the name of an object.

        The name specified via this method is set as the object's name attribute
        and recorded in object.required[0].

        All "names" in the Blackbird environment are required tags.
        If a suitor object specifies a name condition, a target object must have
        an identical name to be a match.

        Names are distinct from other required tags in that within a given
        container, names should generally be unique. That is, a given container
        object should generally contain one object with a specific name. By
        contrast, a container object may contain multiple objects with identical
        other required (required[1:]). The decision of whether to follow
        the unique name policy is left to higher-level objects. Common
        exceptions include Financials objects, which create replicas with
        identical names to manage certain records.

        Names are stored in the first position of required and managed
        through the dynamicSpecialTagManager descriptor. Names are optional. If
        no name is specified, the required[0] position will be filled with a
        None object. Deleting a name similarly sets required[0] to None.
        """
        self.name = deCase(newName)

    def tag(self, *newTags, field="opt", permit_duplicates=False):
        """


        Tags.tag( *newTags[,
                  field = "opt"[,
                  permit_duplicates = False]]]) -> None


        Method appends tags to an instance.

        NOTE 1: Method automatically **decases** all tags.

        The ``field`` argument regulates tag placement on the instance:
        -- "req" means last position of instance.required
        -- "opt" [ default ] means last position of instance._optional

        Tags should generally be optional. When in doubt, add more tags.

        If ``permit_duplicates`` is False, method will skip (no-op) tags
        that already appear in the specified field on the on the instance.
        """
        attrs = {}
        attrs["r"] = attrs["req"] = attrs["required"] = "required"
        attrs["o"] = attrs["opt"] = attrs["optional"] = "_optional"
        attrs[0] = attrs["required"] = attrs["r"]
        attrs[1] = attrs["_optional"] = attrs["o"]

        real_thing = getattr(self, attrs[field])

        for tag in newTags:
            # NOTE: automatically decase tags!
            tag = deCase(tag)

            # filter out duplicates if necessary
            if tag not in real_thing or permit_duplicates:
                real_thing.append(tag)

    def untag(self, badTag):
        """


        Tags.untag(badTag) -> None

        --``badTag`` tag to remove from instance

        Method to remove tags from an instance.

        If badTag is located in required[0], method replaces the badTag with
        None. Method calls itself upon finding and removing the first iteration
        of the badTag to check for any others.
        """

        # have to nest the recursive call in the if statements, otherwise
        # method will loop indefinitely. that is, only call the method again if
        # the badTag was already found once and removed

        if badTag in self.required[:1]:
            location = self.required.index(badTag)
            self.required[location] = None
            self.untag(badTag)

        if badTag in self.required[1:]:
            self.required.remove(badTag)
            self.untag(badTag)

        if badTag in self._optional:
            self._optional.remove(badTag)
            self.untag(badTag)

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

        fields = ["required", "_optional"]
        for attr in fields:
            source_tags = getattr(self, attr)
            if attr == "required":
                source_tags = source_tags[1:]
                preserve = getattr(target, attr)[:1]
                # Upgrade-S: can do a direct call instead of getattr

            setattr(target, attr, [])
            # make independent blank lists for the target to make sure method
            # doesn't accidentally modify source attributes (ie, when it is
            # called as part of Tags.copy)

            new_tags = getattr(target, attr)
            if attr == "required":
                new_tags.extend(preserve)
                # preserve target name

            for t in source_tags:
                new_tags.append(t)
