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
from data_structures.system.bbid import ID
from data_structures.system.relationships import Relationships
from .parameters import Parameters
from .history import History




# Constants
# n/a

# Globals
logger = logging.getLogger(bb_settings.LOGNAME_MAIN)

# Classes
class TimePeriod(History, TagsMixIn):
    """

    TimePeriod objects represent periods of time and store a snapshot of some
    data during that period in their ``financials`` attribute.

    Class represents an interval that includes its endpoints: [start, end].

    If one thinks of a TimeLine as a clothesrack, TimePeriods are individual
    hangers. This structure enables Blackbird to track the evolution of the data
    over real-world wall/calendar) time.

    TimePeriod.financials is dict keyed by bbid, with values as the Business
    Unit's Financials.

    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    start                 datetime.date; first date in period.
    end                   datetime.date; last date in period
    next_end              datetime.date; end of following period
    past_end              datetime.date; end of preceding period
    financials            dict {bbid: Financials)
    id                    instance of ID class
    length                float; seconds between start and end
    parameters            Parameters object, specifies shared parameters
    relationships         instance of Relationships class
    summary               string, Summary Period = None, 'annual', 'quarterly'

    FUNCTIONS:
    __str__               basic print, shows starts, ends,
    copy()                returns new TimePeriod with a copy of financials
    clear()               clears financials dictionary
    extrapolate_to()      updates inheritance then delegates to Tags
    ex_to_default()       creates result from seed, sets to target start/end
    ====================  ======================================================
    """
    def __init__(self, start_date, end_date, model=None):
        History.__init__(self, recursive_attribute="financials")
        TagsMixIn.__init__(self)

        self.start = start_date
        self.end = end_date

        self.financials = dict()

        self.summary = None
        self.id = ID()
        self.relationships = Relationships(self)

        self.past_end = None
        self.next_end = None

        self.parameters = Parameters()
        self.unit_parameters = Parameters()

        # The current approach to indexing units within a period assumes that
        # Blackbird will rarely remove existing units from a model. both
        # The ``bu`` and ``ty`` directories are static: they do not know if
        # the unit whose bbid they reference is no longer in their domain.

    def __str__(self):
        dots = "*" * bb_settings.SCREEN_WIDTH
        s = "\t starts:  \t%s\n" % self.start.isoformat()
        e = "\t ends:    \t%s\n" % self.end.isoformat()
        c = "\t content: \t%s\n" % self.content
        result = dots + "\n" + s + e + c + dots + "\n"
        return result

    def __iter__(self):
        """

        __iter__() -> iterator of TimePeriod

        Iteration starts with the period following this one and goes forward.
        """
        this = self
        while this.next_end:
            this = this.future
            yield this

    @property
    def past(self):
        """

        ** property **

        TimePeriod.past() -> TimePeriod

        If parent Timeline.add_period() set a _past_day on us, use it
        to locate the predecessor in parent's dictionary.
        """
        past_day = getattr(self, 'past_end', None)
        if past_day:
            return self.relationships.parent[past_day]
        else:
            return None

    @past.setter
    def past(self, value):
        """

        ** property setter **

        TimePeriod.past() -> None

        Noop. TimePeriods look each other up through parent TimeLine.
        """
        pass

    @property
    def future(self):
        """

        ** property **

        TimePeriod.future() -> TimePeriod

        If parent Timeline.add_period() set a _next_day on us, use it
        to locate the successor in parent's dictionary.
        """
        next_day = getattr(self, 'next_end', None)
        if next_day:
            return self.relationships.parent[next_day]
        else:
            return None

    @future.setter
    def future(self, value):
        """

        ** property setter **

        TimePeriod.future() -> None

        Noop. TimePeriods look each other up through parent TimeLine.
        """
        pass

    def clear(self):
        """


        TimePeriod.clear() -> None


        Method erases all Financials data.
        """
        self.financials = dict()

    def copy(self, clean=False):
        """


        TimePeriod.copy() -> TimePeriod


        Method returns a new TimePeriod object whose content is a class-specific
        copy of the caller content.
        """

        result = copy.copy(self)
        result.relationships = self.relationships.copy()
        result.start = copy.copy(self.start)
        result.end = copy.copy(self.end)

        result.tags = self.tags.copy()
        result.parameters = self.parameters.copy()

        result.unit_parameters = Parameters()
        for bbid, unit_dict in self.unit_parameters.items():
            result.unit_parameters[bbid] = unit_dict.copy()

        for bbid, fins in self.financials.items():
            result.financials[bbid] = fins.copy(clean=clean)

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

        model = self.relationships.parent.model
        company = model.get_company()
        if company:
            company.reset_financials(period=result)
            company.fill_out(period=result)
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

        # Step 3: return container
        return result
