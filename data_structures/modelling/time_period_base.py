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
from tools.parsing import date_from_iso

from .history import History
from .financials import Financials




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
    start                 datetime.date; first date in period.
    end                   datetime.date; last date in period
    id                    instance of ID class
    next_end              datetime.date; end of following period
    past_end              datetime.date; end of preceding period
    relationships         instance of Relationships class

    FUNCTIONS:
    copy()                return a copy of the caller instance
    ====================  ======================================================
    """

    def __init__(self, start_date, end_date, model=None):
        History.__init__(self, recursive_attribute="content")

        self.start = start_date
        self.end = end_date

        self.financials = dict()

        self.summary = None
        self.id = ID()
        self.relationships = Relationships(self, model=model)

        self.past_end = None
        self.next_end = None

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

    @classmethod
    def from_portal(cls, model, portal_data):
        """


        TimePeriodBase.to_portal(portal_model) -> TimePeriodBase

        **CLASS METHOD**

        Method deserializes a TimePeriodBase from portal representation.
        """
        period = cls(
            date_from_iso(portal_data['period_start']),
            date_from_iso(portal_data['period_end']),
            model=model,
        )
        period.summary = portal_data['summary']

        financials_set = Financials.from_portal(
            period, portal_data.get('financials_set', [])
        )
        for buid, fins in financials_set.items():
            period.financials[buid] = fins

        return period

    def to_portal(self):
        """


        TimePeriodBase.to_portal(portal_model) -> dict

        Method serializes a TimePeriodBase to portal representation.
        """
        financials_set = []
        for buid, fins in self.financials.items():
            if not isinstance(buid, str):
                buid = buid.hex
            financials_set.extend(fins.to_portal(self, buid))
        result = {
            'period_end': format(self.end),
            'period_start': format(self.start),
            'summary': self.summary,
            'financials_set': financials_set,
        }
        return result

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

        return result

