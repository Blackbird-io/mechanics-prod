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
import logging

import bb_settings
import bb_exceptions

from data_structures.system.tags_mixin import TagsMixIn

from .parameters import Parameters
from .time_period_base import TimePeriodBase




# Constants
# n/a

# Globals
logger = logging.getLogger(bb_settings.LOGNAME_MAIN)

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
    parameters            Parameters object, specifies shared parameters
    unit_parameters       Parameters object, unit-specific parameters

    FUNCTIONS:
    __str__               basic print, shows starts, ends, and content
    copy()                returns new TimePeriod with a copy of content
    combine_parameters()  propagate past parameters to current period
    extrapolate_to()      updates inheritance then delegates to Tags
    ex_to_default()       creates result from seed, sets to target start/end
    get_units()           return list of units from bbid pool
    get_lowest_units()    return list of units w/o components from bbid pool
    ====================  ======================================================
    """
    def __init__(self, start_date, end_date, model=None):
        # content is handled differently, is not passed on to base init
        TimePeriodBase.__init__(self, start_date, end_date, model=model)
        TagsMixIn.__init__(self)

        self.parameters = Parameters()
        self.unit_parameters = Parameters()

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

    def combine_parameters(self):
        """


        TimePeriod.copy() -> None

        Propagate preceeding period's parameters to self.
        Our parameters override.
        """

        if self.past:
            # augment our parameters with past parameters
            comb = self.past.parameters.copy()
            # ours dominate
            comb.update(self.parameters)
            self.parameters.update(comb)

            # update period-specific unit parameters with past parameters
            this_dict = self.unit_parameters
            past_dict = self.past.unit_parameters
            # all bbid's in past and present unit_parameters
            pair_keys = this_dict.keys() | past_dict.keys()
            for bbid in pair_keys:
                # create our unit_parameters for this bbid if missing
                this_parm = this_dict.setdefault(bbid, {})
                past_parm = past_dict.get(bbid, {})
                # update our unit_parameters with past parameters
                comb = past_parm.copy()
                # ours dominate
                comb.update(this_parm)
                this_parm.update(comb)

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
