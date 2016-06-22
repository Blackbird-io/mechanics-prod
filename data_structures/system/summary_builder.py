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




class SummaryBuilder:

    def __init__(self, timeline):
        self.time_line = timeline

    # Wrapper functions
    def make_annual_summaries(self, bu_bbid=None, recur=False):
        # optionally recursive for component business units
        # calculates all available annual summaries for current period and all
        # available future periods
        if not bu_bbid:
            bu_bbid = self.time_line.current_period.content.id.bbid

        self.make_summaries(bu_bbid, 12, recur)
        self.time_line.summaries["annual"] = self.time_line.summaries[12]

    def make_quarterly_summaries(self, bu_bbid=None, recur=False):
        # optionally recursive for component business units
        # calculates all available quarterly summaries for current period and all
        # available future periods
        # if bbid not provided, uses top-level business unit (company)
        if not bu_bbid:
            bu_bbid = self.time_line.current_period.content.id.bbid

        self.make_summaries(bu_bbid, 3, recur)
        self.time_line.summaries["quarterly"] = self.time_line.summaries[3]

    @staticmethod
    def get_previous_month(month):
        if month > 1:
            return month - 1
        else:
            return 12

    @staticmethod
    def get_next_month(month):
        if month < 12:
            return month + 1
        else:
            return 1

    @staticmethod
    def get_interval_end(curr_date, interval):
        return curr_date + relativedelta(months=interval)

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

        if not self.time_line.fiscal_year_end:
            fye = date(2015, 12, 31)
            last_month = fye.month
        else:
            fye = self.time_line.fiscal_year_end
            last_month = fye.month
            last_day = calendar.monthrange(fye.year, fye.month)[1]
            if last_day - fye.day > fye.day:
                last_month = self.get_previous_month(fye.month)
                last_day = calendar.monthrange(fye.year, last_month)[1]

            fye = date(fye.year, last_month, last_day)
            # maybe make FYE a property and do this on assignment

        # get bu from current period to use as template
        template_bu = self.time_line.current_period.bu_directory[bu_bbid]

        # make the building blocks to hold this set of summaries
        timeline_summary = TimelineSummary(interval)
        timeline_summary.id.set_namespace(self.time_line.id.namespace)

        # Start in the current year, at the beginning of the fiscal year
        fiscal_year_start = fye + relativedelta(years=-1, months=+1)

        start_pointer = fiscal_year_start
        # start pointer is inclusive, need to include this TimePeriod
        last_period_end = max(self.time_line.keys())
        while start_pointer + relativedelta(months=interval) <= last_period_end:
            end_pointer = self.get_interval_end(start_pointer, interval-1)
            # end pointer is inclusive, need to include this TimePeriod

            use_start = date(start_pointer.year, start_pointer.month, 1)

            end_year = end_pointer.year
            end_month = end_pointer.month
            end_day = calendar.monthrange(end_year, end_month)[1]
            use_end = date(end_year, end_month, end_day)
            period_summary = PeriodSummary(use_start, use_end)
            summary_fins, complete = self.get_financials_summary(bu_bbid,
                                                                 start_pointer,
                                                                 end_pointer)

            if summary_fins:
                unit_summary = UnitSummary(template_bu.name)
                unit_summary.id = copy.deepcopy(template_bu.id)
                unit_summary.set_financials(summary_fins)
                unit_summary.complete = complete

                # intentionally keeping source BU's bbid so we can find it later
                period_summary.set_content(unit_summary, updateID=False)

                timeline_summary.add_period(period_summary)

            start_pointer = self.get_interval_end(start_pointer, interval)

        self.time_line.summaries[interval] = timeline_summary

    def get_financials_summary(self, bu_bbid, start_date, end_date):
        # delegate to get_statement_summary and get_balance_summary
        # store results in
        fins_out = Financials()
        all_nones = True
        for name in ["overview", "income", "cash"]:
            new_statement, complete = self.get_statement_summary(bu_bbid,
                                                                 start_date,
                                                                 end_date,
                                                                 name)
            fins_out.__dict__[name] = new_statement
            if new_statement:
                all_nones = False

        balances, bal_complete = self.get_balance_summary(bu_bbid,
                                                          start_date,
                                                          end_date)

        fins_out.starting = balances["starting"]
        if balances["starting"]:
            all_nones = False

        fins_out.ending = balances["ending"]
        if balances["ending"]:
            all_nones = False

        if all_nones:
            fins_out = None

        return fins_out, complete

    def get_statement_summary(self, bu_bbid, start_date, end_date, statement_name):

        if statement_name not in ["overview", "income", "cash"]:
            c = 'Method only works for overview, income, and cash statements'
            raise bb_exceptions.BBAnalyticalError(c)

        # loop through time periods from start_date to end_date
        # pull business units out
        complete = True
        period = self.time_line.find_period(start_date)

        bu = None
        while period.end <= end_date:
            try:
                bu = period.bu_directory[bu_bbid]
            except KeyError:
                complete = False
                period = period.future
            else:
                break

        if not bu:
            summary_statement = None
            complete = False
        else:
            statement = getattr(bu.financials, statement_name, None)
            summary_statement = statement.copy()
            summary_statement.reset()

            while period.end <= end_date:
                bu = period.bu_directory[bu_bbid]
                if not bu.life.alive or not bu.filled:
                    complete = False

                statement = getattr(bu.financials, statement_name, None)
                if statement:
                    summary_statement.increment(statement, consolidating=True)

                period = period.future
                if not period:
                    if bu.period.end + relativedelta(months=1) <= end_date:
                        complete = False
                    break

        return summary_statement, complete

    def get_balance_summary(self, bu_bbid, start_date, end_date):
        """


        SummaryBuilder.get_balance_summary() -> (dict, bool)

        Args:
            bu_bbid:
            start_date:
            end_date:

        Returns:

        """
        complete = True

        # get starting period
        start_period = self.time_line.find_period(start_date)
        start_bu = None
        while start_period.end <= end_date:
            try:
                start_bu = start_period.bu_directory[bu_bbid]
            except KeyError:
                complete = False
                start_period = start_period.future
                if not start_period:
                    complete = False
                    break
            else:
                break

        if not start_bu:
            complete = False
            out = dict()
            out["starting"] = None
            out["ending"] = None

        else:
            if not start_bu.filled:
                start_bu.fill_out()

            if not start_bu.life.alive:
                complete = False

            start_bal = start_bu.financials.starting.copy()
            start_bal.link_to(start_bu.financials.starting)

            # get ending period
            end_period = None
            while end_date >= start_period.end:
                try:
                    end_period = self.time_line.find_period(end_date)
                except KeyError:
                    end_date = end_date - relativedelta(months=1)
                else:
                    break

            if not end_period:
                raise bb_exceptions.BBAnalyticalError

            end_bu = None
            while end_period.end >= start_period.end:
                try:
                    end_bu = end_period.bu_directory[bu_bbid]
                except KeyError:
                    complete = False
                    end_period = end_period.past
                    if not end_period:
                        complete = False
                        break
                else:
                    break

            if not end_bu:
                raise bb_exceptions.BBAnalyticalError

            if not end_bu.filled:
                end_bu.fill_out()

            if not end_bu.life.alive:
                complete = False

            end_bal = end_bu.financials.ending.copy()
            end_bal.link_to(end_bu.financials.ending)

            out = dict()
            out["starting"] = start_bal
            out["ending"] = end_bal

        return out, complete
