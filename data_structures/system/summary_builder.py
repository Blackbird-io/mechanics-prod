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
SummaryBuilder        driver class for building financial summaries
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
    def __init__(self, timeline):
        self.time_line = timeline

    def get_balance_summary(self, bu_bbid, start_date, end_date):
        """


        SummaryBuilder.get_balance_summary() -> (dict, bool)

        --``bu_bbid`` is the id of the business unit you wish to summarize
        --``start_date`` is the date to start summarizing balance sheets
        --``end_date`` is the date to stop summarizing balance sheets

        Method
        """

        # get starting period
        start_period = self.time_line.find_period(start_date)
        start_bu = start_period.bu_directory[bu_bbid]

        if not start_bu.filled:
            start_bu.fill_out()

        if not start_bu.life.alive:
            raise bb_exceptions.BBAnalyticalError

        start_bal = start_bu.financials.starting.copy()
        start_bal.link_to(start_bu.financials.starting)

        # get ending period
        end_period = self.time_line.find_period(end_date)
        end_bu = end_period.bu_directory[bu_bbid]

        if not end_bu.filled:
            end_bu.fill_out()

        if not end_bu.life.alive:
            raise bb_exceptions.BBAnalyticalError

        end_bal = end_bu.financials.ending.copy()
        end_bal.link_to(end_bu.financials.ending)

        out = dict()
        out["starting"] = start_bal
        out["ending"] = end_bal

        return out

    def get_financials_summary(self, bu_bbid, start_date, end_date):
        # delegate to get_statement_summary and get_balance_summary
        # store results in
        fins_out = Financials()
        for name in ["overview", "income", "cash"]:
            new_statement = self.get_statement_summary(bu_bbid,
                                                       start_date,
                                                       end_date,
                                                       name)
            fins_out.__dict__[name] = new_statement

        balances = self.get_balance_summary(bu_bbid, start_date, end_date)

        fins_out.starting = balances["starting"]
        fins_out.ending = balances["ending"]

        return fins_out

    def get_statement_summary(self, bu_bbid, start_date, end_date,
                              statement_name):

        if statement_name not in ["overview", "income", "cash"]:
            c = 'Method only works for overview, income, and cash statements'
            raise bb_exceptions.BBAnalyticalError(c)

        # loop through time periods from start_date to end_date
        # pull business units out
        period = self.time_line.find_period(start_date)

        bu = period.bu_directory[bu_bbid]

        statement = getattr(bu.financials, statement_name)
        summary_statement = statement.copy()
        summary_statement.reset()

        while period.end <= end_date:
            bu = period.bu_directory[bu_bbid]

            if not bu.filled:
                bu.fill_out()

            if not bu.life.alive:
                raise bb_exceptions.BBAnalyticalError

            statement = getattr(bu.financials, statement_name)
            summary_statement.increment(statement, consolidating=True)

            period = period.future
            if not period:
                break

        return summary_statement

    # Wrapper functions
    def make_annual_summaries(self, bu_bbid=None):
        # calculates all available annual summaries for current period and all
        # available future periods
        if not bu_bbid:
            bu_bbid = self.time_line.current_period.content.id.bbid

        self.make_summaries(bu_bbid, 12, recur=False)
        self.time_line.summaries["annual"] = self.time_line.summaries[12]

    def make_quarterly_summaries(self, bu_bbid=None):
        # calculates all available quarterly summaries for current period and
        # all available future periods
        # if bbid not provided, uses top-level business unit (company)
        if not bu_bbid:
            bu_bbid = self.time_line.current_period.content.id.bbid

        self.make_summaries(bu_bbid, 3, recur=False)
        self.time_line.summaries["quarterly"] = self.time_line.summaries[3]

    def make_summaries(self, bu_bbid, interval, recur=False):
        # optionally recursive for component business units
        # calculates financial summaries over given interval for all available
        # periods now -> future, bases off fiscal_year_end
        # here is where a lot of the work of storing and traversing is done

        if (12 % interval != 0 and interval < 12) or interval > 12:
            print("!!WARNING!!  Given interval does not correspond to cycling "
                  "over a year (12-month period)")

        if not isinstance(interval, int):
            c = "Interval must be an integer."
            raise bb_exceptions.BBAnalyticalError(c)

        # Get working value for fiscal_year_end
        if not self.time_line.fiscal_year_end:
            year = self.time_line.current_period.end.year
            fye = date(year, 12, 31)
        else:
            # maybe make fiscal_year_end a property and do this on assignment
            fye = self.time_line.fiscal_year_end
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

        # get bu from current period to use as template
        template_bu = self.time_line.current_period.bu_directory[bu_bbid]

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
            # here get actual start and end points to use
            catch_all = self._get_endpoints(bu_bbid, start_pointer, end_pointer)
            start_date = catch_all[0]
            end_date = catch_all[1]
            complete = catch_all[2]

            if start_date and end_date:
                summary_fins = self.get_financials_summary(bu_bbid,
                                                           start_date,
                                                           end_date)

                unit_summary = UnitSummary(template_bu.name)

                # intentionally keeping source BU's bbid so we can find it later
                unit_summary.id = copy.deepcopy(template_bu.id)
                unit_summary.set_financials(summary_fins)
                unit_summary.complete = complete

                period_summary = PeriodSummary(start_date, end_date)
                period_summary.set_content(unit_summary, updateID=False)

                timeline_summary.add_period(period_summary)

            start_pointer = end_pointer + relativedelta(months=1)
            end_pointer = self._get_interval_end(start_pointer, interval-1)

        self.time_line.summaries[interval] = timeline_summary

    #*************************************************************************#
    #                          NON-PUBLIC METHODS                             #
    #*************************************************************************#

    def _find_first_alive(self, bu_bbid, start, end):
        period = self.time_line.find_period(start)

        period_found = False
        new_start = None
        while period.end <= end:
            try:
                temp = period.bu_directory[bu_bbid]
            except KeyError:
                period = period.future
            else:
                if not temp.life.alive:
                    period = period.future
                else:
                    period_found = True
                    break

        if period_found:
            new_start = period.start

        return new_start

    def _find_last_alive(self, bu_bbid, start, end):
        period = self.time_line.find_period(end)

        period_found = False
        new_end = None
        while period.start >= start:
            try:
                temp = period.bu_directory[bu_bbid]
            except KeyError:
                period = period.past
            else:
                if not temp.life.alive:
                    period = period.past
                else:
                    period_found = True
                    break

        if period_found:
            new_end = period.end

        return new_end

    @staticmethod
    def _get_interval_end(curr_date, interval):
        return curr_date + relativedelta(months=interval)

    def _get_endpoints(self, bu_bbid, start_date, end_date):
        new_st_date = self._find_first_alive(bu_bbid, start_date, end_date)
        new_ed_date = self._find_last_alive(bu_bbid, start_date, end_date)

        complete = False
        if new_st_date == start_date and new_ed_date == end_date:
            complete = True

        return new_st_date, new_ed_date, complete
