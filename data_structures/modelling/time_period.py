# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL
# Blackbird Environment
# Module: data_structures.modelling.time_period
"""

Module defines TimePeriod class.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
TimePeriod            a snapshot of data over a period of time. 
====================  ==========================================================
"""





# Imports
import copy

import bb_exceptions

from data_structures.system.tags_mixin import TagsMixIn

from .parameters import Parameters
from .time_period_base import TimePeriodBase




# Constants
# n/a

# Classes
class TimePeriod(TimePeriodBase, TagsMixIn):
    """

    TimePeriod objects represent periods of time and store a snapshot of some
    data during that period in their ``content`` attribute.

    Class represents an interval that includes its endpoints: [start, end].
    
    If one thinks of a TimeLine as a clothesrack, TimePeriods are individual
    hangers. This structure enables Blackbird to track the evolution of the data
    over real-world wall/calendar) time. 

    The data in ``content`` is usually a top-level business unit. TimePeriod
    provides a reference table ``bu_directory`` for objects that the data
    contains. The bu_directory tracks objects by their bbid. Only one object
    with a given bbid should exist within a TimePeriod. bbid collisions within
    a time period represent the time-traveller's paradox. 
    
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    bu_directory          dict; all business units in this period, keyed by bbid
    content               pointer to content, usually a business unit
    end                   datetime.date; last date in period 
    id                    instance of ID class
    length                float; seconds between start and end
    parameters            Parameters object, specifies shared parameters
    relationships         instance of Relationships class
    start                 datetime.date; first date in period.
    ty_directory          dict; keys are strings, values are sets of bbids
    
    FUNCTIONS:
    __str__               basic print, shows starts, ends, and content
    clear()               clears content, resets bu_directory
    copy()                returns new TimePeriod with a copy of content
    extrapolate_to()      updates inheritance then delegates to Tags
    ex_to_default()       creates result from seed, sets to target start/end
    get_units()           return list of units from bbid pool
    get_lowest_units()    return list of units w/o components from bbid pool
    register()            conform and register unit
    set_content()         attach company to period
    ====================  ======================================================
    """
    def __init__(self, start_date, end_date, content=None):
        TimePeriodBase.__init__(self, start_date, end_date)
        TagsMixIn.__init__(self)

        self.parameters = Parameters()
        self.unit_parameters = Parameters()
        self.ty_directory = dict()

        if content:
            self.set_content(content)

        # The current approach to indexing units within a period assumes that
        # Blackbird will rarely remove existing units from a model. both
        # The ``bu`` and ``ty`` directories are static: they do not know if
        # the unit whose bbid they reference is no longer in their domain.

    def clear(self):
        """


        TimePeriod.clear() -> None


        Method sets content to None and resets instance directories.
        """
        self.content = None
        self._reset_directories()
        
    def copy(self):
        """


        TimePeriod.copy() -> TimePeriod


        Method returns a new TimePeriod object whose content is a class-specific
        copy of the caller content. 
        """

        # result = TimePeriodBase.copy(self)
        result = copy.copy(self)
        result.relationships = self.relationships.copy()
        result.start = copy.copy(self.start)
        result.end = copy.copy(self.end)

        if self.content:
            new_content = self.content.copy()

            result.set_content(new_content, updateID=False)

        result.tags = self.tags.copy()
        result.ty_directory = copy.copy(self.ty_directory)
        result.parameters = self.parameters.copy()

        result.unit_parameters = Parameters()
        for bbid, unit_dict in self.unit_parameters.items():
            result.unit_parameters[bbid] = unit_dict.copy()

        return result
        
    def extrapolate_to(self, target):
        """


        TimePeriod.extrapolate_to() -> TimePeriod


        Method returns a new time period with a mix of seed and target data.

        Method updates tags on seed and target and then passes them to standard
        Tags.extrapolate_to() selection logic. 
        """

        result = self.ex_to_default(target)

        if result.end > self.end:
            result.set_history(self, clear_future=True, recur=True)
        else:
            self.set_history(result, clear_future=False, recur=True)
            # For backwards extrapolation; keep future as-is.

        if result.content:
            result.content.reset_financials()
            result.content.fill_out()
            # This logic should really run on the business unit
        
        return result
    
    def ex_to_default(self, target):
        """


        TimePeriod.ex_to_default() -> TimePeriod


        Method used for extrapolation when existing target content can be
        discarded. Method returns a new TimePeriod object that represents a
        projection of seed (caller) content into the point in time specified by
        target.

        NOTE: Method assumes that both seed and target have up-to-date inherited
        tags. It is up to user to deliver accordingly. 

        Method first creates a vanilla shallow copy of the caller, then runs
        a class-specific .copy on the vanilla alt_seed to create the result
        shell. Method sets the time endpoints on the result to those specified
        by target and creates a copy of seed content. Method concludes by
        running setContent(new_content) on the result. The last step spread the
        period and date information down the content structure and updates the
        result's bu_directory with the bbid's of all BusinessUnits it contains.
        
        NOTE2: For best results, may want to clear and re-inherit tags on result
        after method returns it. 
        """
        # Step 1: make container
        seed = self

        alt_seed = copy.copy(seed)
        # Keep all attributes identical, but now can zero out the complicated
        # stuff.
        alt_seed.clear()
        
        result = alt_seed.copy()
        # Use class-specific copy to create independent objects for any important
        # container-level data structures; Tags.copy() only creates new tag lists
        
        result.tags = result.tags.extrapolate_to(target.tags)
        # Updates result with target tags. We use "at" mode to pick up all tags.
        
        # Step 2: configure and fill container
        result.start = copy.copy(target.start)
        result.end = copy.copy(target.end)

        result.parameters = target.parameters.copy()

        # update period-specific unit parameters to reflect target period vals
        for bbid, unit_parms in target.unit_parameters.items():
            try:
                temp_parms = result.unit_parameters[bbid]
            except KeyError:
                temp_parms = Parameters()

            temp_parms.update(unit_parms)

            result.unit_parameters.add({bbid: temp_parms}, overwrite=True)

        if seed.content:
            new_content = seed.content.copy()
            result.set_content(new_content, updateID=False)
    
        # Step 3: return container
        return result        

    def get_lowest_units(self, pool=None, run_on_empty=False):
        """


        TimePeriod.get_lowest_units() -> list


        Method returns a list of units in pool that have no components.
        
        Method expects ``pool`` to be an iterable of bbids. 

        If ``pool`` is None, method will build its own pool from all keys in
        the instance's bu_directory. Method will raise error if asked to run
        on an empty pool unless ``run_on_empty`` == True.
        
        NOTE: method performs identity check (``is``) for building own pool;
        accordingly, running a.select_bottom_units(pool = set()) will raise
        an exception.         
        """
        if pool is None:
            pool = sorted(self.bu_directory.keys())
        else:
            pool = sorted(pool)
        #make sure to sort pool for stable output order
        #
        if any([pool, run_on_empty]):
            foundation = []
            for bbid in pool:
                bu = self.bu_directory[bbid]
                if bu.components:
                    continue
                else:
                    foundation.append(bu)
            #
            return foundation
            #
        else:
            c = "``pool`` is empty, method requires explicit permission to run."
            raise bb_exceptions.ProcessError(c) 
                
    def register(self, bu, updateID=True, reset_directories=False):
        """


        TimePeriod.register() -> None


        Manually add unit to period. Unit will conform to period and appear
        in directories. Use sparingly: designed for master (taxonomy) period.

        NOTE: Period content should generally have a tree structure, with a
        single bu node on top. That node will manage all child relationships.
        Accordingly, the best way to add units to a period is to run
        bu.add_component(new_unit).

        If ``updateID`` is True, method will assign unit a new id in the
        period's namespace. Parameter should be False when moving units
        between scenarios.
        
        If ``reset_directories`` is True, method will clear existing type
        and id directories. Parameter should be True when registering the
        top (company) node of a structure. 
        """
        
        bu._fit_to_period(self, recur=True)
        # Update unit life.

        if updateID:
            bu._update_id(self.id.namespace, recur=True)
        if not bu.id.bbid:
            c = "Cannot add content without a valid bbid."
            raise bb_exceptions.IDError(c)
        # Make sure unit has an id in the right namespace. 
        
        if reset_directories:
            self._reset_directories()

        bu._register_in_period(recur=True, overwrite=False)
        # Register the unit.

    def set_content(self, bu, updateID=True):
        """


        TimePeriod.set_content() -> None


        Register bu and set instance.content to point to it. 

        NOTE: ``updateID`` should only be True when adding external content to
        a model for the first time (as opposed to moving content from period to
        period or level to level within a model).

        TimePeriods in a Model all share the model's namespace_id. Accordingly,
        a BusinessUnit will have the same bbid in all time periods. The
        BusinessUnit can elect to get a different bbid if it's name changes, but
        in such an event, the Model will treat it as a new unit altogether.
        """
        self.register(bu, updateID=updateID, reset_directories=True)
        # Reset directories when setting the top node in the period.
        self.content = bu
        
    #*************************************************************************#
    #                          NON-PUBLIC METHODS                             #
    #*************************************************************************#
              
    def _reset_directories(self):
        """


        TimePeriod.reset_directories() -> None


        Method sets instance.bu_directory and instance.ty_directory to blank
        dictionaries. 
        """
        self.bu_directory = {}
        self.ty_directory = {}
