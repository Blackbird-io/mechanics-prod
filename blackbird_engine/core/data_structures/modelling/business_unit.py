#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: data_structures.modelling.business_unit
"""

Module defines BusinessUnit class.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:

FUNCTIONS:

CLASSES:
BusinessUnit          structured snapshot of a business at a given point in time
====================  ==========================================================
"""




# Imports
import copy
import datetime
import time

import bb_exceptions
import bb_settings

from data_structures.guidance.guide import Guide
from data_structures.system.bbid import ID
from data_structures.system.tags import Tags
from data_structures.valuation.business_summary import BusinessSummary
from data_structures.valuation.company_value import CompanyValue

from . import common_events

from .components import Components
from .driver import Driver
from .dr_container import DrContainer
from .equalities import Equalities
from .financials import Financials
from .history import History
from .life import Life as LifeCycle
from .parameters import Parameters




# Constants
# n/a

# Globals
# Tags class carries a pointer to the tag manager; access individual tags
# through that pointer
tConsolidated = Tags.tagManager.catalog["consolidated"]
tHardCoded = Tags.tagManager.catalog["hard"]

# Classes   
class BusinessUnit(History, Tags, Equalities):
    """
   
    Object describes a group of business activity. A business unit can be a
    store, a region, a product, a team, a relationship (or many relationships),
    etcetera.
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    components            instance of Components class, stores business units
    drivers               dict; tag/line name : set of driver bbids
    filled                bool; True if fill_out() has run to completion
    financials            instance of Financials object
    guide                 instance of Guide object
    id                    instance of ID object
    life                  instance of Life object
    location              placeholder for location functionality
    parameters            flexible storage for data that shapes unit performance
    size                  int; number of real-life equivalents obj represents
    type                  str or None; unit's in-model type (e.g., "team")
    summary               None or BusinessSummary; investment summary
    valuation             None or CompanyValue; market view on unit
    
    FUNCTIONS:
    add_component()       adds unit to instance components
    add_driver()          registers a driver 
    clear()               restore default attribute values
    fill_out()            integrates consolidate() and derive()
    kill()                make dead, optionally recursive
    recalculate()         reste financials, compute again, repeat for future
    reset_financials()    resets instance and (optionally) component financials
    set_analytics()       attaches an object to instance.analytics 
    set_financials()      attaches a Financials object from the right template
    set_history()         connect instance to older snapshot, optionally recur
    synchronize()         set components to same life, optionally recursive
    ====================  ======================================================
    """

    irrelevantAttributes = ["allTags",
                            "filled",
                            "guide",
                            "id",
                            "parentObject",
                            "partOf"]
    
    tagSources = ["components", "drivers", "financials"]
    
    _UPDATE_BALANCE_SIGNATURE = "Update balance"
        
    def __init__(self, name, fins=None):

        History.__init__(self)
        Tags.__init__(self, name)
        
        self._type = None
        
        self.components = None
        self._set_components()
        
        self.drivers = None
        self._set_drivers()

        self.filled = False
        
        self.set_financials(fins)
        
        self.guide = Guide()
        self.id = ID()
        # Get the id functionality but do NOT assign a bbid yet
        
        self.life = LifeCycle()
        self.location = None
        self.parameters = Parameters()
        self.period = None
        # May want to change period to a property, so that a set to new value
        # will always cause the unit to rerun registration. 

        self.size = 1
        self.summary = BusinessSummary()
        self.valuation = CompanyValue()

    @property
    def type(self):
        """


        **property**


        Getter returns instance._type.

        Setter registers instance bbid under the new value key and removes old
        registration (when instance.period is defined). 

        Deletion prohibited.
        """
        return self._type

    @type.setter
    def type(self, value):
        #
        old_type = self.type
        self._type = value
        #
        if self.period:
            old_entry = self.period.ty_directory.get(old_type)
            old_entry.remove(self.id.bbid)
            new_entry = self.period.ty_directory.setdefault(value, set())
            new_entry.add(self.id.bbid)
            # Entries are sets of bbids for units that belong to that type

    @type.deleter
    def type(self):
        c = "``type`` is a property; delete prohibited. to represent generic "
        c += "unit, set to None instead."
        raise bb_exceptions.ManagedAttributeError(c)
        
    def __hash__(self):
        return self.id.__hash__()

    def __str__(self, lines=None):
        """


        BusinessUnit.__str__() -> str


        Method concatenates each line in ``lines``, adds a new-line character at
        the end, and returns a string ready for printing. If ``lines`` is None,
        method calls _get_pretty_lines() on instance. 
        """
        # Get string list, slap a new-line at the end of every line and return
        # a string with all the lines joined together.
        if not lines:
            lines = self._get_pretty_lines()
            
        # Add empty strings for header and footer padding
        lines.insert(0, "")
        lines.append("")
        
        box = "\n".join(lines)
        return box

    def add_component(self, bu, update_id=True):
        """


        BusinessUnit.add_component() -> None


        Method prepares a bu and adds it to instance components.

        Method always sets bu namespace_id to instance's own namespace_id. If
        ``updateID`` is True, method then assigns a new bbid to the instance.

        Method raises IDNamespaceError if the bu's bbid falls outside the
        instance's namespace id. This is most likely if updateID is False and
        the bu retains an old bbid from a different namespace (e.g., when
        someone inserts a business unit from one model into another without
        updating the business unit's bbid).

        Method raises IDCollisionError if the period's directory already
        contains the new business unit's bbid.

        If all id verification steps go smoothly, method delegates insertion
        down to Components.add_item().       
        """
        bu.summary = None
        bu.valuation = None
        # Step 1: update lifecylce with the right dates for unit and components
        bu._fit_to_period(self.period, recur=True)
        # Step 2: optionally update ids.
        if update_id:
            bu._update_id(namespace=self.id.bbid, recur=True)
        # Step 3: Register the the units. Will raise errors on collisions. 
        bu._register_in_period(recur=True, overwrite=False)
        self.components.add_item(bu)
    
    def addDriver(self, newDriver, *otherKeys):
        """

        **OBSOLETE**

        Legacy interface for add_driver().
        """
        return self.add_driver(newDriver, *otherKeys)
        
    def add_driver(self, newDriver, *otherKeys):
        """


        BusinessUnit.add_driver() -> None


        Method registers a driver to names and tags of lines it supports.
        Method delegates all work to DrContainer.addItem().
        """
        newDriver.validate(parent=self)
        # Validation call will throw DefinitionError if driver does not have
        # sufficient data to run in this instance at the time of insertion.
        
        # Topics may inject drivers into business units at time A with the
        # intent that these drivers work only at some future time B (when their
        # work conditions or other logic has been satisfied). Time B may be
        # arbitrarily far away in the future. This method looks to avoid
        # confusing future errors by making sure that the Topic author is aware
        # of the required formula parameters at the time the Topic runs.

        self.drivers.add_item(newDriver, *otherKeys)
                  
    def clear(self):
        """


        BusinessUnit.clear() -> None


        Method sets attributes in instance.tagSources to their default
        __init__ values.

        **NOTE: clear() will permanently delete data**
        
        """
        blank_bu = BusinessUnit(name=self.name)
        for attr in self.tagSources:
            blank_attr = getattr(blank_bu,attr)
            setattr(self, attr, blank_attr)
    
    def copy(self, enforce_rules=True):
        """


        BU.copy() -> BU


        Method returns a new business unit that is a deep-ish copy of the
        instance.

        The new bu starts out as a shallow Tags.copy() copy of the instance.
        The method then sets the following attributes on the new bu to either
        deep or class-specific copies of the instance values:

        - components
        - drivers
        - financials
        - header.profile
        - id (vanilla shallow copy)
        - life

        The class-specific copy methods for components, drivers, and financials
        all return deep copies of the object and its contents. See their
        respective class documenation for mode detail.
        """
        result = Tags.copy(self, enforce_rules)
        # Start with a basic shallow copy
        #
        r_comps = self.components.copy(enforce_rules)
        result._set_components(r_comps)
        
        r_drivers = self.drivers.copy(enforce_rules)
        result._set_drivers(r_drivers)

        r_fins = self.financials.copy(enforce_rules)
        result.set_financials(r_fins)

        result.guide = copy.deepcopy(self.guide)
        # Have to make a deep copy of guide because it is composed of Counter
        # objects. Guide shouldn't point to a business unit or model
        result.id = copy.copy(self.id)
        result.life = self.life.copy()
        result.summary = BusinessSummary()
        result.valuation = CompanyValue()

        return result
                                
    def recalculate(self, adjust_future=True):
        """


        BusinessUnit.recalculate () -> None


        Recalculate instance finanicals. If ``adjust_future`` is True, will
        repeat for all future snapshots. 
        """
        self.reset_financials()
        self.fill_out()
        if adjust_future and self.future:
            self.future.recalculate(adjust_future=True)
        
    def extrapolate_to(self, target):
        """


        BusinessUnit.extrapolate_to() -> BU


        Returns a new business unit that combines seed and target
        attributes. Method delegates all work to Tags.extrapolate_to() selection
        logic.

        NOTE: BusinessUnit and several objects that form its attributes
        expressly delegate some or all of their extrapolation functionality to
        the Tags module.

        Therefore, these objects will **not** inherit any more
        specialized subclass methods. In the event future versions descend
        BusinessUnit or other objects from specialized subclasses of Tags, can
        fix by removing express delegation and relying on built-in Python MRO. 
        """
        result = Tags.extrapolate_to(self, target)   
        return result

        #have to set history before filling out financials, because they depend
        # on prior balance sheet.

        # now, if i forget about the backwards extrapolation, i can do:
        #   ex_to_default(self):
        #       result = Tags.ex_to(self, target)
        #       result.set_history(self) #can include reset_financials() here
        
        #       if result.parent is None:
        #          result.fill_out()
    
    def ex_to_special(self, target, reverse=False):
        """

       
        BusinessUnit.ex_to_special() -> BU


        Method returns a new business unit that contains a blend of seed
        (caller) and target attributes.

        New unit starts as a copy of caller. Then, for each attribute in
        seed.tagSources, new unit inherits either (i) by default, a new object
        extrapolated from the seed and target attributes of the same name, or
        (ii) an unenforced copy of the target attribute, if that attribute does
        not permit modification. 
        """
        # Step 1: make container
        seed = self
        alt_seed = copy.copy(self)
        alt_seed.clear()
        # Zero out the recursive attributes; a different part of the method works
        # on those
        
        result = alt_seed.copy(enforce_rules=True)
        # Class-specific copy that picks up any class-specific data

        result = Tags.ex_to_special(result, target, mode="at")
        # Updates result with those target tags it doesnt have already. "at" mode
        # picks up all tags from target. other attributes stay identical because
        # Tags uses a shallow copy.
        
        # Step 2: fill container
        
        for attr in self.tagSources:
            o_seed = getattr(self, attr)
            o_targ = getattr(target, attr)
            if self.checkTouch(o_targ):
                o_res = o_seed.extrapolate_to(o_targ)
            else:
                o_res = o_targ.copy(enforce_rules=False)
                #if can't touch an attribute, copy the target wholesale
            setattr(result,attr,o_res)

        # Step 3: return container
        return result

    def fillOut(self, *tagsToOmit):
        """

        **OBSOLETE**

        Legacy interface for fill_out().
        """
        return self.fill_out(*tagsToOmit)
    
    def fill_out(self, *tagsToOmit):
        """


        BusinessUnit.fill_out() -> None


        Will no-op if instance.filled is True. Otherwise, will first sync
        instance balance sheet, then consolidate, and finally derive. At
        conclusion, method sets instance.filled to True to make sure that
        subsequent calls do not increment existing values. 

        NOTE: consolidate() blocks derive() on the same lineitem.
        
        Once a non-None value is written into a Lineitem at one component,
        BusinessUnit.derive() will never run again for that LineItem, either at
        that component or any parent or ancestor of that component.
        """
        if self.filled:
            return
        else:
            self._load_balance()
            self._consolidate(*tagsToOmit)
            self._update_balance(*tagsToOmit)
            # Sets ending balance lines to starting values by default
            self._derive(*tagsToOmit)
            # Derive() will overwrite ending balance sheet where appropriate
            
            self.filled = True
            
    def kill(self, date=None, recur=True):
        """


        BusinessUnit.kill() -> None


        Enters a death event on the specified date. Also enters a ``killed``
        event.

        If ``date`` is None, uses own ref_date. If ``recur`` is True, repeats
        for all components.
        """
        if date is None:
            date = self.life.ref_date
        self.life.events[self.life.KEY_DEATH] = date
        self.life.events[common_events.KEY_KILLED] = date
        if recur:
            for unit in self.components.values():
                unit.kill(date, recur)

    def reset_financials(self, recur=True):
        """


        BusinessUnit.reset_financials() -> None


        Method resets financials for instance and, if ``recur`` is True, for
        each of the components. Method sets instance.filled to False.
        """
        self.filled = False
        print("set ``filled`` to False for bbid\n%s\n" % self.id.bbid)
        self.financials.reset()
        if recur:

            pool = self.components.values()
            
            if bb_settings.DEBUG_MODE:
                pool = self.components.getOrdered()
                # Use stable order to simplify debugging
                
            for bu in pool:
                bu.reset_financials(recur)
                
    def set_analytics(self, atx):
        """


        BusinessUnit.set_analytics() -> None


        Method sets instance.analytics to passed-in argument, sets analytics
        object to point to instance as its parent. 
        """
        atx.setPartOf(self)
        self.valuation = atx

    def set_financials(self, fins=None):
        """


        BusinessUnit.set_financials() -> None


        Method for initializing instance.financials with a properly configured
        Financials object.

        Method will set instance financials to ``fins``, if caller specifies
        ``fins``. Otherwise, method will set financials to a new Financials
        instance. 
        """
        if fins is None:
            fins = Financials()
##        fins.setPartOf(self)
        self.financials = fins

    def set_history(self, history, clear_future=True, recur=True):
        """


        BusinessUnit.set_history() -> None


        Set history for instance; repeat for components (by bbid) if recur is
        True.
        """
        History.set_history(self, history, clear_future=clear_future)

        # Use dedicated logic to handle recursion. 
        if recur:
            for bbid, unit in self.components.items():
                mini_history = history.components[bbid]
                unit.set_history(mini_history)

        self.reset_financials(recur=False)
        # Reset financials here because we just connected a new starting balance
        # sheet.

    def synchronize(self, recur=True):
        """


        BusinessUnit.synchronize() -> None


        Set life on all components to copy of caller. If ``recur`` is True,
        repeat all the way down.
        """
        for unit in self.components.values():
            unit.life = self.life.copy()
            if recur:
                unit.synchronize()

    #*************************************************************************#
    #                          NON-PUBLIC METHODS                             #
    #*************************************************************************#    

    def _consolidate(self, *tagsToOmit, trace=False):
        """


        BusinessUnit.consolidate() -> None


        Method iterates through instance components in order and consolidates
        each living component into instance using BU.consolidate_unit()
        """
        pool = self.components.getOrdered()
        # Need stable order to make sure we pick up peer lines from units in
        # the same order. Otherwise, their order might switch and financials
        # would look different (even though the bottom line would be the same).
            
        for unit in pool:
            
            if unit.life.conceived:
                self._consolidate_unit(unit, *tagsToOmit)
        
    def _consolidate_unit(self, sub, *tagsToOmit):
        """


        BusinessUnit.consolidate_unit() -> None
        

        -- ``sub`` should be a BusinessUnit object
           
        -- ``tagsToOmit`` is a tuple of tags; method will ignore sub lines with
           any of these tags
           
        The Blackbird environment contemplates that BusinessUnits (``parents``)  #<------------------------------------------------update doc string
        may contain multiple component BusinessUnits (``subs``). This method
        consolidates the financials of one sub into the caller instance
        (parent).

        The parent does NOT have to include sub in the parent's components for
        this method to run. 

        Method first fills out the sub, then integrates each line in sub's
        financials into parent financials. 



        The specific sub-to-parent integration algorithm has 5 stages:

        ************************************************************************
        STAGE 1: Check if the sub is alive.
        ************************************************************************

        Method performs no-op if sub is not alive. 

        ************************************************************************
        STAGE 2: Check if the sub LineItem is "informative".
        ************************************************************************
        For a living sub, method steps through each line in sub financials to
        check if the line is ``informative``. 

        ``Informative`` sub LineItems are those that provide insight into the
        meaningful structural or financial profile of the sub. Informative lines
        satisfy at least one of the following conditions:
        
            i)   the LineItem has a non-None name 
            ii)  the LineItem has a non-None value
            iii) the LineItem's allTags list is distinct from the default value
            ([None,None,<spacer>])
            
        Informative LineItems that satisfy condition (i) are ``named``
        LineItems. Informative LineItems that do not satisfy condition (i) but
        do satisfy condition (ii) or (iii) are ``unnamed.``

        NOTE: A lineitem that includes any tags specified in the method's
        ``tagsToOmit`` argument cannot be informative even if it otherwise
        satisifes one of the necessary conditions.

        By default, tagsToOmit include summaryTag and bookMarkTag. That is,
        bookmarks and summaries are per se uninformative and do not increment
        symmetric parent lineitems.         

        This method integrates some of the data from each informative sub line
        into parent's financials. Method skips uninformative sub lines. 

        ************************************************************************
        STAGE 3: Increment named LineItems that have symmetric names.
        ************************************************************************
        If a sub and parent LineItem have the same name, the value of sub
        increments the value of the parent.

        Specifically, for a given named sub lineitem, this method finds the
        **first** line in parent financials with the same name.
        
        Next, method increments the parent line by the sub line value, if the
        sub line has a specified (non-None value). Method skips sub lines with
        None values even if they are named.<-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------absorb tags?

        A signature from this method blocks drivers from modifying a line. 
        
        NOTE1: consolidate() **will** sign a parent line when a sub line
        specifies a value of 0, 0.00, decimal.Decimal(0), etc. 

        That is, setting a lineitem's value to 0 instead of None prevents
        drivers from modifying that lineitem. In the Blackbird environment, 0 is
        affirmative information. Only None signals the absence of information. 

        NOTE2: Only named sub LineItems are eligible for incrementation
        treatment, and only if their names are symmetric to a parent object.
        
        Named LineItems required a non-None value for LineItem.name. Therefore,
        a sub LineItem with .name == None will NOT increment a parent LineItem
        with a .name == None.

        ************************************************************************
        STAGE 4: Create & adjust replicas of name-asymettric sub LineItems.
        ************************************************************************

        For all informative LineItems that do not match the name of a parent
        line, this method copies the line into parent financials.

        Method attempts to insert these ``replica`` lines into parent in the
        same position relative to other lines as the sub line has in sub.

        Prior to insertion, method sets the name for any unnamed informative sub
        lines to a combination of (i) their sub_position and the first 3 tags on
        the sub line. As a result, unnnamed lines from one component should not
        increment the value of parent lines with identical tags.
        
        [UPGRADE-F: TAG-RICH EVO: may require sub lineitems to increment parent
        lineitems with matching or sub.superset tags]

        ************************************************************************
        STAGE 5: Insert replica LineItems into parent.financials.
        ************************************************************************

        Method places replica lines in parent financials to maintain relative
        position of the line against other items in sub financials. 

        Example:

        If lines are ordered [L1,L2,L3,L4] in sub financials, L1 should
        precede L2 in parent.financials. Other lines (LA, LB, LC) can go between
        L1 and L2 in parent because the position of L1 and L2 has no
        relationship to these other lines.

        By contrast, the following order of
        parent lines would violate the relative position of sub L3 and L4:
        
        [L1, ..., L2, ... L4,L3].
        
        Method uses Financials.spotGenerally() to locate the appropriate
        position for a replica. 
        """
        # Step 1: Prep
        tagsToOmit = set(tagsToOmit) #<---------------------------------------------------------------------------------------------------------should be on statement?

        # Step 2: Actual consolidation
        sub.fill_out()

        for attr_name in sub.financials.ORDER:
            child_statement = getattr(sub.financials, attr_name)
            
            if child_statement:
                parent_statement = getattr(self.financials, attr_name)
                parent_statement.increment(child_statement, *tagsToOmit, consolidating=True)

    def _derive(self, *tagsToOmit, spread=False, sheet=None):
        """


        BusinessUnit.derive() -> None


        Method for calculating the value of certain financials lineitems by
        using drivers. Method builds a Queue of applicable drivers for each
        LineItem in BusinessUnit.financials. Method then runs the drivers in the
        queue sequentially. Each LineItem gets a unique queue. Derive() ignores
        drivers that fail Queue.alignItems (misfits)

        In addition to any user-specified tags, method will not derive any lines
        carrying tags for consolidation or hard-coding.

        Method will try to use drivers specifically assigned to the line name in
        instance.drivers. If and only if the drivers dictionary for the line is
        empty, derive() will check if any unassigned (BU.drivers[None]) drivers
        match the line.
        
        NOTE: ALWAYS RUN BusinessUnit.consolidate() BEFORE BusinessUnit.Derive()
        """
        tags_to_omit = set(tagsToOmit) | {tConsolidated, tHardCoded}
        #need to change tagging rules above to make sure BU.consolidate() tags
        #lines appropriately. also need to make sure that inheritTagsFrom() does---------------------------------------------------------------
        #not pick up blockingTags

        # We never derive the starting balance sheet. Accordingly,
        # financials.ordered does not include ``starting``. 
        
        for statement in self.financials.ordered:
            if statement is not None:
                
                for line in statement.get_ordered():    
                    if tags_to_omit & set(line.allTags):
                        continue
                        # _spread_line()
                        # _
                        
                    else:
                        self._derive_line(line, spread=spread, sheet=sheet)
                        # Each line will move the current row to the next
                        # empty cell

    def _spread_or_derive_line():

        for line in statement:

            if tags_to_omit & set(line.allTags):

                self._spread_as_is()
                continue

            else:

                self._derive_line()
                # Derivation works best with spreading because formulas
                # can then look up parameters and other lines

                # If they only look up parameters, you can write the formulas as strings
                # to a list and then put the strings whereever, cause their referents
                # won't change. But some formulas will want to look at other lines and
                # potentially other periods. It's more difficult to do so if you don't know
                # where they are, though we could have some system that sets up pointers
                # to the input lines and then we resolve the pointers when we know where
                # they are. Like literally, the formula would deliver a string template
                # with a bunch of blank fields "{cost}.xl.final + {opex}.xl.final + {sga}.xl.final" and then an array of
                # objects (!): [a, b, c]  (or a dictionary: "cost" : a, "opex" : b, "sga" : c} and we would format the string at the appropriate time (once
                # we have completed those other things). A more explicit format like that
                # could actually prove useful as a comment in excel: we can literally take
                # the entire string and put it on as a comment (or only in the current column)
                #
                # We would still want to piggyback on the recursion cause otherwise difficult
                # to replicate the order of operations.
                #
                # The challenge with drivers is that they work in sequence and build on
                # existing values. And then update the xl.derived.final attribute to wherever
                # they finish. I guess we could make that operation automatic in the _spread()
                # function. 
                #
                # In the separate spread approach, each driver could append row-style entries to
                # a list. The entries should have a formula, a context dictionary, and a label.
                # Basically, up to a 3-column array. If the driver wants to use params, it can
                # specify those as well.
                #
                # The spreader function could then spread all those entries to a list. 
                #
                #   The issue is how to do incremental things. I guess could just point to line.xl.final
                #   and would have to be careful about when I increment them (ie, whatever the value was
                #   at that time). 
                #
                #   The outcome is basically the same cause you still get each one of the steps to
                #   generate a thing. Also, still expect the formula to use parameters, and those are still
                #   on the sheet. The difference is now you can organize the positions separate from
                #   the order of operations. 
                #
                #   Finally, if you point to other periods, ... kind of need to know what column they are in
                #   So the final coordinate has to have a row and a column.
                #
                #   Potentially allows much faster spreading because you make the formula once, its on the
                #   driver, and then you can apply it many times (copy the columns).
                #
                # One other challenge is inserting lines // when the periods differ from each
                # other. Here, you really would want to insert lines in the spreadsheet, because
                # you want to make sure you keep the alignment. 
                #
                # So driver would build up driver cells and put them on .xl.derived.rows
                #
                # and then the spreader would put all the cells in a particular order
                #
                # the spreader could be the one that assembles the details into the whole
                    # walks each line in each statement
                        # for detail in order:
                            # spreads line:
                                # consolidated results
                                # derived results
                                # detailed results
                            # adds summations for each, where appropriate
                        # 
                #
                # then the load_balance function can assign xl coordinates to the right cells
                #
                # in terms of insertion:
                #   you have to move existing cells down if you are putting in a line that wasn't there in
                #   prior period in same position
                # 
                #   and you have to leave cells blank if you are missing a line
                #       otherwise you are going to be putting things in the wrong place
                #       could introduce ranges for this
                #        or line ids
                #        or something else
                #
                #

                        # <----------------------------------------------------this will skip derivation on details?
                        # Can flip this logic into:
                            # for line in statement.get_ordered():
                                # self._derive_line(line)

                        # Then in _derive_line():
                            # if line & bad_tags == set():
                                ## run the drivers
                                # _spread_line():

                            # else:
                                ## _spread_line()

                            # if line._details:
                                ## self._derive_line(details)

                        # Or, can make it derive_and_spread():
                            # 

                        # Also, can add starting balance sheet after CF?
                            # too late? what about change in working capital?
                            
                        # It doesn't get evaluated until we load the sheet anyways, so can just ??
                            # but then don't know where to point formulas

                        # Better approach:
                            # put it at the top, hide it, then can move it again to the bottom
                            # 

                        # Issue is that until we do derive for a statement, we dont know many rows
                        # it's going to take. 

                        # Could simplify this somewhat and just say, ok, each driver gets a row
                        # and all the vars go into the formula directly, and we put a label on the
                        # row.

                        # Really need insert_row() and insert_column() functionality:
                            # Moves everything else down, updates all the formulas that reference the row
                                # for every cell, have a formula attribute
                                # for every formula, have a references attribute
                                    # if the row is referenced, have to adjust
                                    # if the 
                                    
                            # could then rework the derive mechanism, though 

                if spread:
                    sheet.current_row += 1
                    # Add an extra row between statements

    # Each driver's cells should come in a block, so we can put spaces between them, group them, etc.
    # and update the pointer to the line value

    # A rows object should be a list
        # can modify later to support relative positioning

    def _driver_spread(self):
        """
        Add rows for my own production
        """

        # 1 {label: x, formula: y, references: z}
        # 2 {
        # 

    def _formula_spread(self):
        # returns a string
        # with params
        #
        # formula should attach cells to the driver block
        #   or return cells to the driver
        #
        # can finally separate derive and spread (sort of)
        #   if formula looks to past periods, that's ok; formula can conduct
        #   complex search ops and that's ok too: can just add pointers to the
        #   results (hopefully).
        #
        # for the vars it uses:
        #   driver can give it the dictionary of hard-coded addresses?
                # most natural
        #   or it can pass in the sheet

        #   or it can deliver a matrix of rows
        #     issue is that now at derive time, we dont know absolute position
        #     not entirely true: we know absolute position of parameters
        #
        # 
        #
        #   alternatively, driver can deliver a map 
        #
        # can start off by using hard-coded params within the formula
        # (or driver can add rows to a lookup; but dont want a huge thing)
        # 
        # ok come on lets do the skeleton
        # 

    def _derive_line(self, line, spread=False, sheet=None, indent=0):
        """


        BusinessUnit._derive_line() -> None


        Compute the value of a line using drivers stored in the instance.
        """

        if spread:
            # By the time we get here, each line should have it's consolidating
            # links.
            
            # First, add the cells from line consolidation
            line.xl.rows.consolidated.starting = sheet.current_row
            label_column = sheet.time_line.cols.get_position("label")
            
            for link, label in line.xl.rows.consolidated.links_and_labels:

                link_cell = sheet.cell(sheet.current_column, sheet.current_row)
                link_cell.value = link
                # Link should actually be a properly configured formula because
                # it has to point to a different sheet in the book

                label_cell = sheet.cell(label_column, sheet.current_row)
                # Labels should be in the form "from unit 1..."

                line.xl.rows.consolidated.ending = sheet.current_row
                sheet.current_row += 1

                # Can modify this logic to split consolidation into different
                # chunks (ie 5 children per line, 10 children per line, etc.).                

            # Second, add a summation line for the consolidated formulas
            summation_formula = "=sum({column}{starting_row}:{column}{ending_row})"
            local_summation = summation_formula.format(
                "column" : sheet.current_column,
                "starting_row" : line.xl.consolidated.starting,
                "ending_row" : line.xl.consolidated.ending
                )

            summation_cell = sheet.cell(sheet.current_column, sheet.current_row)
            summation_cell.value = summation_formula

            summation_label_cell = sheet.cell(label_column, sheet.current_row)
            if summation_label_cell.value is None:
                summation_label_cell.value = "Consolidated %s" % line.name
                # Conditional to avoid duplicate runs on multi-period

            # Update coordinates
            line.xl.consolidated.ending = sheet.current_row
            line.xl.final = sheet.current_row #<--------------------------------------------------------------------------fixed attr coordinates are absolute; lookup coordinates are relative!!!

            sheet.current_row += 1
            line.xl.rows.derived.starting = sheet.current_row
        
        key = line.name.casefold()
        if key in self.drivers:

##            line.clear()
            matching_drivers = self.drivers.get_drivers(key)

            for driver in matching_drivers:
                driver.workOnThis(line)
                
                if spread:
                    driver.spread(line, sheet)                     # <--------------------------------------------------------------------Each driver should update current row on sheet

        # Repeat for any details            
        if line._details:

            if spread:
                # Prep area:

                line.xl.rows.details.starting = sheet.current_row
                
                f_sum_rows = "+sum("
                f_add_row = "{column}{row},"
                f_add_row.format(
                    "column" : sheet.current_column
                    )
                detail_summation = blah
            
            for detail in line.get_ordered():

                if indent is not None:
                    indent += 2

                self._derive_line(detail, spread=spread, sheet=sheet, indent=indent)
                # <-------------------------------------------------------------------------------------- Sheet should track the current row
                
                if spread:
                     detail_summation += (f_add_row % detail.xl.rows.final)
                     
            else:

                detail_summation += ")"
                # Add a closing parenthesis to the summation formula

            if details and spread:

                # Add a summation line
                summation_cell = sheet.cell(sheet.current_column, sheet.current_row)
                summation_cell.value = detail_summation
                line.xl.rows.details.ending = sheet.current_row

                label_cell = sheet.cell(label_column, sheet.current_row)
                if label_cell.value is None:
                    label = indent * " "
                    label += ("%s: total details" % line.name)
                    label_cell.value = label
                    
                sheet.current_row +=1
            
        if spread:

            # Now, pull it all together: final line value is sum of consolidated, derived, and detailed
            
            # Make the total row
            f_total_summation = f_summation

            if line.xl.rows.consolidated.ending:
                f_total_summation += (f_add_row % line.xl.rows.consolidated.final)

            if line.xl.rows.derived.ending:
                f_total_summation += (f_add_row % line.xl.rows.derived.final)

            if line.xl.rows.detailed.ending is not None:
                f_total_summation += (f_add_row % line.xl.rows.detailed.ending)

            f_total_summation += ")"

            total_cell = sheet.cell(sheet.current_column, sheet.current_row)             # May be safer to keep column index in letters
            total_cell.value = f_total_summation

            label_cell = sheet.cell(label_column, sheet.current_row)
            label_cel.value = "Total %s" % line.name

            sheet.current_row +=1 
            
                    
        # May be I should indicate the current row on the sheet? Would simplify
        # matters a fair amount

        # HAVEN'T WRITTEN THE LINE NAME ANYWHERE YET <-------------------------------------------ISSUE !!!
            # in the consolidation block, should be writing unit names
            # in the derivation block, should be writing driver names?
            # all of the labelling is a waste if we do more than one column
            
        # Generally speaking, "current row" should always be empty. Each routine
        # should move the index to the right place when its done.

        # Right now, all the logic takes place in _derive_line. As a result, the spreading
        # logic won't run on lines that we've consolidated (or any of their details).
        # 
        # We should remove this dependency. First pass does not have to be efficient. Can
        # duplicate the routines. if not bad_tags: derive, else: derive, spread? Alternatively
        # can make the cells and then put them on the list. Probably best to do that.

        # Then final _spread is like fill_out() or something. Can add this later, let's finish
        # this first bit of logic first.
                
    def _fit_to_period(self, time_period, recur=True):
        """


        BusinessUnit._fit_to_period() -> None

        
        Set pointer to timeperiod and synchronize ref date to period end date.
        If ``recur`` == True, repeat for all components.
        """
        self.period = time_period
        self.life.set_ref_date(time_period.end)
        if recur:
            for unit in self.components.values():
                unit._fit_to_period(time_period, recur)

    def _get_pretty_lines(self,
                          top_element="=",
                          side_element="|",
                          box_width=23,
                          field_width=5):
        """


        BusinessUnit._get_pretty_lines() -> list


        Method returns a list of strings that displays a box if printed in
        order. Line ends are naked (i.e, lines do **not** terminate in a
        new-line character).

        Box format (live units):
      
        +=====================+
        | NAME  : Baltimore-4 |
        | ID    : ...x65-0b78 |
        | DOB   :  2015-04-01 |
        | LIFE  :         43% |
        | STAGE :      MATURE |   
        | TYPE  :         OPS |
        | FILL  :        True |
        | COMPS :          45 |
        +=====================+

        Box format (dead units):

        +=====\========/======+
        | name \: Balt/more-4 |
        | id    \ .../65-0b78 |
        | dob   :\ 2/15-04-01 |
        | life  : \/      43% |
        | stage : /\   MATURE |   
        | type  :/  \     OPS |
        | fill  /    \   True |
        | comps/:     \    45 |
        +=====/========\======+

        Box format (unborn units):
      
        ?  = = = = = = = = =  ?
        | NAME  : Baltimore-4 |
          ID    : ...x65-0b78  
        | DOB   :  2015-04-01 |
          LIFE  :         43%  
        | STAGE :      MATURE |   
          TYPE  :         OPS  
        | FILL  :        True |
          COMPS :          45 
        ?  = = = = = = = = =  ?
        
        """
        reg_corner = "+"
        alt_corner = "?"
        alt_element = " "
        #
        ##formatting rules
        template = "%s %s : %s %s"
        empty_line = template % (side_element,
                                     ("x" * field_width),
                                     "",
                                     side_element)
        #empty_line should equal " | xxxxxxxx :  |"
        data_width = box_width - len(empty_line)
        #
        ##fields:
        fields = ["NAME",
                  "ID",
                  "DOB",
                  "LIFE",
                  "EVENT",
                  "TYPE",
                  "FILL",
                  "SIZE",
                  "COMPS"]
        ##data
        data = {}
        unit_name = str(self.name)
        if len(unit_name) > data_width:
            #abbreviate unit name if its too long
            unit_name_parts = unit_name.split()
            if len(unit_name_parts) > 1:
                last_part = unit_name_parts[-1]
                initials = ""
                for part in unit_name_parts[:-1]:
                    initial = part[:1] + "."
                    initials = initials + initial
                unit_name = initials + last_part
        data["NAME"] = unit_name[:data_width]

        id_dots = "..."
        tail_width = data_width - len(id_dots)
        id_tail  = str(self.id.bbid)[(tail_width * -1):]
        data["ID"] = id_dots + id_tail

        date_of_birth = self.life.events.get(self.life.KEY_BIRTH)
        if date_of_birth:
            dob = date_of_birth.isoformat()
        else:
            dob = "n/a"
        data["DOB"] = dob
        
        if self.life.percent is not None:
            life = int(self.life.percent)
            life = str(life) + r"%"
        else:
            life = "n/a"
        data["LIFE"] = life
        
        data["EVENT"] = self.life.get_latest()[0][:data_width]
        # Pick out the event name, trim to data width. 
        
        unit_type = str(self.type)[:data_width]
        data["TYPE"] = unit_type.upper()
        
        data["FILL"] = str(self.filled)
        
        data["COMPS"] = str(len(self.components.get_living()))
        
        data["SIZE"] = str(self.size)[:data_width]
        #
        ##assemble the real thing
        ##DONT FORGET TO rjust(data_width)
        #
        lines = []
        top_border = reg_corner + top_element * (box_width - 2) + reg_corner
        lines.append(top_border)
        #
        for field in fields:
            new_line = template % (side_element,
                                   field.ljust(field_width),
                                   data[field].rjust(data_width),
                                   side_element)
            lines.append(new_line)
        #
        #add a bottom border symmetrical to the top
        lines.append(top_border)
        #
        #post-processing (dashed lines for units scheduled to open in the
        #future, x's for units that have already closed)
        
        if self.life.ref_date < date_of_birth:
            #
            alt_width = int(box_width / 2) + 1
            alt_border = (top_element + alt_element) * alt_width
            alt_border = alt_border[:(box_width - 2)]
            alt_border = alt_corner + alt_border + alt_corner
            #
            core_lines = lines[1:-1]
            for i in range(0, len(core_lines), 2):
                line = core_lines[i]
                core_symbols = line[1:-1]
                line = alt_element + core_symbols + alt_element
                core_lines[i] = line
            #
            lines = [alt_border] + core_lines + [alt_border]
        #
        date_of_death = self.life.events.get(self.life.KEY_DEATH)
        if self.life.ref_date > date_of_death:
            #
            alt_lines = []
            line_count = len(lines)
            down_start = int((box_width - line_count)/2)
            #X is line_count lines wide
            up_start = down_start + line_count
            #
            for i in range(line_count):
                #
                #replace the character at (down_start + i) with "\"
                #replace the character at (up_start - i) with "/"
                #
                line = lines[i]
                #
                down_pos = (down_start + i)
                seg_a = line[: (down_pos)]
                seg_b = line[(down_pos + 1):]
                line = seg_a + "\\" + seg_b
                #
                up_pos = (up_start - i)
                seg_a = line[:(up_pos)]
                seg_b = line[(up_pos + 1):]
                line = seg_a + "/" + seg_b
                line = line.casefold()
                #
                alt_lines.append(line)
            lines = alt_lines
        #
        return lines    

    def _load_balance(self):
        """


        BusinessUnit._load_balance() -> None


        Connect starting balance sheet to past if available, copy shape to
        ending balance sheet.
        """
        if self.past:
            self.financials.starting = self.past.financials.ending
            # Connect to the past

        ending_name = self.financials.ending.name
        self.financials.ending = self.financials.starting.copy(enforce_rules=False) 
        # Copy all lines from starting; we are assuming no changes here.
        self.financials.ending.setName(ending_name)
        
        self.financials.ending.reset()
        # By default, the ending balance sheet should look the same as the
        # starting one. Here, we copy the starting structure and zero out
        # the values. We will fill in the values later through
        # consolidate(), update_balance(), and derive().
        
    def _register_in_period(self, recur=True, overwrite=True):
        """


        BusinessUnit._register_in_period() -> None


        Method updates the bu_directory on the instance period with the contents
        of instance.components (bbid:bu). If ``recur`` == True, repeats for
        every component in instance.

        If ``overwrite`` == False, method will raise an error if any of its
        component bbids is already in the period's bu_directory at the time of
        call.

        NOTE: Method will raise an error only if the calling instance's own
        components have ids that overlap with the bu_directory. To the extent
        any of the caller's children have an overlap, the error will appear only
        when the recursion gets to them. As a result, by the time the error
        occurs, some higher-level or sibling components may have already updated
        the period's directory.        
        """
        # UPGRADE-S: Can fix the partial-overwrite problem by refactoring this
        # routine into 2 pieces. build_dir(recur=True) would walk the tree and
        # return a clean dict. update_dir(overwrite=bool) would compare that
        # dict with the existing directory and raise an error if there is
        # an overlap. Also carries a speed benefit, cause only compare once.
        
        if not overwrite:
            if self.id.bbid in self.period.bu_directory:
                c1 = "TimePeriod.bu_directory already contains an object with "
                c2 = "the same bbid as this unit. \n"
                c3 = "unit id:         %s\n" % self.id.bbid
                c4 = "known unit name: %s\n"
                c4 = c4 % self.period.bu_directory[self.id.bbid].name
                c5 = "new unit name:   %s\n\n" % self.name
                print(self.period.bu_directory)
                c = c1+c2+c3+c4+c5
                raise bb_exceptions.IDCollisionError(c)
            
        # Check for collisions first, then register if none arise.
        self.period.bu_directory[self.id.bbid] = self
        brethren = self.period.ty_directory.setdefault(self.type, set())
        brethren.add(self.id.bbid)

        if recur:
            for unit in self.components.values():
                unit._register_in_period(recur, overwrite)

    def _build_directory(self, recur=True, overwrite=True):
        """


        BusinessUnit._build_directory() -> (id_directory, ty_directory)
        

        Register instanceyourself and optionally your components, by type and by id
        return id_directory, ty_directory
        """
        #return a dict of bbid:unit
        id_directory = dict()
        ty_directory = dict()
        if recur:
            for unit in self.components.values():
                lower_level = unit._build_directory(recur=True, overwrite=overwrite)
                lower_ids = lower_level[0]
                lower_ty = lower_level[1]
                id_directory.update(lower_ids)
                ty_directory.update(lower_ty)
                
            #update the directory for each unit in self
            pass
        if self.id.bbid in directory:
            if not overwrite:
                raise Error
            
        id_directory[self.id.bbid] = self
        this_type = ty_directory.setdefault(self.type, set())
        this_type.add(self.id.bbid)
      
        return id_directory, ty_directory
        # unfinished <--------------------------------------------------------------------------------------------

    def _set_components(self, comps=None):
        """


        BusinessUnit._set_components() -> None


        Method sets instance.components to the specified object, sets object to
        point to instance as its parent. If ``comps`` is None, method generates
        a clean instance of Components().
        """
        if not comps:
            comps = Components()
        comps.setPartOf(self)
        self.components = comps
        
    def _set_drivers(self, dr_c=None):
        """


        BusinessUnit._set_drivers() -> None


        Method for initializing instance.drivers with a properly configured
        DrContainer object. Method sets instance as the parentObject for
        DrContainer and any drivers in DrContainer.
        """
        if not dr_c:
            dr_c = DrContainer()
        dr_c.setPartOf(self, recur = True)
        self.drivers = dr_c

    def _update_balance(self, *tagsToOmit):
        """


        BusinessUnit._update_balance() -> None

        
        Populate blank lines in the ending balance sheet with starting values.
        Ignore lines that we have already consolidated. Derive() can later
        overwrite these values. 
        """
        tags_to_omit = set(tagsToOmit)
        tags_to_omit.add(tConsolidated)
        
        starting_balance = self.financials.starting
        ending_balance = self.financials.ending

        # Method expects balance sheet to come with accurate tables. We first
        # build the table in load_balance(). We then run consolidate(), which
        # will automatically update the tables if it changes the statement. 
        
        if starting_balance and ending_balance:
            
            for name, starting_line in ending_balance._details.items():

                if tags_to_omit & set(starting_line.allTags):
                    continue

                else:
                    ending_line = ending_balance.find_first(starting_line.name)
                    if starting_line.value is not None:
                        ending_line.set_value(source.value, self._UPDATE_BALANCE_SIGNATURE)

                # Theoretically find_first() could create problems if multiple lines in a
                # balance sheet have the same details (ie short-term and long-term bonds).
                # In practice, we are going through only the top-level items in the ending
                # balance sheet, so the only conflict could arise if starting balance sheet
                # somehow has only a detail like ending but not the top-level item to block
                # it. That's basically impossible.
    
    def _update_id(self, namespace, recur=True):
        """


        BusinessUnit._update_id() -> None


        Assigns instance a new id in the namespace, based on the instance name.
        If ``recur`` == True, updates ids for all components in the parent
        instance bbid namespace.
        """
        self.id.set_namespace(namespace)
        self.id.assign(self.name)
        # This unit now has an id in the namespace. Now pass our bbid down as
        # the namespace for all downstream components. 
        if recur:
            for unit in self.components.values():
                    unit._update_id(namespace=self.id.bbid, recur=True)


        
        

        
                    

    
        
        

    
