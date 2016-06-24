# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL
# Blackbird Environment
# Module: data_structures.system.summary_builder
"""

Module defines SummaryBuilder class. SummaryBuilder holds functionality to
generate financial summaries.
====================  =========================================================
Attribute             Description
====================  =========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
SummaryBuilder        worker class for building financial summaries
====================  =========================================================
"""




# imports
import calendar
import copy

from datetime import date
from dateutil.relativedelta import relativedelta

import bb_exceptions

from data_structures.modelling.financials import Financials
from data_structures.modelling.period_summary import PeriodSummary
from data_structures.modelling.timeline_summary import TimelineSummary
from data_structures.modelling.unit_summary import UnitSummary




# globals
# n/a

# classes
class SummaryBuilder:
    """

    SummaryBuilder is a worker class that is used by TimeLine and can be used
    by Topics to calculate summaries of financials and statements.
    ====================  =====================================================
    Attribute             Description
    ====================  =====================================================

    DATA:
    fiscal_year_end       date; end of fiscal year default = 12/31/current year
    summaries             dict; holds TimelineSummary objects keyed by interval
    time_line             pointer to TimeLine containing relevant financials

    FUNCTIONS:
    get_balance_summary()    returns starting and ending balance summaries
    get_financials_summary() returns summary of all financials over an interval
    get_statement_summary()  returns summary of a statement over an interval
    make_annual_summaries()  makes annual summaries and stores on time_line
    make_quarterly_summaries() makes quarterly summaries and stores on time_line
    make_summaries()      makes periodic summaries and stores on time_line
    ====================  =====================================================
    """

    ANNUAL_KEY = "annual"
    QUARTERLY_KEY = "quarterly"

    def __init__(self, timeline):
        self._fiscal_year_end = None
        self.summaries = dict()
        self.time_line = timeline

    @property
    def fiscal_year_end(self):
        if not self._fiscal_year_end:
            year = self.time_line.current_period.end.year
            fye = date(year, 12, 31)
        else:
            fye = self._fiscal_year_end

        return fye

    @fiscal_year_end.setter
    def fiscal_year_end(self, fye):
        # maybe make fiscal_year_end a property and do this on assignment
        last_day = calendar.monthrange(fye.year, fye.month)[1]
        if last_day - fye.day > fye.day:
            # closer to the beginning of the month, use previous month
            # for fiscal_year_end
            temp = fye - relativedelta(months=1)
            last_month = temp.month
            last_day = calendar.monthrange(fye.year, last_month)[1]

            fye = date(fye.year, last_month, last_day)
        else:
            # use end of current month
            last_day = calendar.monthrange(fye.year, fye.month)[1]
            fye = date(fye.year, fye.month, last_day)

        self._fiscal_year_end = fye

    def get_balance_summary(self, bu_bbid, start_date, end_date):
        """


        SummaryBuilder.get_balance_summary() -> dict

        --``bu_bbid`` is the id of the business unit you wish to summarize
        --``start`` is the date to start summarizing balance sheets
        --``end`` is the date to stop summarizing balance sheets

        Method returns a dictionary with two keys "starting" and "ending" which
        contains the starting and ending balance sheets over the specified
        period.

        Starting balance will correspond to the starting balance sheet in the
        period containing ``start``.  Ending balance will correspond to
        the ending balance sheet in the period containing ``end``.
        """

        # get starting period
        start_period = self.time_line.find_period(start_date)
        start_bu = start_period.bu_directory[bu_bbid]

        if not start_bu.life.alive or not start_bu.filled:
            c = "The specified business unit cannot be included in summary; " \
                "unit is either not alive or not filled."
            raise bb_exceptions.BBAnalyticalError(c)

        start_bal = start_bu.financials.starting.copy()
        start_bal.link_to(start_bu.financials.starting)

        # get ending period
        end_period = self.time_line.find_period(end_date)
        end_bu = end_period.bu_directory[bu_bbid]

        if not end_bu.life.alive or not end_bu.filled:
            c = "The specified business unit cannot be included in summary; " \
                "unit is either not alive or not filled."
            raise bb_exceptions.BBAnalyticalError(c)

        end_bal = end_bu.financials.ending.copy()
        end_bal.link_to(end_bu.financials.ending)

        out = dict()
        out["starting"] = start_bal
        out["ending"] = end_bal

        return out

    def get_financials_summary(self, bu_bbid, start, end):
        """


        SummaryBuilder.get_financials_summary() -> Financials

        --``bu_bbid`` is the id of the business unit you wish to summarize
        --``start`` is the date to start summarizing financials
        --``end`` is the date to stop summarizing finanacials

        Method returns a Financials object containing summarized statements and
        balance sheets.  Method delegates to get_balance_summary() and
        get_statement_summary() for most of its work.
        """

        # delegate to get_statement_summary and get_balance_summary
        # store results in a Financials() object
        fins_out = Financials()
        for name in ["overview", "income", "cash"]:
            new_statement = self.get_statement_summary(bu_bbid,
                                                       start,
                                                       end,
                                                       name)
            fins_out.__dict__[name] = new_statement

        balances = self.get_balance_summary(bu_bbid, start, end)

        fins_out.starting = balances["starting"]
        fins_out.ending = balances["ending"]

        return fins_out

    def get_statement_summary(self, bu_bbid, start, end, statement_name):
        """


        SummaryBuilder.get_statement_summary() -> Statement

        --``bu_bbid`` is the id of the business unit you wish to summarize
        --``start`` is the date to start summarizing statement
        --``end`` is the date to stop summarizing statement
        --``statement_name`` is the name of the statement you wish to summarize

        Method returns a Statement() object that contains the summarized values
        for the specified period.  Method summarizes entire periods from period
        containing ``start`` date to (inclusive) period containing ``end`` date.
        """

        if statement_name not in ["overview", "income", "cash"]:
            c = 'Method only works for overview, income, and cash statements'
            raise bb_exceptions.BBAnalyticalError(c)

        # loop through time periods from start_date to end_date
        # pull business units out
        period = self.time_line.find_period(start)

        bu = period.bu_directory[bu_bbid]

        statement = getattr(bu.financials, statement_name)
        summary_statement = statement.copy()
        summary_statement.reset()
        for line in summary_statement.get_full_ordered():
            line.set_hardcoded(False)

        # loop while end date is in the future or current period, break when
        # end date is in the current period
        while period.end < end or (period.start <= end <= period.end):
            bu = period.bu_directory[bu_bbid]

            if not bu.life.alive or not bu.filled:
                c = "The specified business unit cannot be included in " \
                    "summary; unit is either not alive or not filled."
                raise bb_exceptions.BBAnalyticalError(c)

            statement = getattr(bu.financials, statement_name)
            label = calendar.month_name[period.end.month]
            summary_statement.increment(statement, consolidating=True,
                                        xl_label=label)

            if period.start <= end <= period.end:
                break
            else:
                period = period.future

        return summary_statement

    def make_annual_summaries(self, bu_bbid=None, recur=False):
        """


        SummaryBuilder.make_annual_summaries() -> None

        --``bu_bbid`` is the id of the business unit you wish to summarize
        --``recur`` whether or not to calculate summaries for component bu's

        Method delegates to make_summaries() to calculate annual summaries for
        the business unit indicated by bu_bbid.  If bu_bbid is not
        provided, method will use the bbid of the top-level business unit
        (company) in the current period.

        If recur = True, method will also calculate summaries for all component
        business units.

        Calculated summaries are stored in time_line.summaries and keyed by
        ANNUAL_KEY and 3:
        model.summaries[self.ANNUAL_KEY] is model.summaries[12]
        True
        """

        # if bbid not provided, uses top-level business unit (company)
        if not bu_bbid:
            bu_bbid = self.time_line.current_period.content.id.bbid

        self.make_summaries(bu_bbid, 12, recur=recur)
        self.summaries[self.ANNUAL_KEY] = self.summaries[12]

    def make_quarterly_summaries(self, bu_bbid=None, recur=False):
        """


        SummaryBuilder.make_quarterly_summaries() -> None

        --``bu_bbid`` is the id of the business unit you wish to summarize
        --``recur`` whether or not to calculate summaries for component bu's

        Method delegates to make_summaries() to calculate quarterly summaries
        for the business unit indicated by bu_bbid.  If bu_bbid is not
        provided, method will use the bbid of the top-level business unit
        (company) in the current period.

        If recur = True, method will also calculate summaries for all component
        business units.

        Calculated summaries are stored in time_line.summaries and keyed by
        self.QUARTERLY_KEY and 3:
        model.summaries[self.QUARTERLY_KEY] is model.summaries[3]
        True
        """

        # if bbid not provided, uses top-level business unit (company)
        if not bu_bbid:
            bu_bbid = self.time_line.current_period.content.id.bbid

        self.make_summaries(bu_bbid, 3, recur=recur)
        self.summaries[self.QUARTERLY_KEY] = self.summaries[3]

    def make_summaries(self, bu_bbid, interval, recur=False):
        """


        SummaryBuilder.make_summaries() -> None

        --``bu_bbid`` is the id of the business unit you wish to summarize
        --``interval`` is the period (in months) over which to summarize
        --``recur`` whether or not to calculate summaries for component bu's

        Method calculates financial summaries over the given interval for the
        specified business unit (bu_bbid). Summaries start at the beginning of
        the current fiscal year and are made at the specified interval until
        the end of the time_line is reached.

        Example:
            fiscal year start = 1/1/2015
            interval = 3

            Summaries are made for:
            1/1/2015 - 3/31/2015
            4/1/2015 - 6/30/2015
            7/1/2015 - 9/30/2015
            10/1/2015 - 12/31/2015
            1/1/2016 - 3/31/2016
            And so forth until the end of the time_line is reached...

        If recur = True, method will also calculate summaries for all component
        business units.

        Calculated summaries are stored in time_line.summaries and are keyed by
        interval.
        """

        # Get working value for fiscal_year_end
        fye = self.fiscal_year_end

        # make the building blocks to hold this set of summaries
        timeline_summary = TimelineSummary(interval)
        timeline_summary.id.set_namespace(self.time_line.id.namespace)

        # Start at the beginning of the current fiscal year
        fiscal_year_start = fye + relativedelta(years=-1, months=+1)

        start_pointer = fiscal_year_start
        end_pointer = self._get_interval_end(start_pointer, interval-1)
        # start pointer is inclusive, need to include this TimePeriod
        last_period_end = max(self.time_line.keys())
        while end_pointer <= last_period_end:
            period_summary = PeriodSummary(start_pointer, end_pointer)
            unit_summary = self._get_unit_summary(bu_bbid,
                                                  start_pointer,
                                                  end_pointer,
                                                  period_summary,
                                                  recur)

            if unit_summary:
                period_summary.set_content(unit_summary)
                timeline_summary.add_period(period_summary)

            start_pointer = end_pointer + relativedelta(months=1)
            start_pointer = self._get_month_start(start_pointer)
            end_pointer = self._get_interval_end(start_pointer, interval-1)

        self.summaries[interval] = timeline_summary

    #*************************************************************************#
    #                          NON-PUBLIC METHODS                             #
    #*************************************************************************#

    def _find_first_alive(self, bu_bbid, start, end):
        """


        SummaryBuilder._find_first_alive() -> date

        --``bu_bbid`` is the id of the business unit you wish to summarize
        --``start`` is the first date to consider
        --``end`` is the last date to consider

        Method finds first period between (inclusive) start and end dates in
        which the specified business unit is alive. Method returns period.start
        """

        try:
            period = self.time_line.find_period(start)
        except KeyError:
            period = self.time_line[min(self.time_line.keys())]

        period_found = False
        new_start = None
        while period.end <= end:
            try:
                temp = period.bu_directory[bu_bbid]
            except KeyError:
                period = period.future
            else:
                if not temp.life.alive or not temp.filled:
                    period = period.future
                else:
                    period_found = True
                    break

            if not period:
                break

        if period_found:
            new_start = period.start

        return new_start

    def _find_last_alive(self, bu_bbid, start, end):
        """


        SummaryBuilder._find_first_alive() -> date

        --``bu_bbid`` is the id of the business unit you wish to summarize
        --``start`` is the earliest date to consider
        --``end`` is the latest date to consider

        Method finds latest period between (inclusive) start and end dates in
        which the specified business unit is alive. Method returns period.end
        """
        period_found = False
        new_end = None

        first = min(self.time_line.keys())

        if end >= first:
            period = self.time_line.find_period(end)

            while period.start >= start:
                try:
                    temp = period.bu_directory[bu_bbid]
                except KeyError:
                    period = period.past
                    if not period:
                        break
                else:
                    if not temp.life.alive or not temp.filled:
                        period = period.past
                    else:
                        period_found = True
                        break

                if not period:
                    break

            if period_found:
                new_end = period.end

        return new_end

    @staticmethod
    def _get_interval_end(curr_date, interval):
        """
        Method adds specified number of months to the provided date and returns
        """
        end_date = curr_date + relativedelta(months=interval)
        last_day = calendar.monthrange(end_date.year, end_date.month)[1]
        end_date = date(end_date.year, end_date.month, last_day)

        return end_date

    @staticmethod
    def _get_month_start(chk_date):
        """
        Method returns date corresponding to first of current month
        """
        start = date(chk_date.year, chk_date.month, 1)
        return start

    def _get_endpoints(self, bu_bbid, start, end):
        """


        SummaryBuilder._get_endpoints() -> tuple(start, end, complete)

        --``bu_bbid`` is the id of the business unit you wish to summarize
        --``start`` is the first date to consider
        --``end`` is the last date to consider

        Method finds period during which business unit is alive within the
        given date range and returns relevant start and end dates.  If unit is
        dead (or not yet born) during some or all of the period,
        complete = False, if unit is alive during the entire period,
        complete = True.
        """
        new_st_date = self._find_first_alive(bu_bbid, start, end)
        new_ed_date = self._find_last_alive(bu_bbid, start, end)

        complete = False
        if new_st_date == start and new_ed_date == end:
            complete = True

        return new_st_date, new_ed_date, complete

    def _get_unit_summary(self, bu_bbid, start, end, period, recur=False):
        """


        SummaryBuilder._get_unit_summary() -> UnitSummary

        --``bu_bbid`` is the id of the business unit you wish to summarize
        --``start`` is the date to start summarizing statement
        --``end`` is the date to stop summarizing statement
        --``period`` is the PeriodSummary object in which to place unit
        --``recur`` whether or not to calculate summaries for component bu's

        Method delegates to get_financials_summary() to calculate the summary
        of financials for the given business unit over the given period.

        IF recur = True, method will also calculate summaries for all component
        business units.
        """

        # get bu from current period to use as template
        template_bu = self.time_line.current_period.bu_directory[bu_bbid]

        # here get actual start and end points to use
        catch_all = self._get_endpoints(bu_bbid, start, end)
        start_date = catch_all[0]
        end_date = catch_all[1]
        complete = catch_all[2]

        unit_summary = None
        if start_date and end_date:
            summary_fins = self.get_financials_summary(bu_bbid,
                                                       start_date,
                                                       end_date)

            unit_summary = UnitSummary(template_bu.name)

            # intentionally keeping source BU's bbid so we can find it later
            unit_summary.id = copy.deepcopy(template_bu.id)
            unit_summary.set_financials(summary_fins)
            unit_summary.complete = complete
            unit_summary.period = period
            unit_summary.periods_used = end_date.month - start_date.month + 1

            if recur:
                for comp in template_bu.components.get_all():
                    comp_summary = self._get_unit_summary(comp.id.bbid,
                                                          start,
                                                          end,
                                                          recur)
                    if comp_summary:
                        comp_summary.period = period
                        unit_summary.add_component(comp_summary)

        return unit_summary
