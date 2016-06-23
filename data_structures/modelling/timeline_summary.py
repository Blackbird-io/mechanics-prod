# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL
# Blackbird Environment
# Module: data_structures.modelling.timeline_summary
"""

Module defines TimeLine class. TimeLines are dictionaries of time periods with
custom search methods.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
TimelineSummary       collection of PeriodSummary objects indexed by end date
====================  ==========================================================
"""




# imports
from datetime import date, timedelta

from data_structures.system.bbid import ID




# globals
# n/a

# classes
class TimelineSummary(dict):
    """

    A TimeLine is a dictionary of TimePeriod objects keyed by ending date.
    The TimeLine helps manage, configure, and search TimePeriods.

    Unless otherwise specified, class expects all dates as datetime.date objects
    and all periods as datetime.timedelta objects.

    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    id                    instance of BBID class, for interface
    interval              int; interval (in months) of financial summary

    FUNCTIONS:
    add_period()          adds period to TimelineSummary
    find_period()         returns period that contains queried time point
    get_ordered()         returns list of periods ordered by end point
    ====================  ======================================================
    """
    def __init__(self, interval):
        dict.__init__(self)
        self.id = ID()
        self.interval = interval

    def add_period(self, period):
        """


        TimelineSummary.add_period() -> None

        --``period`` is a PeriodSummary object

        Method configures period and records it in the instance under the
        period's end_date.
        """
        period = self._configure_period(period)
        self[period.end] = period

    def find_period(self, query):
        """


        TimelineSummary.find_period() -> TimePeriod


        Method returns a time period that includes query. ``query`` can be a
        POSIX timestamp (int or float), datetime.date object, or string in
        "YYYY-MM-DD" format.
        """
        if isinstance(query, date):
            q_date = query
        else:
            try:
                q_date = date.fromtimestamp(query)
            except TypeError:
                num_query = [int(x) for x in query.split("-")]
                # query is a string, split it
                q_date = date(*num_query)

        result = None
        for p in self.values():
            if p.start <= q_date <= p.end:
                result = p
                break

        return result

    #*************************************************************************#
    #                          NON-PUBLIC METHODS                             #
    #*************************************************************************#

    def _configure_period(self, period):
        """


        TimelineSummary._configure_period() -> period


        Method sets period's namespace id to that of the TimeLine, then returns
        period.
        """
        model_namespace = self.id.namespace
        period.id.set_namespace(model_namespace)
        # Period has only a pointer to the Model.namespace_id; periods don't
        # have their own bbids.
        period.relationships.set_parent(self)

        return period
