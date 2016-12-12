# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL
# Blackbird Environment
# Module: data_structures.modelling.time_period_base
"""

Module defines TimePeriodBase class.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
TimePeriodBase        a snapshot of data over a period of time.
====================  ==========================================================
"""




# Imports
import copy

import bb_exceptions
import bb_settings

from data_structures.system.bbid import ID
from data_structures.system.relationships import Relationships

from .history import History




# Constants
# n/a

# Classes
class TimePeriodBase(History):
    """

    PeriodSummary objects represent periods of time and store a snapshot of some
    data during that period in their ``content`` attribute.

    Class represents an interval that includes its endpoints: [start, end].

    If one thinks of a TimeLine as a clothesrack, TimePeriods are individual
    hangers. This structure enables Blackbird to track the evolution of the data
    over real-world wall/calendar) time.

    The data in ``content`` is usually a top-level business unit. TimePeriod
    provides a reference table ``bu_directory`` for objects that the data
    contains. The bu_directory tracks objects by their bbid. Only one object
    with a given bbid should exist within a PeriodSummary. bbid collisions within
    a time period represent the time-traveller's paradox.

    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    bu_directory          dict; all business units in this period, keyed by bbid
    content               pointer to content, usually a business unit
    end                   datetime.date; last date in period
    id                    instance of ID class
    next_end              datetime.date; end of following period
    past_end              datetime.date; end of preceding period
    relationships         instance of Relationships class
    start                 datetime.date; first date in period.

    FUNCTIONS:
    copy()                return a copy of the caller instance
    get_units()           return list of units from bbid pool
    ====================  ======================================================
    """

    def __init__(self, start_date, end_date, content=None, model=None):
        History.__init__(self, recursive_attribute="content")

        self.start = start_date
        self.end = end_date

        self.bu_directory = model.bu_directory
        self.financials = dict()

        self.summary = None
        self.content = content
        self.id = ID()
        self.relationships = Relationships(self)

        self.past_end = None
        self.next_end = None

        # The current approach to indexing units within a period assumes that
        # Blackbird will rarely remove existing units from a model.
        # The ``bu`` directory is static: it does not know if
        # the unit whose bbid it references is no longer in its domain.

    def __str__(self):
        dots = "*" * bb_settings.SCREEN_WIDTH
        s = "\t starts:  \t%s\n" % self.start.isoformat()
        e = "\t ends:    \t%s\n" % self.end.isoformat()
        c = "\t content: \t%s\n" % self.content
        result = dots + "\n" + s + e + c + dots + "\n"
        return result

    def __iter__(self):
        """

        __iter__() -> iterator of TimePeriodBase

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

        TimePeriodBase.past() -> TimePeriodBase

        If parent TimelineBase.add_period() set a _past_day on us, use it
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

        TimePeriodBase.past() -> None

        Noop. TimePeriods look each other up through parent TimeLine.
        """
        pass

    @property
    def future(self):
        """

        ** property **

        TimePeriodBase.future() -> TimePeriodBase

        If parent TimelineBase.add_period() set a _next_day on us, use it
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

        TimePeriodBase.future() -> None

        Noop. TimePeriods look each other up through parent TimeLine.
        """
        pass

    def copy(self):
        """


        TimePeriodBase.copy() -> TimePeriodBase


        Method returns a new TimePeriod object whose content is a class-specific
        copy of the caller content.
        """
        result = copy.copy(self)
        result.relationships = self.relationships.copy()
        result.start = copy.copy(self.start)
        result.end = copy.copy(self.end)
        #same id namespace (old model)

        return result

    def get_units(self, pool):
        """


        TimePeriodBase.get_units() -> list


        Method returns a list of objects from instance.bu_directory that
        correspond to each bbid in ``pool``. Method sorts pool prior to
        processing.

        Method expects ``pool`` to be an iterable of bbids.
        """
        pool = sorted(pool)
        # make sure to sort pool for stable output order
        units = []
        for bbid in pool:
            u = self.bu_directory[bbid]
            units.append(u)
        return units

    # *************************************************************************#
    #                          NON-PUBLIC METHODS                             #
    # *************************************************************************#

    def _reset_directories(self):
        """


        TimePeriodBase.reset_directories() -> None


        Method sets instance.bu_directory to blank dictionary.
        """
        self.bu_directory = dict()
