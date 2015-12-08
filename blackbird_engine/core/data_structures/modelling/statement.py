#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: data_structures.modelling.statement
"""

Module defines Statement, a container for lines.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
Statement             container that stores, updates, and organizes LineItems
====================  ==========================================================
"""




# Imports
import copy
import time

import bb_exceptions

from data_structures.system.tags import Tags
from tools import parsing as ParsingTools

from .book_mark import BookMark
from .equalities import Equalities
from .line_item import LineItem




# Constants
# n/a

# Globals
# Tags class carries a pointer to the tag manager; access individual tags
# through that pointer
bookMarkTag = Tags.tagManager.catalog["bookmark"]
builtInTag = Tags.tagManager.catalog["built_in"] 
doNotTouchTag = Tags.tagManager.catalog["do_not_touch"]
dropDownReplicaTag = Tags.tagManager.catalog["ddr"]
ddr_tag = dropDownReplicaTag
skipTag = Tags.tagManager.catalog["skip"]
summaryTag = Tags.tagManager.catalog["summary"]
tConsolidated = Tags.tagManager.catalog["consolidated"]
uninheritableTags = [doNotTouchTag, dropDownReplicaTag]

# Classes
class PlacementSuccess(Exception):
    pass
        
class Statement(list, Tags, Equalities):
    """

    Ordered container that supports hierarchies and fast(er) lookup.
    
    ITEM HIERARCHIES:
    
    A Statement object is generally a list of lines or line-like objects.

    Lines vary by significance. Some show very basic information and would
    appear in the least granular presentation of the statement. We call these
    lines ``top-level``.  Other lines elaborate on the top-level lines. We call
    these lines ``details``. 

    The distinction here is one of financial custom: you could easily imagine a
    ``flat`` statement that shows every piece of information in order. It can
    be difficult for people to read a long, flat list, so finance professionals
    generally add hierarchy to split the lines into logical chunks.

    Our Statement objects track this pattern. Statements support multiple
    levels of hierarchy: one line can have details, and those details can have
    details too.

    TOP OF THE PILE:
    
    Objects that say they are part of the Statement go at the top of our
    hierarchy. In other words, if obj.partOf is in instance._top_level_names,
    the Statement will treat the object as a top-level item. A blank (None)
    .partOf attribute also classifies the object as top-level. 

    DETAILS:
    
    Detail objects name another object in the container as their parent. 
    
    Example 1: financials2014 includes lineitem1 and lineitem5.
    
      lineitem1.name = "Insurance"
      lineitem1.partOf = "SGA".
      lineitem5.name = "SGA"
      lineitem5.partOf = "Financials".

    In such a scenario, lineitem1 is a detail of lineitem5.

    Details should follow immediately after their parents in the Statement.
    
    SUMMARIES:
    
    Statement objects automatically sum values for lines that have details. The
    Statement lists these total values on new lines called ``summaries.``

    1.  Summaries appear after the last detail for a given item.        
    2.  Summary line names are a concatenation of the parent and the
        summary prefix. For example, a summary for lineitem5 above would have
        .name ==``TOTAL SGA``
    3.  Summaries are at the same level of the statement hierarchy as their
        parent. In code, summary.partOf == parent.partOf.

    REPLICAS:
    
    Statements create replicas of lines that have both details and a defined
    value to help tabulate summaries.

    Replicas are copies of a line that are also part of that same line. When a
    Statement inserts a replica for a line, it moves the line's value to the
    replica and zeroes out the parent. If the parent then picks up more value
    in the future, Statement will increment the replica by that value and zero
    out the parent. 

    Visually, the outcome looks as follows:

        SGA .......... 10                 SGA ..........0              
          Employees... 6                    SGA.........10
          Insurance... 8        ===>        Employees...6  
          Security.... 2                    Insurance...8
        *TOTAL SGA.... 16                   Security....2
                                          TOTAL SGA.....26

        *only lineitems that are partOf SGA increment the summary
            
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    autoSummarize         bool, controls whether summarize runs on __str__
    contextualFormatting  bool, 
    table_by_name         lookup table by object.name; values are index sets
    table_by_part         lookup table by object.partOf; values are index sets

    FUNCTIONS:
    add_line_to()         add a detail object to a parent 
    add_top_line()        add top-level object, optionally after another
    build_tables()        build standard lookup tables for instance contents
    build_custom_table()  build custom lookup table
    copy()                return deep copy
    increment()           add data from a collection of objects
    indexByName()         build lookup table, return item position
    reset()               clear values and managed lines
    summarize()           compute total values, manage hierarchy
    ====================  ======================================================
    """
    keyAttributes = []
    # Retain as explicit empty list to force Equalities to use list.__eq__ but
    # support tracing.

    _LABEL_MISFIT = "MISFIT"
    _INDENT = 2

    SIGNATURE_FOR_SUMMARY_RESET = "update reset"
    SIGNATURE_FOR_SUMMARY_UPDATES = "updateSummaries"
    SIGNATURE_FOR_MANAGING_REPLICAS = "manageDDR"
    SIGNATURE_FOR_INCREMENTATION = "Incremented "
    SUMMARY_PREFIX = "TOTAL"
    
    def __init__(self, name=None):
        list.__init__(self)
        Tags.__init__(self, name=name)

        self.autoSummarize = True
        self.contextualFormatting = True
        self.table_by_name = {}
        self.table_by_part = {}
        
        self._hierarchy_groups = None
        self._hierarchy_map = None
        self._top_level_names = [None, self.name, "financials", "Financials"]

    def __eq__(self, comparator, trace=False, tab_width=4):
        """


        Statement.__eq__() -> bool


        Method explicitly delegates work to Equalities.__eq__(). The Financials
        class defines keyAttributes as an empty list at the class level, so
        Equalities will run pure-play list.__eq__() comparison logic, but still
        support tracing.
        """
        return Equalities.__eq__(self, comparator, trace, tab_width)

    def __ne__(self, comparator, trace=False, tab_width=4):
        """


        Statement.__ne__() -> bool


        Method explicitly delegates all work to Equalities. 
        """
        return Equalities.__ne__(self, comparator, trace, tab_width)

    def __str__(self):
        result = ""
        result += "\n"
        if self.autoSummarize:
            self.summarize()
        indentPerLevel = self._INDENT
        replicaPrefix = "Unspecified"
        misfitPrefix = self._LABEL_MISFIT + "! "
        self._map_hierarchy()
        for n in range(len(self)):
            lineItem = self[n]
            if self._hierarchy_map[n] != self._LABEL_MISFIT:
                if (self.contextualFormatting and
                    dropDownReplicaTag in lineItem.allTags):
                    lineItem.pre_format(prefix = replicaPrefix,
                                       left_tab = indentPerLevel * (1 + self._hierarchy_map[n]),
                                       right_tab = indentPerLevel)
                elif (self.contextualFormatting and
                      not n == (len(self)-1) and 
                      dropDownReplicaTag in self[n+1].allTags):
                    lineItem.pre_format(header = True,
                                       left_tab = indentPerLevel * (1 + self._hierarchy_map[n]),
                                       right_tab = indentPerLevel)
                else:
                    lineItem.pre_format(left_tab = indentPerLevel * (1 + self._hierarchy_map[n]),
                                       right_tab = indentPerLevel)
                result = result + str(lineItem) + "\n"
            else:
                mWidth = defaultScreenWidth - len(misfitPrefix) - indentPerLevel*2
                lineItem.pre_format(width = mWidth, left_tab = 0, right_tab = 0)
                stamped = " "*indentPerLevel + misfitPrefix + str(self[n])
                result = result + stamped + "\n"
        return result
    
    def add_line_to(self, line, *ancestor_tree, allow_duplicates=False):
        """


        Statement.add_line_to() -> None


        Method adds line to instance. ``ancestor_tree`` is a list of 1+ strings.
        The strings represent names of lines in instance, from senior to junior.
        Method adds line as a part of the most junior member of the ancestor
        tree.

        In the event an instance contains two sets of lines whose names match
        the ancestor tree, method will add line to the first such structure. 

        Method delegates recursive location work to Financials._spot_in_tree().

        Method will raise KeyError if instance does not contain the
        ancestor_tree structure in full. Method will throw BBAnalyticalError if
        ancestor_tree is empty.

        If ``allow_duplicates`` == False, method will raise error when dealing
        with a line that has a symmetrical name to one that's already in the
        instance. 

        EXAMPLE:
        
        >>> F = Statement()
        >>> ...
        >>> print(F)
        
        revenue ............................None
          mens  ............................None
            footwear .......................None
            
        >>> sandals = LineItem("sandals")
        >>> sandals.setValue(6, "example")
        >>> F.add_line_to(sandals, "revenue", "mens", "footwear")
        >>> print(F)
    
        revenue ............................None
          mens  ............................None
            footwear .......................None
              sandals..........................6
        """
        
        #ancestors is a list of names of ancestors
        self.build_tables()
        self._map_hierarchy()
        if not allow_duplicates:
            if line.name in self._top_level_names:
                raise bb_exceptions.BBAnalyticalError()
        
        i, j, parent = self._spot_in_tree(*ancestor_tree)
        line.setPartOf(parent)
        self.insert(j, line)
        #
        return (i, j, parent)

    def add_top_line(self, line, after=None, allow_duplicates=False):
        """


        Statement.add_top_line() -> None


        Insert line at the top level of instance. Method expects ``after`` to
        be the name of the item after which caller wants to insert line. If
        ``after`` == None, method appends line to self.

        If ``allow_duplicates`` == False, method will raise error when dealing
        with a line that has a symmetrical name to one that's already in the
        instance. 
        """
        self.build_tables()
        insert = True
        if not allow_duplicates:
            if line.name in self.table_by_name:
                raise ErrorOfSomeSort #bad duplicates!
        #
        #do all the real work
        self._map_hierarchy()
        line.setPartOf(self)
        j = None
        if not after:
            j = len(self)
        else:
            i = self.indexByName(after)
            j = self._hierarchy_map.index(0, i)
                #find the first top-level item after position ``i``. command
                #completely escapes any tree that contains ``after``
            j_line = self[j]
            if summaryTag in j_line.allTags:
                j = j + 1
                #if the next top-level line is a summary of the line at i, move
                #one step to the right. no nested trees can come up because we
                #are considering only top level items. 
        self.insert(j, line)
        
    def build_tables(self, *tagsToOmit):
        """


        Statements.build_tables() -> None


        Method goes through each line item in the instance and records its name
        and partOf in the instance's placement dictionaries. Method creates
        separate entries for cased and caseless versions of each name and partOf
        (but only to the extent they are different). 
        """
        tagsToOmit = set(tagsToOmit)
        # By default, scans everything
        
        self._clear_tables()
        
        for i in range(len(self)):
            line = self[i]
            lName = copy.copy(line.name)
            if lName:
                lNameCaseless = lName.casefold()
            lPart = copy.copy(line.partOf)
            if lPart:
                lPartCaseless = lPart.casefold()
            if tagsToOmit.intersection(set(line.allTags)) != set():
                continue
            if lName:
                try:
                    self.table_by_name[lName].add(i)
                except KeyError:
                    self.table_by_name[lName] = {i}
            if lNameCaseless != lName:
                try:
                    self.table_by_name[lNameCaseless].add(i)
                except KeyError:
                    self.table_by_name[lNameCaseless] = {i}
            if lPart in self._top_level_names:
                continue
            else:
                try:
                    self.table_by_part[lPart].add(i)
                except KeyError:
                    self.table_by_part[lPart] = {i}
                try:
                    self.table_by_part[lPartCaseless].add(i)
                except KeyError:
                    self.table_by_part[lPartCaseless] = {i}

    def build_custom_table(self, tagsToInclude, tagsToExclude=[],
                        container=None, keyTags=True):
        """


        Statement.build_custom_table() -> dict


        Method builds a dictionary (``D``) of items in container. D includes
        all items that contain at least one tag specified in tagsToInclude.
        D does not include any items that have any tagsToExclude. Presence of
        tagsToExclude trumps inclusion rule.

        Objects passed in as ``tagsToInclude`` and ``tagsToExclude`` must be
        iterable (lists, sets, etc.).

        D keys are item names; D values are static item indexes in the container
        (i.e., a change to the container ordering or size will not automatically
        change D values). 

        If ``container`` is None, method goes through the items in the instance.

        If ``keyTags`` is True, D includes keys for each tags in tagsToInclude;
        values for such items are a set of indexes for lines that include the
        tag.
        """
        if not container:
            container = self
        tagsToInclude = set(tagsToInclude)
        tagsToExclude = set(tagsToExclude)
        D = {}
        if keyTags:
            for tag in tagsToInclude:
                D[tag] = set()
        for i in range(len(container)):
            line = container[i]
            lName = copy.copy(line.name)
            tagsIn = set(line.allTags) & tagsToInclude
            tagsOut = set(line.allTags) & tagsToExclude
            if tagsOut != set():
                continue
            if tagsIn != set():
                try:
                    D[lName].add(i)
                except KeyError:
                    D[lName] = {i}
            if keyTags:
                for tag in tagsIn:
                    D[tag].add(i)
        return D           

    def clearInheritedTags(self, recur=True):
        """


        Statement.clearInheritedTags() -> None


        Method runs Tags.clearInheritedTags() on instance. If ``recur`` is True,
        does the same for every line in instance.
        """
        Tags.clearInheritedTags(self,recur)
        if recur:
            for L in self:
                L.clearInheritedTags(recur)

    def copy(self, enforce_rules=True):
        """


        Statement.copy() -> Fins


        Method returns a deep copy of the instance. If ``enforce_rules`` is
        True, the copy itself and all lineItems in copy conform to ``out``
        rules.

        Method first creates a shell for the copy by using Tags.copy(). Method
        then fills that shell with copies of any lineItems in the instance. 

        NOTE: Method resets dictionaries and summarizes the copy from scratch,
        so copying an unsummarized Financials object may return a new object
        that does not compare equal. Summarized instances and their copies
        should always compare equal, however.

        NOTE2: Line.parentObject pointers for lines below top level may not
        point to objects within the copy.
      
        The method generally tries to ensure some partOf consistency within the
        copy by manually setting all top-level lines to point to the copy. For
        detail lines, however, the method does not try to set line.parentObject
        to anything other than the default value for that line.copy().

        Can remedy by running updatePart() on every line in the result. Make
        sure to update dictionaries every time, or manually enter the new part
        in instance.table_by_part.
        """
        result = Tags.copy(self,enforce_rules)
        #Tags.copy returns a shallow copy of the instance w deep copies
        #of the instance tag attributes
        result.clear()
        #result is its own container; clearing it will not clear the seed
        #instance
        result._clear_tables()
        #create independent objects for any attributes that point to something
        #mutable or structured
        result._hierarchy_groups = None
        result._hierarchy_map = None
        result._top_level_names = copy.copy(self._top_level_names)
        tags_to_omit = []
##        tags_to_omit = [summaryTag,
##                        summaryTag.casefold(),
##                        dropDownReplicaTag,
##                        dropDownReplicaTag.casefold()]
        tags_to_omit = set(tags_to_omit)
        for line in self:
            problem_tags = tags_to_omit & set(line.allTags)
            if problem_tags != set():
                continue
            else:                    
                rL = line.copy(enforce_rules)
                if rL.partOf in result._top_level_names:
                    rL.setPartOf(result)
                result.append(rL)
        return result

##    def extrapolate_to(self,target):
##        """
##
##
##        Fins.extrapolate_to(target) -> Fins
##
##
##        Method returns new Financials object. Delegates all work to
##        Tags.extrapolate_to().
##        """
##        return Tags.extrapolate_to(self,target)

    def ex_to_special(self, target):
        """


        Statement.ex_to_special() -> Fins


        Method returns new Financials object, runs custom logic.

        First, make a container by creating a shallow copy of seed instance,
        clearing out any contents, clearing out that shell's inherited tags,
        and applying the non-inherited tags from the target to that shell.

        Second, fill the shell with lineitems.
         -- Step through seed instance
         -- If a line is in both seed and target, extrapolate seed line to
            target line to get a new line for result. If target LineItem is
            hands-off, use a copy of the target line.
         -- If a line is only in seed, add the line.copy(enforce_rules = True)
            of that line to result.
         -- If a line is only in target, add a copy to result if it's special;
            skip otherwise.

        Third, return result.
        """
        # Step 1: make a container
        tags_to_omit = [summaryTag,
                        summaryTag.casefold(),
                        dropDownReplicaTag,
                        dropDownReplicaTag.casefold()]
        seed = self
        alt_seed = copy.copy(seed)
        alt_seed.clear()
        #blending container level data only for now, so discard the complex,
        #recrusive contents from alt_seed. we will insert them independently
        #in step 2.
        result = alt_seed.copy(enforce_rules = True)
        #result is now a class-specific copy of alt_target, with all container
        #data in independent objects
        result = Tags.ex_to_special(result,target,mode = "at")
        #updates result with those target tags it doesnt have already. "at" mode
        #picks up all tags from target. other attributes stay identical because
        #Tags uses a shallow copy.
        
        # Step 2: fill the result container
        # go line by line
        alt_target.build_tables(*tags_to_omit)
        # Exclude summaries and replicas from the target
        tags_to_omit = set(tags_to_omit)
        for sL in self:
            if tags_to_omit & set(sL.allTags) != set():
                continue
            #shared line items. extrapolate seed on to target. 
            if sL.name in alt_target.table_by_name.keys():
                itL = min(alt_target.table_by_name[sL.name])
                tL = alt_target[itL]
                if tL.checkTouch():
                    newL = sL.extrapolate_to(tL)
                else:
                    newL = tL.copy(enforce_rules = False)
            else:
                newL = sL.copy(enforce_rules = True)
            if newL.partOf in result._top_level_names:
                newL.setPartOf(result)
                #to catch any new top-level seed lines
            result.append(newL)

        result.build_tables()

        target_only = set(alt_target.table_by_name.keys()) - set(result.table_by_name.keys())
        target_only = sorted(target_only)
        #enforce stable order to maintain consistency across runtimes
        for l_name in target_only:
            i_target = min(alt_target.table_by_name[l_name])
            line = alt_target[i_target]
            if self.checkOrdinary(line):
                continue
            else:
                #insert lines that are special, hardcoded, or do_not_touch
                i_result = result._spot_generally(line,alt_target,i_target)
                r_line = line.copy(enforce_rules = False)
                result.insert(i,r_line)
        
        # Step 3: return the container
        return result

    def increment(self, lines, *tagsToOmit, refresh=False, signature=None):
        """


        Statement.increment() -> None
        

        Increment matching lines, add new ones to instance. 
        ``tags_to_omit`` should be a set of tags for speed #<---------------------------------------------
        """
        if refresh:
            self.build_tables()

        if signature is None:
            signature = self.SIGNATURE_FOR_INCREMENTATION
        
        for i in range(len(lines)):
            # Walk through indeces because we may need them for positioning
            # later. 
            line = lines[i]

            # Skip uninformative or bad lines
            if not line.name:
                continue
            if set(tagsToOmit) & set(line.allTags):
                # Line has tags we want to omit
                continue

            # If we get here, the line has survived screening. We now have two
            # ways to add its information to the instance. Option A, is to
            # increment the value on a matching line. Option B is to copy the
            # line into the instance. We apply Option B only when we can't do
            # Option A.
            
            if line.name in self.table_by_name:
                # Option A: increment an existing line

                if line.value is None:
                    continue
                
                j = max(self.table_by_name[line.name])
                existing_line = self[j]
                
                starting_value = existing_line.value or 0
                # Replace ``None`` with 0
                new_value = starting_value + line.value
                existing_line.setValue(new_value, signature)
                
                existing_line.inheritTagsFrom(line)
                if tConsolidated not in existing_line.allTags:
                    existing_line.tag(tConsolidated)
                    
            else:
                # Option B: copy the line into instance
                new_line = line.replicate()
                
                if line.value is not None:
                    if tConsolidated not in new_line.allTags:
                        new_line.tag(tConsolidated)
                    # Pick up lines with None values, but don't tag them. We
                    # want to allow derive to write to these if necessary.

                i = self._spot_generally(new_line, lines, i)
                self._update_part(new_line)
                self.insert(i, new_line)
                self.build_tables()
                # Always build index after inserting something
                
    def indexByName(self, name):
        """


        Statement.indexByName() -> int


        Method returns index where first item with matching name is located in
        the instance. Checks for name matches on a caseless (casefolded) basis.
        If no such item exists, returns ValueError.

        NOTE: This method runs build_tables() on every call. It is expensive.
        You should manually retrieve results from the dictionaries for better
        performance.
        """
        name = name.casefold()
        self.build_tables()
        try:
            spots = self.table_by_name[name]
        except KeyError:
            raise ValueError
        spots = list(spots)
        spots.sort()
        i = spots[0]
        return i
    
    def inheritTags(self, recur=True):
        """


        Statement.inheritTags() -> None


        Method runs standard Tags routine and then inherits tags from every
        line item in the instance. Method skips lines with bookmark, summary, or
        drop-down replica tags. 
        """
        Tags.inheritTags(self, recur)
        tags_to_omit = [bookMarkTag,
                        bookMarkTag.casefold(),
                        dropDownReplicaTag,
                        dropDownReplicaTag.casefold(),
                        summaryTag,
                        summaryTag.casefold()]
        tags_to_omit = set(tags_to_omit)        
        for line in self:
            if tags_to_omit & set(line.allTags) != set():
                continue
            else:
                self.inheritTagsFrom(line)

    def reset(self):
        """


        Statement.reset() -> None


        Method erases all replicas and summaries, clears line values for all
        remaining lines, and then resets dictionaries.

        Method attempts to establish a state for financials that, when filled
        out by a business unit, will generate the same outcome as a different
        business unit with identical drivers and components. So, if a user was
        to copy a filled out business unit, running financials.reset() and then
        fill_out() on the copy would generate a Financials state equal to that
        of the original.
        """
        self._erase_managed_lines()
        for line in self:
            line.clear()
        self._clear_tables()
        self._hierarchy_map = None
        self._hierarchy_groups = None
    
    def summarize(self, *tagsToOmit):
        """


        Statement.summarize() -> None

        
        Add summaries and replicas. Ignore objects with tags to omit.
        """
        if tagsToOmit == tuple():
            tagsToOmit = [bookMarkTag.casefold()]
        
        self._manage_replicas(*tagsToOmit)
        self._manage_summaries(*tagsToOmit)
        self._update_summaries(*tagsToOmit)

    #*************************************************************************#
    #                          NON-PUBLIC METHODS                             #
    #*************************************************************************#

    def _clear_tables(self):
        """


        Statement._clear_tables() -> None


        Resets ``table_by_name`` and ``table_by_part`` to blank dictionaries
        """
        self.table_by_name = {}
        self.table_by_part = {}
        
    def _erase_managed_lines(self):
        """


        Statement._erase_managed_lines() -> None

        
        Method erases all lineitems with the dropDownReplicaTag and summaryTag.
        Uses ParsingTools.excludeByTag() to filter the managed lineitems.
        quickly.
        """
        ddrtag = dropDownReplicaTag
        stag = summaryTag
        mTags = [ddrtag,
                 ddrtag.casefold(),
                 stag,
                 stag.casefold()]
        newFin = self[:]
        newFin = ParsingTools.excludeByTag(newFin,*mTags)
        self.clear()
        self.extend(newFin)

    def _find_next_book_mark(self, refFins, refIndex=0):
        """

    
        Statement._find_next_book_mark() -> int


        Method returns index (``B``) of first bookmark in refFins located to the
        right of the refIndex.

        If no bookMark is found, B == -1.
        """
        for i in range(len(refFins))[refIndex:]:
            line = refFins[i]
            if bookMarkTag.casefold() in line.optionalTags:
                B = i
                break            
            else:
                continue
        else:
            #finished iterating through refFins, no bookmarks right of refIndex
            B = -1
        return B

    def _find_peer_or_senior(self, ref_index, end_index=None):
        """


        Statement._find_peer_or_senior() -> int


        Method locates the first peer or senior item to the right of ref_index
        and left of end_index. Method returns the index of that peer/senior
        relative to instance as a whole. 

        If end_index == None, method uses instance length as the end index.
        
        If no peer or senior exists in instance[ref_index, end_index), method
        returns end_index. When end_index is None, method returns instance
        length, so callers can insert an object into last position.

        Items A and B are peers if A's hierarchy value equals that of B. A is
        senior to B if A's hierarchy value is **lower** than B. Method builds
        hierarchy map on instance and walks it until it finds the first senior
        or peer. 
        """
        spot = None
        peer_level = self._hierarchy_map[ref_index]
        start = ref_index + 1
        #
        if end_index:
            end = end_index
        else:
            end = len(self._hierarchy_map)
        #
        for i in range(start, end):
            if self._hierarchy_map[i] <= peer_level:
                #line in position is equal or greater in senior to ref
                spot = i
                break
            else:
                continue
        else:
            spot = end
        return spot
    
    def _group_by_hierarchy(self, reprocess=True, attempts=50):
        """


        Statement._group_by_hierarchy() -> (groups, misfits)


        Method builds a list of lineItem groups.

        Each group represents a step down in the partOf hierarchy of the
        Financials object. The first group, index and level 0, contains
        lineitems whose ``partOf`` attribute matches an item in
        ``_top_level_names``. The seconds group, index and level 1, contains
        lineitems that are partOf level 0 lineItems. And so on.

        A lineItem is a ``misfit`` if it is not toplevel and not part of any other
        items in self. Misfits do not have a level in the partOf hierarchy.

        The method uses an internal function (categorizer()) to catch misfits
        and construct hierarchy lists.
        
        Categorizer() accepts two arguments:
          -- a container, and
          -- a pre-built or blank hierarchy (in the form of a list of lists).
        Categorizer() returns the resulting hierarchy and the list of misfits.

        Categorizer scans the container right to left. For each item,
        categorizer() checks whether the hierarchy it received contains an
        appropriate group. Appropriate groups are those that contain objects
        that are partOf a prior group or the **instance's** (as opposed to the
        hierarchy argument's)``_top_level_names`` list. Categorizer appends a new
        level (list) whenever it encounters an item that's part of the lowest
        existing level.

        When Categorizer() encounters an item that has no top in the
        then-existing hierarchy object, Categorizer() classifies such item as a
        misfit. As a result, the function applies the ``misfit`` label to
        detail objects whose top follows them in the container. Because
        ``misfits`` are strictly defined as lineitems that do not have a proper
        top in the container at all, this classification is an error when
        applied to misordered items. 

        If reprocess == True, the method attempts to control for the
        scenario described above by running Categorizer() repeatedly. The method
        starts by running Categorizer twice: first on the instance's own list
        items, and then on the misfits produced by the first run. The method
        provides the hierarchy procuded by the first run as a starting point to
        the second. At that time, the hierarchy includes the parents of
        misordered details, unless the parents are also misordered.
        
        If misfits exist after the second pass, the method keeps runs
        categorizer() up to ``attempts`` times.

        If the misfit list stops changing prior to the last reprocessing attempt,
        the method stops running categorizer(). A stable misfit list means that
        no items in the list are partOf an existing lineItem. In other words,
        the misfits cannot properly fit into the existing hierarchy regardless
        of the order of review (though they may form a coherent hierarchy of
        their own).
        
        If items in a container are ordered in reverse [4,3,2,1], each
        categorizer() pass will place the top-most item in a hierarchy. The
        remaining items will appear as misfits until the next pass places one.
        Accordingly, 50 iterations should clean up any ordering errors in
        hierarchies with less than 50 levels.

        NOTE: The hierarchy produced by this method contains pointers to the
        **actual** objects in the instance list. This allows other methods to
        check lineitem membership in the groups. 
        
        """
        two_level = [list(), list()]
        # Create a starter lattice. 
        
        first_hierarchy, first_misfits = self._categorize(self, two_level)
        result = (first_hierarchy, first_misfits)
        
        second_hierarchy, second_misfits=self._categorize(first_misfits, first_hierarchy)

        if reprocess == False:
            self._hierarchy_groups = first_hierarchy
            
        elif (reprocess and second_misfits != []):

            misfit_delta = []
            counter = 0

            while counter < attempts:

                for L in first_misfits:
                    if L not in second_misfits:
                        misfit_delta.append(L)
                    else:
                        continue

                if misfit_delta == []:
                    break
                # Stop working as soon as you go through a cycle without
                # placing an item in the hierarchy.
                
                first_hierarchy = second_hierarchy
                first_misfits = second_misfits
                second_hierarchy, second_misfits = self._categorize(first_misfits, first_hierarchy)
                counter +=1    

            # While loop is over.
            result = (second_hierarchy, second_misfits)
            self._hierarchy_groups = second_hierarchy
        else:
            self._hierarchy_groups = second_hierarchy
        
        return result
    
    def _categorize(self, container, hierarchy):
        """


        Statement._categorize() -> (list, list)

        
        Return completed hierarchy and a list of misfits. Misfits will be an
        empty list if all items in container fit into a hierarchy. Utility
        function for _group_by_hierarchy().
        """
        misfits = []
        
        for line in container:

            if line.partOf in self._top_level_names:
                hierarchy[0].append(line)
                
            else:
                depth = len(hierarchy)

                for n in range(depth):
                    try: 

                        for potential_parent in hierarchy[n]:
                            
                            if not line.partOf == potential_parent.name:
                                continue
                            else:
                                # Current line is part of an nth-level line. Now
                                # that we know the line's relationship to the
                                # container structure, we have to put it in the
                                # right group. 
                                
                                #check if there is an n+1 level
                                if not n == (depth - 1):
                                    #there is a deeper level
                                    #append current lineitem to the next level
                                    hierarchy[n+1].append(line)
                                    raise PlacementSuccess
                                
                                else:
                                    #there is not a deeper level, so make one
                                    new_level = []
                                    new_level.append(line)
                                    hierarchy.append(new_level)
                                    raise PlacementSuccess
                            
                    except PlacementSuccess:
                        break

                else:
                    #finished going through hierarchy, didnt find the right
                    #top at any level. could be because proper top follows
                    #after unknownLineItem or because proper top is missing
                    #completely. in either event, the current line item is
                    #a misfit
                    misfits.append(line)
                    
        return (hierarchy, misfits)

    def _manage_replicas(self, *tagsToOmit):
        """


        Statement._manage_replicas() -> None


        Add replicas for lines with details and a filled-in value. Increment
        existing replicas where the existing parent picks up new value. 

        For example, suppose a line "Shoes" has a value of 10. Suppose "Shoes"
        also includes a detail line called "Sandals", with a value of 5. To make
        sure that total Shoes value is 15, this method will copy "Shoes", add
        that copy as a detail (replica) to "Shoes", and then set the parent
        line to zero.

        As a result, "Shoes" will now have two details:
        
        Shoes:
         - Shoes: 10
         - Sandals : 5

        and will total 15. The top Shoes line will have a value of None.
        """
        # This method inserts objects into a list, so walk through a fixed copy
        # of this list. If a line is eligible, check if it has a replica. If it
        # does, increment the replica by the line's value, then zero the line.
        # if the line doesn't have a replica, insert one.

        signature = self.SIGNATURE_FOR_MANAGING_REPLICAS
        fixed_order = self[:]
        fixed_count = len(fixed_order)
        off_set = 0
        
        for position in range(0, (fixed_count-1)):

            line = fixed_order[position]
            neighbor = fixed_order[position+1]
            existing_replica = None
            first_detail = None

            #0) kick out lines that dont have a value
            if line.value is None:
                continue
            #1) kick out lines that dont have details
            if neighbor.partOf == line.name:
                first_detail = neighbor
            else:
                continue
            
            #2) kick out lines that we have to explicitly omit
            if set(tagsToOmit) & set(line.allTags) != set():
                continue

            #3) kick out replicas themselves
            if (line.name == line.partOf 
                or dropDownReplicaTag in line.allTags):
                continue
            
            if first_detail.name == line.name:
                existing_replica = first_detail
                #detail has the same name as line, detail is a replica

            if existing_replica:

                #if replica exists, increment it by line value. 
                f3 = ParsingTools.valueReplacer
                new_value = f3(existing_replica.value, 0, None) + line.value
                #update replica signature block to exactly match the top
                existing_replica.modifiedBy = copy.copy(line.modifiedBy)
                existing_replica.setValue(new_value, signature)

                existing_replica.inheritTagsFrom(line, None)
                #when calling inherit on a replica, override defaults and
                #copy as much as possible. passing in None results in
                #doNotInherit = (None,)

                if not dropDownReplicaTag in existing_replica.allTags:
                    existing_replica.tag(dropDownReplicaTag)
                line.setValue(0, signature)
                continue

            else: 

                # Line needs a replica. create and insert one. 

                new_replica = LineItem.copy(line, enforce_rules=False)
                # Keep enforce_rules False so that both drop down replica and
                # the original lineItem retain all tags (including those not
                # inheritable ``out``, like specialTag).
                
                new_replica.tag(dropDownReplicaTag)
                new_replica.setPartOf(line)
                if new_replica.value == line.value:
                    #check that replica picked up value before zeroing original 
                    line.setValue(0, signature)
                else:
                    c = "replica value does not equal line."
                    raise bb_exceptions.IOPMechanicalError(c, line, new_replica)
                self.insert(position + off_set + 1, new_replica)
                off_set = off_set + 1
                
    def _manage_summaries(self, *tagsToOmit):
        """


        Statement._manage_summaries() -> None


        This method maintains summary lines.
        
        The method evaluates whether a given detail-level lineitem has a summary
        to increment. The method does not evaluate specific summary needs of
        topLevel items. manageSummaries() also skips lineitems that carry
        tagsToOmit.
        
        Algorithm:
          1)  Iterate through a list that includes all items in the instance
              except those with tagsToOmit.

          2)  If the item is topLevel (its .partOf is in _top_level_names), no need
              for summary, go on to next one. 

          3)  If the item is detail, proceed to check whether it has a proper
              summary to increment.

          4)  To do so, aggregate lineitems in self that have the summaryTag.
              Method refreshes this list of existing summaries every time it
              encounters a detail line item to make sure that the summaries
              include those inserted by manageSummaries() since last call. 
        
          5)  Check if any of the existing summaries is the proper summary for
              the detail item. A proper summary is one whose name ends with
              the .partOf value of the detail.

          6)  If the detail does not match any existing summaries, create a
              proper summary for it. Method creates an instance of lineitem,
              tags it w a summaryTag, gives it a proper summary name.

          7)  Place the new summary immediately prior to the next peer in
              the hierarchy.

        The summary precedes the first lineitem that is at the same level of the
        hierarchy as its lineitem. That is, the summary follows all details of
        the lineitem it summarizes, as well as their details. The method uses
        instance._hierarchy_map to locate the proper insertion position. 
        """
        tagsToOmit = set(tagsToOmit)
        tagsToOmit.add(summaryTag)
        existingSummaries = self.build_custom_table([summaryTag])
        for i in existingSummaries[summaryTag]:
            summaryLine = self[i]
            summaryLine.setValue(0,"update reset")
        startingSelf = self[:]
        #step through a slice because will do insertions
        for L in startingSelf:
            if L.partOf in self._top_level_names:
                continue
            if set(L.allTags) & tagsToOmit != set():
                continue
            summaryName = self.SUMMARY_PREFIX + " " + L.partOf
            summaryName = summaryName.casefold()
            if summaryName in existingSummaries.keys():
                continue
            else:
                #make and insert the summary lineitem
                newSummary = LineItem(name = summaryName)
                newSummary.tag(summaryTag,skipTag,field = "req")
                self.build_tables()
                tPlaces = list(self.table_by_name[L.partOf])
                tPlaces.sort()
                top = self[tPlaces[0]]
                if top.parentObject:
                    newSummary.setPartOf(top.parentObject)
                else:
                    newSummary.partOf = top.partOf
                newSummary.inheritTagsFrom(L, *uninheritableTags)
                self._map_hierarchy()
                #insertion logic follows
                #
                #summary should go in before the first line with an H value that
                #is lower than that of L; this line may be a peer or senior of
                #L's parentObject
                #
                #for example, in situations where the parent object is the last
                #detail of its own parent, the different between H values for L
                #and the next superior line is 2 or more.
                #
                #find L in self (**not** startingSelf - location could be
                #arbitrarily different due to prior insertions)
                spots_L = list(self.table_by_name[L.name])
                spots_L.sort()
                iL = spots_L[0]
                hL = self._hierarchy_map[iL]
                j = None
                rightMap = self._hierarchy_map[(iL+1):]
                for spot in range(len(rightMap)):
                    newH = rightMap[spot]
                    if newH < hL:
                        j = spot+(iL+1)
                        break
                    else:
                        continue
                else:
                    j = len(self._hierarchy_map)
                #if this doesnt work, can try finding all senior Hs and running
                # a min on the list, though that seems like overkill
                self.insert(j, newSummary)
                existingSummaries = self.build_custom_table([summaryTag])
                continue
        self.dSummaries = existingSummaries
        #Upgrade: summarize unlabelled line items from subs
        
    def _map_hierarchy(self):
        """


        Statement._map_hierarchy() -> None

        
        Builds a list of position in hierarchy by item. Stores result on
        instance._hierarchy_map.
        """
        self._group_by_hierarchy(reprocess=True)
        #build map from scratch on every call
        self._hierarchy_map = []
        for lineItem in self:
            for n in range(len(self._hierarchy_groups)):
                if lineItem in self._hierarchy_groups[n]:
                    self._hierarchy_map.append(n)
                    break
                else:
                    continue
            else:
                self._hierarchy_map.append(self.LABEL_MISFIT)
        if not len(self._hierarchy_map) == len(self):
            c = "map does not properly reflect hierarchy"
            raise bb_exceptions.IOPMechanicalError()

    def _match_book_mark(self, book_mark, double_check=True):
        """


        Statement._match_book_mark() -> int


        Method returns index ("B") of first bookmark in self that is
        name-symmetric to book_mark.

        Raise BookMarkError if instance does not have the same mark. 
        """
        #UPGRADE-S: could potentially run faster on bookmark/line __hashes__
        B = -1
        try:
            places = list(self.table_by_name[book_mark.name])
            places.sort()
            B = places[0]
            return B
        except KeyError:
            if double_check:
                self.build_tables()
                B = self._match_book_mark(mark, double_check=False)
                # Must specify double_check is false, otherwise loops forever.
                return B
            else:
                raise bb_exceptions.BookMarkError

    def _spot_by_book_mark(self, container, index):
        """


        Statement._spot_by_book_mark() -> int
        

        L is always suitable for list.insert(L,obj). 

        Method returns the index of the first bookMark that is both in
        container and in self. If no such bookMark is found, L == -1.
        """
        L = None
        i = self._find_next_book_mark(container, index)
        if i == -1:
            L = len(self)
            # No more bookmarks in refFins, spot is end of instance.
        else:
            ref_mark = container[i]
            try:
                L = self._match_book_mark(ref_mark)
            except BookMarkError:
                #self missing the first bookmark found in refFins after
                #refIndex; find next bookMark, try that
                L = self._spot_by_book_mark(container, ref_mark)
        return L

    def _spot_generally(self, line, container, index):
        """


        Statement._spot_generally() -> int


        Method returns the positive integer index (``L``) prior to which the
        line at container[index] should be inserted into this instance.

        NOTE: Method requires index parameter to expedite analysis.
        """
        refPart = line.partOf
        if refPart in self._top_level_names:
            L = self._spot_by_book_mark(container, index)
            return L
        else:
            try:
                #check if line is partOf something in self
                places = self.table_by_name[refPart]
                #places is a set of positions; to get last position, find
                #largest value in set
                ref_spot = max(places)
                self._map_hierarchy()
                L = self._find_peer_or_senior(ref_spot)
                
            except KeyError:
                #line.partOf not in self.fins.table_by_name;
                #place based on bookmarks
                L = self._spot_by_book_mark(container, index)
            finally:
                return L

    def _spot_in_tree(self, *ancestor_tree, start=None, end=None):
        """


        Statement._spot_in_tree() -> (i, j, parent)


        Method locates a position in index ``j`` that represents the last line
        in the most junior member of the ancestor_tree. The ``parent`` is that
        most junior member. ``i`` is the parent's location.

        Inserting an object into instance at j will append it to the most junior
        member of the ancestor_tree.

        Method expects:

        -- ``ancestor tree`` to be a tuple of 1+ strings that match the names of
           lines in instance,
        -- ``start`` to be the starting index for a search, and
        -- ``end`` to be the ending index for a search.

        Method will raise a KeyError if instance[start, end] does not contain
        the ancestor_tree structure.

        Method will raise an error if ancestor_tree is blank on the first call.
        """
        i = start
        j = end
        parent = self
        if not ancestor_tree:
            c = "Method requires a tree of at least name."
            raise bb_exceptions.BBAnalyticalError(c)
        if ancestor_tree:
            parent_name = ancestor_tree[0]
        i = self.indexByName(parent_name)
        parent = self[i]
        j = self._find_peer_or_senior(i)
        
        descendants = ancestor_tree[1:]
        if descendants:
            i, j, parent = self._spot_in_tree(*descendants, start=i, end=j)
            
        return (i, j, parent)
    
    def _update_part(self, refLine):
        """


        Statement._update_part() -> None


        Method sets refLine's partOf to a suitable parent (matching by name)
        in the instance. If no suitable parent exists, sets refLine to be a top
        level item.
        """
        refPart = copy.copy(refLine.partOf)
        if refPart in self.table_by_name.keys():
            places = list(self.table_by_name[refPart])
            places.sort()
            top = self[places[-1]]
            refLine.setPartOf(top)
        else:
            refLine.setPartOf(self)

    def _update_summaries(self, *tagsToOmit, refresh=False):
        """


        Statement._update_summaries() -> None


        For each line without a bad tag, method increments the name-appropriate
        summary. Method assumes all necessary summaries exist and skips any
        lines without one.

        If ``refresh`` is False (default), method requires someone (usually
        self.manageSums3) to update the self.dSummaries dictionary prior to
        incrementation. The manul update allows for speed gains but **creates
        potential for error**.

        If ``refresh`` is True, method builds a new existingSummaries dict on
        call and saves it to self.dSummaries. 
        """
        usSig = self.SIGNATURE_FOR_SUMMARY_UPDATES
        tagsToOmit = set(tagsToOmit)
        existingSummaries = self.dSummaries
        
        if refresh:
            existingSummaries = self.build_custom_table([summaryTag])

        for i in existingSummaries[summaryTag]:
            summaryLine = self[i]
            if summaryLine.value:
                summaryLine.setValue(0, self.SIGNATURE_FOR_SUMMARY_RESET)
                
        #no insertions so ok to use self:
        for L in self:
            
            if not L.value:
                continue
            if L.partOf in self._top_level_names:
                continue
            if set(L.allTags) & tagsToOmit != set():
                continue

            summaryName = self.SUMMARY_PREFIX + " " + L.partOf
            summaryName = summaryName.casefold()

            try:
                places = existingSummaries[summaryName]
                spot = min(places)
                matchingSummary = self[spot]
                sValue = matchingSummary.value or 0
                # Replace None with 0
                newValue = sValue + L.value
                
                matchingSummary.setValue(newValue,usSig)
                matchingSummary.inheritTagsFrom(L, *uninheritableTags)
                continue
            
            except KeyError as X:
                c = "Summary line ``%s`` expected but does not exist"
                c = c % summaryName
                raise bb_exceptions.HierarchyError(c)

        if refresh:
            self.dSummaries = existingSummaries
        

