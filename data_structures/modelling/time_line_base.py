# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL
# Blackbird Environment
# Module: data_structures.modelling.time_line_base
"""

Module defines TimelineBase class. TimelineBase objects  are dictionaries of
time periods with custom search methods.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
TimelineBase       collection of PeriodSummary objects indexed by end date
====================  ==========================================================
"""




# imports
import copy

from datetime import date

from data_structures.system.bbid import ID




# globals
# n/a

# classes
class TimelineBase(dict):
    """

    A TimelineBase is a dictionary of TimePeriod objects keyed by ending date.
    The TimelineBase helps manage, configure, and search TimePeriods.

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
    def __init__(self, interval, model):
        dict.__init__(self)
        self.id = ID()
        # TimelineBase objects support the id interface and pass the model's id
        # down to time periods. The TimelineBase instance itself does not get
        # its own bbid.
        self.interval = interval
        self.model = model

    def add_period(self, period):
        """


        TimelineBase.add_period() -> None

        --``period`` is a TimePeriod or TimePeriodBase object

        Method configures period and records it in the instance under the
        period's end_date.
        """
        period = self._configure_period(period)
        self[period.end] = period

    def copy(self):
        """


        TimeLineBase.copy() -> obj


        Method returns a copy of the instance.
        """
        result = copy.copy(self)
        for key, value in self.items():
            result[key] = value.copy()
            result[key].relationships.set_parent(result)

        return result

    def find_period(self, query):
        """


        TimelineBase.find_period() -> TimePeriod


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

    def get_ordered(self):
        """


        TimelineBase.get_ordered() -> list


        Method returns list of periods in instance, ordered from earliest to
        latest endpoint.
        """
        return list(self.iter_ordered())

    def iter_ordered(self, open=None, exit=None, shut=None):
        """


        TimelineBase.iter_ordered() -> iter

        --``open`` date, soft start, if falls in period, iteration starts
        --``exit`` date, soft stop, if falls in period, last shown
        --``shut`` date, hard stop, if not exact period end, iteration stops

        Method iterates over periods in order, starting with the one in which
        ``open`` falls, and ending with the one including ``exit``.
        """
        for end_date, period in sorted(self.items()):
            if open and open > period.end:
                continue
            if exit and exit < period.start:
                break
            if shut and shut < period.end:
                break
            yield period

    # *************************************************************************#
    #                           NON-PUBLIC METHODS                             #
    # *************************************************************************#

    def _configure_period(self, period):
        """


        TimelineBase._configure_period() -> period


        Method sets period's namespace id to that of the TimeLine, then returns
        period.
        """
        model_namespace = self.id.namespace
        period.id.set_namespace(model_namespace)
        # Period has only a pointer to the Model.namespace_id; periods don't
        # have their own bbids.
        period.relationships.set_parent(self)

        # end dates of the past and future periods
        try:
            period.past_end = max(
                (day for day in self.keys() if day < period.end)
            )
        except:
            period.past_end = None
        try:
            period.next_end = min(
                (day for day in self.keys() if day > period.end)
            )
        except:
            period.next_end = None
        # link adjacent periods
        if period.past_end:
            past_period = self[period.past_end]
            past_period.next_end = period.end
        if period.next_end:
            next_period = self[period.next_end]
            next_period.past_end = period.end

        return period
