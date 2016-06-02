#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: data_structures.modelling.components
"""

Module defines Components class, a container for business units. 
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
Components            Tags-type container that stores business units
====================  ==========================================================
"""




#imports
import copy
import time

import bb_exceptions
import tools.for_tag_operations

from data_structures.system.tags import Tags

from .equalities import Equalities




#globals
#n/a

#classes
class Components(dict, Equalities):
    """

    The Components class defines a container that stores BusinessUnit objects
    keyed by their bbid. Components objects descend from the Tags class to
    support inheritance and extrapolation. Specifically, the tags on a
    Components instance, when maintained properly, should show whether any of
    the business units within that instance requires special extrapolation.
    
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    by_name               dict; keys are unit names, values are unit bbids
    keyAttributes         list; CLASS; keep empty to follow standard dict logic

    FUNCTIONS:
    add_item()            adds an object to self, keyed under obj's bbid
    clearInheritedTags()  runs Tags method and then repeats for each component
    copy()                returns deep copy of instance and contents
    find_bbid()           return bbid that contains a known string
    get_living()          returns a bbid:bu dict of all bus that are alive
    getOrdered()          legacy interface for get_ordered() 
    get_ordered()         returns a list of values, ordered by key
    get_tagged()          return a dict of units with tags
    inheritTags()         runs default routine, then inherits from all comps
    refresh_names()       clear and rebuild name-to-bbid dictionary
    remove_item()         remove an item from components
    ====================  ======================================================
    """
    #
    #while at first Components would seem to be a natural contender to use the
    #collections.ChainMap structure, the direction of information flow across
    #the Blackbird tree and the number of components create substantial
    #obstacles to semantically meaningful implementation.
    #

    #
    keyAttributes = []
    #keyAttributes should remain an explicit empty list to maintain dictionary
    #comparison logic
        
    def __init__(self,name = "Components"):
        dict.__init__(self)
        Equalities.__init__(self)
        self.by_name = dict()
        self.tags = Tags(name)

    def __eq__(self, comparator, trace = False, tab_width = 4):
        """


        Components.__eq__(comparator[, trace = False[, tab_width = 4]]) -> bool

        
        Call Equalities.__eq__ explicitly to bypass dict.__eq__ and support
        tracing.    
        """
        return Equalities.__eq__(self,comparator, trace, tab_width)

    def __ne__(self, comparator, trace = False, tab_width = 4):
        """


        Components.__ne__(comparator, [trace = False[, tab_width = 4]]) -> bool


        Explicit call to Equalities.__ne__ 
        """
        return Equalities.__ne__(self, comparator, trace, tab_width)


    def __str__(self, lines = None):
        """


        Components.__str__(lines = None) -> str


        Method concatenates each line in ``lines``, adds a new-line character at
        the end, and returns a string ready for printing. If ``lines`` is None,
        method calls _get_pretty_lines() on instance. 
        """
        if not lines:
            lines = self._get_pretty_lines()
        line_end = "\n"
        result = line_end.join(lines)
        return result        
        
    def add_item(self, bu):
        """


        Components.add_item(bu) -> None


        Method adds bu to the instance, keyed as bu.id.bbid. If bu does not
        specify a bbid, method raises IDError.

        Method also registers each unit's id under the unit's name in
        instance.by_name. 
        """
        if not bu.id.bbid:
            c = "Cannot add a component that does not have a valid bbid."
            raise bb_exceptions.IDError(c)
        bu.setPartOf(self)
        self[bu.id.bbid] = bu
        if bu.tags.name:
            self.by_name[bu.tags.name] = bu.id.bbid

    def clearInheritedTags(self, recur = False):
        """


        Components.clearInheritedTags([recur = False]) -> None


        Method runs Tags.clearInheritedTags(). If recur == True, method then
        clears inherited tags for every component in self.getOrdered(). 
        """
        self.tags.clearInheritedTags()
        if recur:
            for C in self.getOrdered():
                C.clearInheritedTags(recur=True)

    def copy(self, enforce_rules=True):
        """


        Components.copy() -> Components


        Method returns a deep copy of components. Uses Tags.copy() to create a
        shell. Method then sets result.by_name to a blank dictionary and adds a
        copy of each unit in the instance to the result. 
        """
        result = Tags.copy(self, enforce_rules=True)
        #
        #customize container
        result.clear()
        result.by_name = dict()
        #
        #fill container (automatically add names)
        for C in self.getOrdered():
            rC = C.copy(enforce_rules)
            result.add_item(rC)
        return result

    def find_bbid(self, snippet):
        """


        Components.find_bbid(snippet) -> uuid


        Method returns first bbid in instance keys that contains the snippet.
        Snippet should be a string. Method returns None if no id in instance
        contains snippet. 
        """
        result = None
        for bbid in self:
            if snippet in str(bbid):
                result = bbid
                break
            else:
                continue
        #
        return result

    def get_living(self):
        """


        Components.get_living() -> dict


        Method returns a dictionary by bbid of every object in instance that
        has life.alive == True.
        """
        result = dict()
        for (bbid, bu) in self.items():
            if bu.life.alive:
                result[bbid] = bu
            else:
                continue
        #
        return result
    
    def getOrdered(self):
        """


        Components.getOrdered() -> list


        Legacy interface for components.get_ordered()
        """
        return self.get_ordered()

    def get_ordered(self):
        """


        Components.get_ordered() -> list


        Method returns a list of every value in the instance, ordered by key. 
        """
        result = []
        for k in sorted(self.keys()):
            bu = self[k]
            result.append(bu)
        return result

    def get_tagged(self, *tags, pool=None, recur=False):
        """


        Components.get_tagged() -> dict


        Return a dictionary of units (by bbid) that carry the specified tags.
        
        If ``pool`` is None, uses instance.values(). Delegates all selection
        work to tools.for_tag_operations.get_tagged()

        If ``recur`` is True, method runs recursively through all values in
        pool first, then adds in results from this level. 
        """
        result = {}
        if not pool:
            pool = self.values()
        if recur:
            for bu in pool:
                one_down = bu.components.get_tagged(*tags, recur=recur)
                result.update(one_down)
        this_level = tools.for_tag_operations.get_tagged(pool, *tags)
        result.update(this_level)
        #
        return result
    
    def inheritTags(self, recur = True):
        """


        Components.inheritTags([recur = True]) -> None


        Method provides a Components-specific form of tag inheritance compatible
        with the general inheritance interface.

        Method first runs Tags.inheritTags() on the instance. This step should
        generally should be a no-op because Components objects leave tagSources
        blank by default.

        Method then goes through every component in self.getOrdered() and
        inherits that component's tags.

        If ``recur`` == True, method asks each component to inheritTags() on its
        own before using that component as a source for the instance. 
        """
        self.tags.inheritTags(recur)
        for bu in self.getOrdered():
            if bu:
                if recur:
                    bu.tags.inheritTags()
                self.tags.inheritTagsFrom(bu.tags)

    def _get_pretty_lines(self):
        """


        Components._get_pretty_lines() -> list


        Method returns a list of strings that show each component in rows of
        three.        
        """
        # Get string list for every unit, slap a new-line at the end of every
        # line and return a string with all the lines joined together.
        main_lines = []
        #
        units = self.getOrdered()
        unit_count = len(units)
        #
        group_size = 9
        group_count = unit_count // group_size
        #there are exactly 9 units in each group
        tail_count = unit_count % group_size
        group_header = "\nComponents %s through %s...\n"
        group_footer = "--"
        #
        bunch_footer = ""
        bunch_size = 3
        #
        box_width = None
        unit_spacer = " " * 3
        unit_header = r"#%s"       
        #
        #build out lines one group at a time. go through units in a group
        #in bunches of 3. each bunch of units makes up a row. there are
        #3 bunches in group.
        #
        #get the pretty print lines for each unit a bunch. zip the lines
        #together (line 1a with line 1b, etc.), separated by spacers. that
        #produces the row. then add headers on top of each unit. the row
        #is complete.
        #
        #group print is 3 rows (one for each bunch), plus the group header.
        #
        for i in range(group_count):
            #
            group_lines = []
            #
            group_start = i * group_size
            group_end = (i + 1) * group_size - 1
            #
            filled_group_hdr = group_header % (group_start, group_end)
            group_lines.append(filled_group_hdr)
            #
            #process the bunches; j is the index in the ordered list of units
            #
            j = group_start
            while j < group_end:
                #
                bunch = units[ j : (j + bunch_size) ]
                #
                bunch_lines = []
                #
                boxes = []
                for unit in bunch:
                    unit_box = unit._get_pretty_lines()
                    boxes.append(unit_box)
                if i == 0:
                    box_width = len(boxes[0][0])
                    #set box width once, to the first line of the first unit
                    #
                filled_bunch_hdr = None
                filled_unit_hdrs = []
                for k in range(j, (j + bunch_size)):
                    hdr = unit_header % k
                    hdr = hdr.center(box_width)
                    filled_unit_hdrs.append(hdr)
                #
                filled_bunch_hdr = unit_spacer.join(filled_unit_hdrs)
                filled_bunch_hdr = "\t" + filled_bunch_hdr
                bunch_lines.append(filled_bunch_hdr)                
                #
                #boxes now contains 3 lists of strings. the lists are all the
                #same length because each unit prints in the same format. zip
                #all those lists together into tuples of (line1a, line1b,
                #line1c), (line2a, line2b, line2c), etc.
                #
                zipped_boxes = zip(*boxes)
                #
                for triplet in zipped_boxes:
                    line = unit_spacer.join(triplet)
                    line = "\t" + line
                    bunch_lines.append(line)
                #
                bunch_lines.append(bunch_footer)
                #add a footer string after each bunch; footer can be empty
                #
                group_lines.extend(bunch_lines)
                #row is over, move to the next 3 units. unit index goes up by 3.
                j = j + bunch_size
            #
            #loop is over, add the group lines and a group footer to main lines.
            main_lines.extend(group_lines)
            main_lines.append(group_footer)
        #
        #finished all the groups; now go through the tail
        #HAVE TO MANUALLY ADD A TAIL HEADER
        filled_tail_hdr = group_header % ((unit_count - tail_count),
                                          (unit_count - 1))
        main_lines.append(filled_tail_hdr)
        if tail_count != 0:
            #
            tail_lines = []
            #
            bunch_count = tail_count // bunch_size
            tail_start = unit_count - tail_count
            stub_count = tail_count % bunch_size
            #
            j = tail_start
            for i in range(bunch_count):
                #build each bunch-row, extend tail_lines; then add the final
                #stub row
                bunch = units[j : (j + bunch_size)]
                #
                bunch_lines = []
                #
                boxes = []
                for unit in bunch:
                    unit_box = unit._get_pretty_lines()
                    boxes.append(unit_box)
                if not box_width:
                    box_width = len(boxes[0][0])
                    #set box_width in case tail is the only group
                #
                filled_bunch_hdr = None
                filled_unit_hdrs = []
                for k in range(j, (j + bunch_size)):
                    hdr = unit_header % k
                    hdr = hdr.center(box_width)
                    filled_unit_hdrs.append(hdr)
                filled_bunch_hdr = unit_spacer.join(filled_unit_hdrs)
                filled_bunch_hdr = "\t" + filled_bunch_hdr
                bunch_lines.append(filled_bunch_hdr)                
                #
                #boxes now contains 3 lists of strings. the lists are all the
                #same length because each unit prints in the same format. zip
                #all those lists together into tuples of (line1a, line1b,
                #line1c), (line2a, line2b, line2c), etc.
                #
                zipped_boxes = zip(*boxes)
                #
                for triplet in zipped_boxes:
                    line = unit_spacer.join(triplet)
                    line = "\t" + line
                    bunch_lines.append(line)
                #
                bunch_lines.append(bunch_footer)
                #add a footer string after each bunch; footer can be empty
                #
                main_lines.extend(bunch_lines)
                #row is over, move to the next 3 units. unit index goes up by 3.
                j = j + bunch_size
            #
            #finally, manually append the tail_stub row
            stub_lines = []
            bunch = units[(stub_count * -1):]
            boxes = []
            for unit in bunch:
                unit_box = unit._get_pretty_lines()
                boxes.append(unit_box)
            #
            if not box_width:
                box_width = len(boxes[0][0])
                #set box_width in case the tail stub is the only row
            filled_bunch_hdr = None
            filled_unit_hdrs = []
            for k in range(j, (j + stub_count)):
                hdr = unit_header % k
                hdr = hdr.center(box_width)
                filled_unit_hdrs.append(hdr)
            filled_bunch_hdr = unit_spacer.join(filled_unit_hdrs)
            filled_bunch_hdr = "\t" + filled_bunch_hdr
            stub_lines.append(filled_bunch_hdr)
            #
            zipped_boxes = zip(*boxes)
            #
            for triplet in zipped_boxes:
                line = unit_spacer.join(triplet)
                line = "\t" + line
                stub_lines.append(line)
            #
            stub_lines.append(bunch_footer)
            main_lines.extend(stub_lines)
            #
        main_lines.append(group_footer)
        main_lines.append(group_footer)
        #
        return main_lines            

    def refresh_names(self):
        """


        Components.refresh_names() -> None


        Method clears and rebuilds the instance by_name dictionary for all units
        in instance. 
        """   
        self.by_name.clear()
        for bu in self.values():
            if bu.tags.name:
                self.by_name[bu.tags.name] = bu.id.bbid
            else:
                continue

    def remove_item(self, bbid):
        """


        Components.remove_item(bbid) -> BusinessUnit()


        Method removes an item from the components dictionary given it's bbid.
        Method then updates the by_name dictionary, and setPartOf -> None.
        Method returns the removed item (usually a BU)
        For Drivers, use Dr_Container.remove_driver() instead
        """
        bu = self.pop(bbid)
        bu.setPartOf(None)
        if bu.tags.name:
            self.by_name.pop(bu.tags.name)

        return bu

