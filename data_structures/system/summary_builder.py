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

import chef_settings
import bb_exceptions

from data_structures.modelling.business_unit_base import BusinessUnitBase
from data_structures.modelling.financials import Financials
from data_structures.modelling.time_period_base import TimePeriodBase
from data_structures.modelling.time_line_base import TimelineBase




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
    summaries             dict; holds TimelineBase objects keyed by interval
    time_line             pointer to TimeLine containing relevant financials

    FUNCTIONS:
    get_balance_summary()    returns starting and ending balance summaries
    get_financials_summary() returns summary of all financials over an interval
    get_line_summary()       summarizes a line over time
    get_statement_summary()  returns summary of a statement over an interval
    make_annual_summaries()  makes annual summaries and stores on time_line
    make_quarterly_summaries() makes quarterly summaries and stores on time_line
    make_summaries()      makes periodic summaries and stores on time_line
    update_summaries()    update previously calculated summaries
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
        time_line = self.time_line

        if not self._fiscal_year_end:
            year = time_line.current_period.end.year
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

    def copy(self):
        """


        SummaryBuilder.copy() -> obj


        Method makes a copy of the instance, maintaining original link to
        time_line, and returns it.
        """
        result = SummaryBuilder(self.time_line)
        result._fiscal_year_end = self._fiscal_year_end
        for key, value in self.summaries.items():
            result.summaries[key] = value.copy()

        return result

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
        time_line = self.source_time_line

        # get starting period
        start_period = time_line[start_date]
        start_bu = start_period.bu_directory[bu_bbid]

        start_bal = start_bu.financials.starting.copy()
        start_bal.link_to(start_bu.financials.starting)

        # get ending period
        end_period = time_line[end_date]
        end_bu = end_period.bu_directory[bu_bbid]

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
        period = self.source_time_line[start]
        bu = period.bu_directory[bu_bbid]

        fins_out = Financials()
        for name in bu.financials.compute_order:
            new_statement = self.get_statement_summary(bu_bbid,
                                                       start,
                                                       end,
                                                       name)

            if getattr(fins_out, name, None):
                fins_out.__dict__[name] = new_statement
            else:
                idx = bu.financials.compute_order.index(name)
                fins_out.add_statement(name, statement=new_statement,
                                       position=idx)

        balances = self.get_balance_summary(bu_bbid, start, end)

        fins_out.starting = balances["starting"]
        fins_out.ending = balances["ending"]

        return fins_out

    def get_line_summary(self, summary_line, period_line, label=None):
        """


        SummaryBuilder.get_line_summary() -> None

        --``summary_line`` is a LineItem from the summary statement
        --``period_line`` is the matching LineItem from a specific time period
        --``label`` is the string label to apply to the summary line in Excel

        Method summarizes a LineItem over time based on its "sum_over_time"
        attribute.  Method will either increment the line with the period's
        line, or will set the line reference to the period line.  Method works
        recursively.
        """
        if summary_line.sum_over_time:
            summary_line.increment(period_line, consolidating=True,
                                   xl_label=label, override=True,
                                   over_time=True)
        else:
            if summary_line._details:
                for line in summary_line._details.values():
                    new_line = period_line.find_first(line.name)
                    self.get_line_summary(line, new_line, label=label)
            else:
                summary_line.set_value(period_line.value, "SummaryBuilder",
                                       override=True)

            summary_line.xl.reference.source = period_line

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
        time_line = self.source_time_line

        # loop through time periods from start_date to end_date
        # pull business units out
        period = time_line[start]
        bu = period.bu_directory[bu_bbid]

        if statement_name not in bu.financials.compute_order:
            c = 'Method only works for statements in financials.compute_order'
            raise bb_exceptions.BBAnalyticalError(c)

        statement = getattr(bu.financials, statement_name)
        summary_statement = statement.copy()
        summary_statement.reset()
        for line in summary_statement.get_full_ordered():
            line.set_hardcoded(False)

        # loop while end date is in the future or current period, break when
        # end date is in the current period
        for period in time_line.iter_ordered(open=start, exit=end):
            bu = period.bu_directory[bu_bbid]

            statement = getattr(bu.financials, statement_name)
            label = format(period.end)
            for line in summary_statement.get_ordered():
                new_line = statement.find_first(line.name)
                self.get_line_summary(line, new_line, label=label)

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
        if chef_settings.SUMMARY_INCLUDES_QUARTERS:
            # read from quarterly summary instead of actual time_line
            source = self.summaries[self.QUARTERLY_KEY]
            # summary time_line to be used in place of actual one
            self.source_time_line = source
            # simulate the current_period and find bu_bbid
            for period, base in sorted(source.items()):
                end = self.time_line.current_period.end
                if base.start <= end <= base.end:
                    bu_bbid = next(iter(base.bu_directory))
                    self.source_time_line.current_period = base
                    break
        else:
            # if bbid not provided, uses top-level business unit (company)
            if not bu_bbid:
                bu_bbid = self.time_line.current_period.content.id.bbid
            self.source_time_line = self.time_line

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
        self.source_time_line = self.time_line

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
        time_line = self.source_time_line

        # Get working value for fiscal_year_end
        fye = self.fiscal_year_end

        # make the building blocks to hold this set of summaries
        timeline_summary = TimelineBase(interval)
        timeline_summary.id.set_namespace(time_line.id.namespace)

        # Start at the beginning of the current fiscal year
        fiscal_year_start = fye + relativedelta(years=-1, months=+1)

        start_pointer = fiscal_year_start
        end_pointer = self._get_interval_end(start_pointer, interval - 1)
        # start pointer is inclusive, need to include this TimePeriod
        last_period_end = max(time_line.keys())
        while start_pointer <= last_period_end:
            period_summary = TimePeriodBase(start_pointer, end_pointer)

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
            end_pointer = self._get_interval_end(start_pointer, interval - 1)

        self.summaries[interval] = timeline_summary

    def update_summaries(self):
        """


        SummaryBuilder.update_summaries() -> None


        Method updates all calculated summaries.
        """
        omit_keys = set([self.ANNUAL_KEY, self.QUARTERLY_KEY])
        intervals = set(self.summaries.keys()) - omit_keys

        for interval in intervals:
            self._update_summary(interval)

    # *************************************************************************#
    #                           NON-PUBLIC METHODS                             #
    # *************************************************************************#

    @staticmethod
    def _do_summary_calculations(real_bu, unit_summary):

        # loop through drivers in real_bu.drivers and copy all
        # "summary_calculate" drivers to unit_summary
        for bbid in sorted(real_bu.drivers.dr_directory.keys()):
            dr = real_bu.drivers.dr_directory[bbid]
            if dr.summary_calculate:
                unit_summary.drivers.add_item(dr.copy())

        summary_fins = unit_summary.financials
        for statement in summary_fins.ordered:
            if statement:
                for line in statement.get_full_ordered():
                    if line.summary_calculate:
                        line.clear()
                        unit_summary._derive_line(line)

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

        Method finds periods during which business unit is alive within the
        given date range and returns the end dates of the first and the last
        such periods. If unit is
        dead (or not yet born) during some or all of the period,
        complete = False, if unit is alive during the entire period,
        complete = True.
        """
        time_line = self.source_time_line
        new_op_date = None
        new_st_date = None
        new_ed_date = None
        month_count = None

        for period in time_line.iter_ordered(open=start, exit=end):
            if period.end < time_line.current_period.end:
                continue
            if bu_bbid in period.bu_directory:
                # switch on start date
                if new_st_date is None:
                    new_op_date = period.start
                    new_st_date = period.end
                # switch on end date
                new_ed_date = period.end

        complete = False
        if new_st_date and new_ed_date:
            if new_op_date == start and new_ed_date == end:
                complete = True
            month_count = \
                new_ed_date.year * 100 + new_ed_date.month - \
                new_op_date.year * 100 - new_op_date.month + 1

        return new_st_date, new_ed_date, complete, month_count

    def _get_unit_summary(self, bu_bbid, start, end, period, recur=False):
        """


        SummaryBuilder._get_unit_summary() -> BusinessUnitBase

        --``bu_bbid`` is the id of the business unit you wish to summarize
        --``start`` is the date to start summarizing statement
        --``end`` is the date to stop summarizing statement
        --``period`` is the TimePeriodBase object in which to place unit
        --``recur`` whether or not to calculate summaries for component bu's

        Method delegates to get_financials_summary() to calculate the summary
        of financials for the given business unit over the given period.

        IF recur = True, method will also calculate summaries for all component
        business units.
        """
        # get bu from current period to use as template
        time_line = self.source_time_line
        template_bu = time_line.current_period.bu_directory[bu_bbid]

        # here get actual start and end points to use
        catch_all = self._get_endpoints(bu_bbid, start, end)
        # start_date and end_date are existing keys in time_line
        start_date, end_date, complete, month_count = catch_all

        unit_summary = None
        if start_date and end_date:
            summary_fins = self.get_financials_summary(bu_bbid,
                                                       start_date,
                                                       end_date)

            unit_summary = BusinessUnitBase(template_bu.name)

            # intentionally keeping source BU's bbid so we can find it later
            unit_summary.id = copy.deepcopy(template_bu.id)
            unit_summary.set_financials(summary_fins)
            unit_summary.complete = complete
            unit_summary.period = period
            unit_summary.periods_used = month_count

            check_period = time_line.find_period(end_date)
            check_bu = check_period.bu_directory[bu_bbid]
            self._do_summary_calculations(check_bu, unit_summary)

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

    def _update_balance_summary(self, unit_summary, start, end):
        """


        SummaryBuilder._update_balance_summary() ->  None

        --``unit_summary`` is the id of the business unit you wish to summarize
        --``start`` is the date to start summarizing balance sheets
        --``end`` is the date to stop summarizing balance sheets

        Method updates starting and ending balance sheet summaries.

        Starting balance will correspond to the starting balance sheet in the
        period containing ``start``.  Ending balance will correspond to
        the ending balance sheet in the period containing ``end``.
        """
        bu_bbid = unit_summary.id.bbid

        # get starting period
        start_period = self.time_line.find_period(start)
        start_bu = start_period.bu_directory[bu_bbid]

        if not start_bu.life.alive or not start_bu.filled:
            c = "The specified business unit cannot be included in summary; " \
                "unit is either not alive or not filled."
            raise bb_exceptions.BBAnalyticalError(c)

        start_bal = unit_summary.financials.starting
        start_bal.increment(start_bu.financials.ending, consolidating=False)
        start_bal.reset()

        start_bal.link_to(start_bu.financials.starting)

        # get ending period
        end_period = self.time_line.find_period(end)
        end_bu = end_period.bu_directory[bu_bbid]

        if not end_bu.life.alive or not end_bu.filled:
            c = "The specified business unit cannot be included in summary; " \
                "unit is either not alive or not filled."
            raise bb_exceptions.BBAnalyticalError(c)

        end_bal = unit_summary.financials.ending
        end_bal.increment(end_bu.financials.ending, consolidating=False)
        end_bal.reset()

        end_bal.link_to(end_bu.financials.ending)

    def _update_financials_summary(self, unit_summary, start, end):
        """


        SummaryBuilder.get_financials_summary() -> Financials

        --``unit_summary`` is the UnitSummary instance to update
        --``start`` is the date to start summarizing financials
        --``end`` is the date to stop summarizing finanacials

        Method delegates to _update_statement() and _update_balance_summary()
        to to update financials for unit_summary.
        """

        # delegate to get_statement_summary and get_balance_summary
        # store results in a Financials() object
        for name in unit_summary.financials.compute_order:
            self._update_statement(unit_summary, start, end, name)

        self._update_balance_summary(unit_summary, start, end)

    def _update_statement(self, unit_summary, start, end, statement_name):
        """


        SummaryBuilder.get_statement_summary() -> Statement

        --``unit_summary`` is the UnitSummary instance to update
        --``start`` is the date to start summarizing statement
        --``end`` is the date to stop summarizing statement
        --``statement_name`` is the name of the statement you wish to update

        Method updates the Statement() object that contains summarized values
        for the specified period.  Method summarizes entire periods from period
        containing ``start`` date to (inclusive) period containing ``end`` date.
        """
        bu_bbid = unit_summary.id.bbid

        if statement_name not in unit_summary.financials.compute_order:
            c = 'Method only works for statements in financials.compute_order'
            raise bb_exceptions.BBAnalyticalError(c)

        # loop through time periods from start_date to end_date
        # pull business units out
        period = self.time_line.find_period(start)

        summary_statement = getattr(unit_summary.financials, statement_name)
        summary_statement.reset()

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
            for line in summary_statement.get_ordered():
                new_line = statement.find_first(line.name)
                self.get_line_summary(line, new_line, label=label)

            if period.start <= end <= period.end:
                break
            else:
                period = period.future

        return summary_statement

    def _update_summary(self, interval):
        """


        SummaryBuilder._update_unit_summary() -> None

        --``interval`` identifies the summary to update

        Method delegates to _update_unit_summary() do the actual work of
        updating the financial summaries over the given interval.
        """
        summary = self.summaries[interval]
        first_date = min(summary.keys())
        first_period = summary[first_date]
        content = first_period.content
        bu_bbid = content.id.bbid

        # Get working value for fiscal_year_end
        fye = self.fiscal_year_end

        # make the building blocks to hold this set of summaries
        timeline_summary = self.summaries[interval]

        # Start at the beginning of the current fiscal year
        fiscal_year_start = fye + relativedelta(years=-1, months=+1)

        start_pointer = fiscal_year_start
        end_pointer = self._get_interval_end(start_pointer, interval - 1)

        # start pointer is inclusive, need to include this TimePeriod
        last_period_end = max(self.time_line.keys())
        while end_pointer <= last_period_end:
            period_summary = timeline_summary.find_period(end_pointer)

            if period_summary:
                try:
                    unit_summary = period_summary.bu_directory[bu_bbid]
                except KeyError:
                    pass
                else:
                    self._update_unit_summary(unit_summary,
                                              start_pointer,
                                              end_pointer)

            start_pointer = end_pointer + relativedelta(months=1)
            start_pointer = self._get_month_start(start_pointer)
            end_pointer = self._get_interval_end(start_pointer, interval - 1)

    def _update_unit_summary(self, unit_summary, start, end):
        """


        SummaryBuilder._update_unit_summary() -> None

        --``unit_summary`` is the UnitSummary instance to update
        --``start`` is the date to start the financials update
        --``end`` is the date to stop the financials update

        Method delegates to _update_financials_summary() to calculate the
        do the actual work of updating the financials for the given business
        unit over the given period.

        Method recursively updates any component business unit summaries, where
        applicable.

        If the unit no longer exists in the given period, the
        unit_summary is deleted.
        """
        bu_bbid = unit_summary.id.bbid
        # get bu from current period to use as template
        template_bu = self.time_line.current_period.bu_directory[bu_bbid]

        # here get actual start and end points to use
        catch_all = self._get_endpoints(bu_bbid, start, end)
        start_date = catch_all[0]
        end_date = catch_all[1]
        complete = catch_all[2]

        if start_date and end_date:
            self._update_financials_summary(unit_summary, start_date, end_date)

            unit_summary.complete = complete
            unit_summary.periods_used = end_date.month - start_date.month + 1

            for comp in unit_summary.components.get_all():
                self._update_unit_summary(comp, start_date, end_date)
        else:
            del unit_summary
