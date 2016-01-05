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

import bb_exceptions

from data_structures.system.tags import Tags
from .equalities import Equalities





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

class Statement(Tags, Equalities):
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
    details
    POSITION_SPACING
    
    FUNCTIONS:
    append()
    copy()                return deep copy
    extend()
    find()
    increment()           add data from a collection of objects
    reset()               clear values
    ====================  ======================================================
    """
    keyAttributes = ["details"]
    # Should rename this comparable_attributes

    _INDENT = 2
   
    def __init__(self, name=None, spacing=100):
        Tags.__init__(self, name=name)        
        self.details = dict()

        if spacing < 1:
            raise error
        if not isinstance(spacing, int):
            raise error

        self.POSITION_SPACING = spacing
        
    def __eq__(self, comparator, trace=False, tab_width=4):
        """


        Statement.__eq__() -> bool


        Method explicitly delegates work to Equalities.__eq__(). The Financials
        class defines keyAttributes as an empty list at the class level, so
        Equalities will run pure-play list.__eq__() comparison logic, but still
        support tracing.
        """
        return Equalities.__eq__(self, comparator, trace, tab_width)
        #<------------------------------------------------------------------------------------------------------------------------need to revise and customize for Line
            #line should include tags? value? (track existing line)
    
    def __ne__(self, comparator, trace=False, tab_width=4):
        """


        Statement.__ne__() -> bool


        Method explicitly delegates all work to Equalities. 
        """
        return Equalities.__ne__(self, comparator, trace, tab_width)

    def __str__(self):
        result = "\n"
        for line in self.get_ordered():
            result += str(line)
        
        return result
                
    def find_first(self, *ancestor_tree):
        """


        Statement.find_first() -> Line or None


        Return a detail that matches the ancestor tree or None. 
        """
        result = None

        caseless_root_name = ancestor_tree[0].casefold()
        root = self.details.get(caseless_root_name)

        if root:
            remainder = ancestor_tree[1:]
            if remainder:
                result = root.find_first(*remainder)
            else:
                result = root
                # Caller specified one criteria and we matched it. Stop work.

        else:
            for detail in self.get_ordered():
                result = detail.find_first(*ancestor_tree)
                if result is not None:
                    break
                else:
                    continue

        return result

    def find_all(self, *ancestor_tree):
        """

        -> list
        """
        result = []

        caseless_root_name = ancestor_tree[0].casefold()
        root = self.details.get(caseless_root_name)

        if root:
            remainder = ancestor_tree[1:]
            if remainder:
                lower_nodes = root.find_all(*remainder)
                if lower_nodes:
                    result.extend(lower_nodes)
            else:
                # Nothing left, at the final node
                node = root
                result.append(node)
        else:
            for detail in self.get_ordered():
                lower_nodes = detail.find_all(*ancestor_tree)
                if lower_nodes:
                    result.extend(lower_nodes)
                    continue

        return result

    def add_line(self, new_line, position=None):
        """

        -> int
        #return position where we inserted?

        #if position is None, adds to end (max position + spacer)
        """
        
        self._inspect_line_for_insertion(new_line)

        if position is None:
            self.append(new_line)
            
        else:
            new_line.position = position

            if not self.details:
                self._bind_and_record(new_line)
                # This block differs from append in that we preserve the
                # requested line position
                
            else:
                ordered = self.get_ordered()
                
                if new_line.position < ordered[0].position or ordered[-1].position < new_line.position:

                    self._bind_and_record(new_line)
                    # Requested position falls outside existing range. No
                    # conflict, insert line as is.

                else:

                    # Potential conflict in positions. Spot existing, adjust as
                    # necessary. 
                    for i in range(len(ordered)):
                        existing_line = ordered[i]
                        
                        if new_line.position < existing_line.position:
                            self._bind_and_record(new_line)
                            break

                        elif new_line.position == existing_line.position:
                            
                            tail = ordered[i:]
                            for pushed_line in tail:
                                pushed_line.position += self.POSITION_SPACING

                            self._bind_and_record(new_line)
                            break

                        else:
                            continue            
            

                
    def append(self, line):
        """
        -> None

        
        """
        self._inspect_line_for_insertion(line)
        # Will throw exception if problem
        
        ordered = self.get_ordered()
        if ordered:
            last_position = ordered[-1].position
        else:
            last_position = 0
        new_position = last_position + self.POSITION_SPACING
        line.position = new_position

        self._bind_and_record(line)
        
    def get_ordered(self):
        """
        -> list

        Return a list of details in order of relative position
        """
        result = sorted(self.details.values(), key = lambda line: line.position)
        return result

    def get_full_ordered(self):
        """

        -> list

        Return ordered list of lines and their details. 
        """
        result = list()
        for line in self.get_ordered():
            if line.details:
                increment = line.get_full_ordered()
                result.extend(increment)
            else:
                result.append(line)
        return result
        
    def add_line_to(self, line, *ancestor_tree):
        """

        **LEGACY INTERFACE: use add_line() instead**

        Statement.add_line_to() -> None


        Method adds line to instance. ``ancestor_tree`` is a list of 1+ strings.
        The strings represent names of lines in instance, from senior to junior.
        Method adds line as a part of the most junior member of the ancestor
        tree.

        Method will throw KeyError if instance does not contain the ancestor tree
        in full. 

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
        if ancestor_tree:
            detail = self.find(*ancestor_tree)
            if detail is None:
                raise KeyError(ancestor_tree)
            else:
                detail.add_line(line)
        else:
            self.append(line)

    def add_top_line(self, line, after=None):
        """


        **LEGACY INTERFACE: use add_line() instead**

        Statement.add_line_to() -> None


        Statement.add_top_line() -> None


        Insert line at the top level of instance. Method expects ``after`` to
        be the name of the item after which caller wants to insert line. If
        ``after`` == None, method appends line to self.
        """
        if after:
            new_position = self.details[after].position + self.POSITION_SPACING
            self.add_line(line, new_position)
        else:
            self.append(line)
    
    def clearInheritedTags(self, recur=True):
        """


        Statement.clearInheritedTags() -> None


        Method runs Tags.clearInheritedTags() on instance. If ``recur`` is True,
        does the same for every line in instance.
        """
        Tags.clearInheritedTags(self, recur) #<-------------------------------------------------------------check what this does
        if recur:
            for line in self.details.values():
                line.clearInheritedTags(recur) #<----------------------------------------------------------------------------------------------review

    def copy(self, enforce_rules=True):
        """


        Statement.copy() -> Statement


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
        result = Tags.copy(self, enforce_rules)
        # Tags.copy returns a shallow copy of the instance w deep copies
        # of the instance tag attributes.
        result.details = dict()
        
##        tags_to_omit = [summaryTag,
##                        summaryTag.casefold(),
##                        dropDownReplicaTag,
##                        dropDownReplicaTag.casefold()]
        tags_to_omit = set()
        
        for line in self.get_ordered():
            problem_tags = tags_to_omit & set(line.allTags)
            if problem_tags != set():
                continue
            else:                    
                rL = line.copy(enforce_rules)
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
        return result #<--------------------------------------------------------------------------------------------------------------rewrite

    def increment(self, matching_statement, *tagsToOmit, refresh=False, consolidating=False):
        """


        Statement.increment() -> None
        

        Increment matching lines, add new ones to instance. 
        ``tags_to_omit`` should be a set of tags for speed #<---------------------------------------------

        #algo:
        #add lines where they are missing
        #increment lines where they match
        #repeat recursively
        """
        for name, external_line in matching_statement.details.items():
            # ORDER SHOULD NOT MATTER HERE
            
            if set(tagsToOmit) & set(external_line.allTags):
                continue

            # If we get here, the line has survived screening. We now have two
            # ways to add its information to the instance. Option A, is to
            # increment the value on a matching line. Option B is to copy the
            # line into the instance. We apply Option B only when we can't do
            # Option A.
            
            own_line = self.details.get(name)

            if own_line:
                # Option A
                own_line.increment(external_line, consolidating=consolidating)

            else:
                # Option B
                local_copy = external_line.copy(enforce_rules=False)
                # Dont enforce rules to track old line.replicate() method
                
                if consolidating:
                    if external_line.value is not None:
                        if tConsolidated not in local_copy.allTags:
                            local_copy.tag(tConsolidated)
                    # Pick up lines with None values, but don't tag them. We
                    # want to allow derive to write to these if necessary.

                self.add_line(local_copy, local_copy.position)
                # For speed, could potentially add all the lines and then fix
                # positions once.         

    #think about what happens when you increment one statement with 5 lines by another w 5 lines and the lines are same rel position #<-------------------

    def extend(self, lines):
        """
        -> None
        lines can be either an ordered container or a Statement object
        """
        try:
            for line in lines:
                self.append(line)
        except TypeError:
            for line in lines.get_ordered():
                self.append(line)
                
    # Can further improve speed by eliminating overwrite protection
    
##    def indexByName(self, name):
##        """
##
##
##        **LEGACY INTERFACE: use direct lookup
##        
##        Statement.indexByName() -> int
##
##
##        Method returns index where first item with matching name is located in
##        the instance. Checks for name matches on a caseless (casefolded) basis.
##        If no such item exists, returns ValueError.
##
##        NOTE: This method runs build_tables() on every call. It is expensive.
##        You should manually retrieve results from the dictionaries for better
##        performance.
##        """
##        line = self.details.get(name) or self.details.get(name.casefold())
##        if not line:
##            raise ValueError    
##        return line.position
##
##    #<-----------------------------------------------------------------------------------------------------------can add index operations
##    #(get_item and set_item)
    
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

        for line in self.details.values(): #<-----------------------------------------------------MUST SORT HERE to make sure order is constant
            if tags_to_omit & set(line.allTags) != set():
                continue
            else:
                self.inheritTagsFrom(line)

        #<-----------------------------------------------------------------------------------------------------------rewrite
        #should just pick up lines from details

    def reset(self):
        """


        Statement.reset() -> None


        Clear all values, preserve line shape.
        """
        #clears values, not shape
        for line in self.details.values():
            line.clear()
        
    #*************************************************************************#
    #                          NON-PUBLIC METHODS                             #
    #*************************************************************************#

    def _bind_and_record(self, line):
        line.setPartOf(self)
        self.details[line.name] = line
            
    def _inspect_line_for_insertion(self, line):
        if not line.name:
            c = "Cannot add nameless lines."
            raise bb_exceptions.BBAnalyticalError(c)

        if line.name in self.details:
            c = "Implicit overwrites prohibited."
            raise bb_exceptions.BBAnalyticalError(c)
        
    def _repair_order(self, starting=0):
        """
         -> list

         return ordered items
        if starting is 0 and position spacing is 1, will create consecutively numbered positions
        """
        
        # Build table by position
        ordered = list()
        by_position = dict()

        for line in self.details.values():
            entry = by_position.setdefault(line.position, list())
            entry.append(line)

        # Now, go through the table and build a list
            #can then just assign order to the list

        for position in sorted(by_position):
            lines = by_position[position]
            lines = sorted(lines, lambda x : x.name)
            ordered.extend(lines)

        # Now can assign positions
        for i in range(len(ordered)):
            line = ordered[i]
            new_position = starting + (i * self.POSITION_SPACING) #<---------------------------fix this
            line.position = new_position

        # Changes lines in place.
        return ordered
    
        # Can also do more complex stuff where you only add spacing on conflicts,
        # so the result is uneven   
