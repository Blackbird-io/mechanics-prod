# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL

# Blackbird Environment
# Module: data_structures.system.summary_maker
"""

Module defines SummaryMaker class. SummaryMaker generates financial summaries.
====================  =========================================================
Attribute             Description
====================  =========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
SummaryMaker        worker class for building financial summaries
====================  =========================================================
"""




# imports
import logging
import calendar
import copy
import datetime as DT

from dateutil.relativedelta import relativedelta

import bb_settings
import bb_exceptions

from data_structures.modelling.business_unit_base import BusinessUnitBase
from data_structures.modelling.financials import Financials
from data_structures.modelling.time_period_base import TimePeriodBase
from data_structures.modelling.time_line_base import TimelineBase




# globals
logger = logging.getLogger(bb_settings.LOGNAME_MAIN)

# classes
class SummaryMaker:
    """

    SummaryMaker is a for incremental build-up of quarterly and annual
    summaries of financials and statements.
    ====================  =====================================================
    Attribute             Description
    ====================  =====================================================

    DATA:
    fiscal_year_end       date; end of fiscal year default = 12/31/current year
    summaries             dict; holds TimelineBase objects keyed by interval
    time_line             pointer to TimeLine containing relevant financials
    bu_bbid               id of the unit being summarized

    FUNCTIONS:
    copy                  copy of the object
    init_summaries        basic initialization of the summary dictionaries
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
        self.time_line = timeline
        self.bu_bbid = None
        self.period_info = dict()
        self.init_summaries()

    @property
    def fiscal_year_end(self):
        """


        SummaryMaker.fiscal_year_end() -> date

        Return self._fiscal_year_end or calendar year end.
        """
        if not self._fiscal_year_end:
            year = self.time_line.current_period.end.year
            fye = DT.date(year, 12, 31)
        else:
            fye = self._fiscal_year_end

        return fye

    @fiscal_year_end.setter
    def fiscal_year_end(self, fye):
        """


        SummaryMaker.fiscal_year_end() -> date

        Set self._fiscal_year_end.
        """
        # maybe make fiscal_year_end a property and do this on assignment
        last_day = calendar.monthrange(fye.year, fye.month)[1]
        if last_day - fye.day > fye.day:
            # closer to the beginning of the month, use previous month
            # for fiscal_year_end
            temp = fye - relativedelta(months=1)
            last_month = temp.month
            last_day = calendar.monthrange(fye.year, last_month)[1]

            fye = DT.date(fye.year, last_month, last_day)
        else:
            # use end of current month
            last_day = calendar.monthrange(fye.year, fye.month)[1]
            fye = DT.date(fye.year, fye.month, last_day)

        self._fiscal_year_end = fye

    def copy(self):
        """


        SummaryMaker.copy() -> obj

        Method makes a copy of the instance, maintaining original link to
        time_line, and returns it.
        """
        result = SummaryMaker(self.time_line)
        result._fiscal_year_end = self._fiscal_year_end
        for key, value in self.summaries.items():
            result.summaries[key] = value.copy()

        return result

    def init_summaries(self):
        """


        SummaryMaker.init_summaries() -> None

        Basic initialization of the summary dictionaries.
        """
        self.summaries = dict()
        for key, periods in (
            (self.QUARTERLY_KEY, 3),
            (self.ANNUAL_KEY, 12),
        ):
            timeline_summary = TimelineBase(periods)
            timeline_summary.id.set_namespace(self.time_line.id.namespace)
            # output quarter or year being currently processed
            timeline_summary.summary_period = None
            self.summaries[key] = timeline_summary

    def parse_period(self, period):
        if not self.bu_bbid:
            self.bu_bbid = self.time_line.current_period.content.id.bbid
        self.period = period
        self.onkey = self.QUARTERLY_KEY
        # determine the quarter and the year of the period pushed to us
        self.which_quarter()
        # push month to quarters
        self.add(period)

    def which_quarter(self):
        """


        SummaryMaker.which_quarter() -> dict

        Given the period sent to us, determine which quarter and year it falls
        into, and compute the bookends of those periods.
        """
        period = self.period
        # determine end of FY in which this period falls
        year = period.end.year
        if not self._fiscal_year_end:
            yr_close = DT.date(year, 12, 31)
        else:
            month = self._fiscal_year_end.month
            last_day = calendar.monthrange(year, month)[1]
            yr_close = DT.date(year, month, last_day)
            # if FY end has passed this year, bump FY up by one year
            if yr_close < period.end:
                last_day = calendar.monthrange(year + 1, month)[1]
                yr_close = DT.date(year + 1, month, last_day)
        # first day of next FY
        yr_after = yr_close + relativedelta(days=1)
        # first day of this FY
        yr_start = yr_after + relativedelta(years=-1)
        # months left in fiscal year (0 in Dec, 11 in Jan)
        yr_left = yr_close.year * 100 + yr_close.month \
            - year * 100 - period.end.month
        # months into the fiscal year (1 in Jan, 12 in Dec)
        yr_into = 12 - yr_left
        # quarter number and months into quarter (Jan = (1, 1), Dec = (4, 3))
        qt_num, qt_into = [x + 1 for x in divmod(yr_into - 1, 3)]
        # first day of next month
        qt_after = period.end + relativedelta(days=1)
        # first day of this quarter
        qt_start = qt_after - relativedelta(months=qt_into)
        # last day of this quarter
        qt_close = qt_start + relativedelta(months=3) - relativedelta(days=1)
        # where am i in the quarter and in the year
        info = {
            self.QUARTERLY_KEY: {
                'period': (yr_close.year, qt_num),
                'enter': qt_start,
                'close': qt_close,
                'into': qt_into,
            },
            self.ANNUAL_KEY: {
                'period': yr_close.year,
                'enter': yr_start,
                'close': yr_close,
                'into': yr_into,
            },
        }
        self.period_info = info
        return info

    def add(self, source):
        """


        SummaryMaker.add() -> None

        --``source`` is monthly period or quarterly summary

        Aggregate source to the higher level summary,
        monthly -> quarterly, quarterly -> annual.
        ``source`` varies between monthly and quarterly, everything else is
        kept on the object.
        """
        # this is what we last worked on, if anything
        timeline_summary = self.summaries[self.onkey]
        summary_period = timeline_summary.summary_period

        # check if we stepped out of the target period, roll over
        if not summary_period or summary_period.end < source.end:
            # close out the summary we have been working on
            self.flush()

            # create next target period
            new_info = self.period_info[self.onkey]
            enter = new_info['enter']
            close = new_info['close']
            summary_period = TimePeriodBase(enter, close)
            summary_period.month_count = 0

            # copy BU structure from time_line.current_period
            summary_unit = self.add_content(self.bu_bbid, summary_period)

            # special handling of the first time period starting balance:
            # link to the starting balance of the first source period
            if len(timeline_summary) == 0:
                source_bu = source.bu_directory[self.bu_bbid]
                bal_enter = source_bu.financials.starting.copy()
                bal_enter.link_to(source_bu.financials.starting)
                summary_unit.financials.starting = bal_enter

            # add to timeline
            summary_period.set_content(summary_unit)
            timeline_summary.add_period(summary_period)
            timeline_summary.summary_period = summary_period

            logger.debug('{}:{} -> {}:{} new {}'.format(
                source.start, source.end,
                summary_period.start, summary_period.end, self.onkey
            ))

        # all aggregation happens here
        timeline_summary.source = source
        self.summarize()

    def flush(self):
        """


        SummaryMaker.flush() -> None

        Complete the period that we have been aggregating. Called in two ways:
        -- when we detect that next source is outside of the target period
        -- by wrap(), when there are no periods left
        When a quarter is completed, call add() in annual mode to cascade
        the finished quarter to the annual summary.
        """
        timeline_summary = self.summaries[self.onkey]

        if len(timeline_summary):
            summary_period = timeline_summary.summary_period
            # when flush() is called, source is the last processed sub-period
            source = timeline_summary.source
            # add link to ending financials of last processed source
            source_bu = source.bu_directory[self.bu_bbid]
            bal_close = source_bu.financials.ending.copy()
            bal_close.link_to(source_bu.financials.ending)
            target_bu = summary_period.bu_directory[self.bu_bbid]
            target_bu.financials.ending = bal_close

            logger.debug('{}:{} -> {}:{} flush {}'.format(
                source.start, source.end,
                summary_period.start, summary_period.end, self.onkey
            ))

            # link starting financials to previous summary
            summary_before = summary_period.past
            if summary_before:
                before_bu = summary_before.bu_directory[self.bu_bbid]
                bal_enter = before_bu.financials.ending.copy()
                bal_enter.link_to(before_bu.financials.ending)
                bal_enter.set_name('starting balance sheet')
                target_bu.financials.starting = bal_enter

            # add formula calculations
            self.derived_calculations()

            # cascade from quarterly to annual
            if self.onkey == self.QUARTERLY_KEY:
                self.onkey = self.ANNUAL_KEY
                self.add(summary_period)
                self.onkey = self.QUARTERLY_KEY

    def add_line_summary(self, source_line, target_line, label=None):
        """


        SummaryMaker.add_line_summary() -> None

        --``source_line`` is the LineItem in a specific time period
        --``target_line`` is the LineItem in the summary statement added to
        --``label`` is the string label to apply to the summary line in Excel

        Method summarizes a LineItem. Aggregation type is defined by
        source_line's attributes.
        """
        summary_type = self.summary_type(target_line)
        if summary_type == 'sum':
            target_line.increment(
                source_line,
                consolidating=True,
                xl_label=label,
                override=True,
                over_time=True
            )
        else:
            if target_line._details:
                for new_line in target_line._details.values():
                    old_line = source_line.find_first(new_line.name)
                    self.add_line_summary(old_line, new_line, label=label)
            else:
                target_line.set_value(
                    source_line.value, "SummaryMaker", override=True
                )
            target_line.xl.reference.source = source_line

    def add_statement_summary(self, source, statement_name):
        """


        SummaryMaker.add_statement_summary() -> None

        --``source`` TimePeriodBase summarized from, monthly or quarterly
        --``statement_name`` is the name of the statement you wish to summarize

        Method adds items from ``statement_name`` in source financials to
        target summary financials.
        """
        if statement_name not in ["overview", "income", "cash"]:
            c = 'Method only works for overview, income, and cash statements'
            raise bb_exceptions.BBAnalyticalError(c)

        # get BUs from time periods
        bu_bbid = self.bu_bbid
        # actual BU whose financials will be aggregated
        source_bu = source.bu_directory[bu_bbid]
        # summary BU
        timeline_summary = self.summaries[self.onkey]
        summary_period = timeline_summary.summary_period
        target_bu = summary_period.bu_directory[bu_bbid]

        source_statement = getattr(source_bu.financials, statement_name)
        target_statement = getattr(target_bu.financials, statement_name)

        # label by ISO end date of the source period
        label = format(source.end)
        for source_line in source_statement.get_ordered():
            target_line = target_statement.find_first(source_line.name)
            if not target_line:
                target_line = source_line.copy()
                target_line.set_hardcoded(False)
                target_line.clear(recur=True, force=True)
                target_statement.add_line(target_line)
            self.add_line_summary(source_line, target_line, label=label)

    def add_content(self, bu_bbid, period, recur=False):
        """


        SummaryMaker.flush() -> None

        Create a BU to use as the summary holder.
        """
        template_bu = self.time_line.current_period.bu_directory[bu_bbid]
        summary_unit = BusinessUnitBase(template_bu.name)

        # intentionally keeping source BU's bbid so we can find it later
        summary_unit.id = copy.deepcopy(template_bu.id)
        summary_unit.complete = False
        summary_unit.period = period
        summary_unit.set_financials(Financials())

        if recur:
            for comp in template_bu.components.get_all():
                unit = self.add_content(comp.id.bbid, period)
                summary_unit.add_component(unit, overwrite=True)

        return summary_unit

    def summarize(self):
        """


        SummaryMaker.flush() -> None

        Add LineItems from the period sent to us into our summary.
        """
        timeline_summary = self.summaries[self.onkey]
        source = timeline_summary.source
        summary_period = timeline_summary.summary_period
        summary_period.month_count += getattr(source, 'month_count', 1)

        logger.debug('{}:{} -> {}:{} add to {} summary {}'.format(
            source.start, source.end,
            summary_period.start, summary_period.end,
            self.onkey, summary_period.month_count
        ))

        for name in ["overview", "income", "cash"]:
            self.add_statement_summary(source, name)

    def wrap(self):
        """


        SummaryMaker.wrap() -> None

        Close out open summaries. Clean up working properties.
        """
        for key in (self.QUARTERLY_KEY, self.ANNUAL_KEY):
            self.onkey = key
            # this is the only crucial line here, it completes ending periods
            self.flush()
            timeline_summary = self.summaries[key]
            timeline_summary.summary_period = None
        self.period_info.clear()
        self.period = None

    # *************************************************************************#
    #                           NON-PUBLIC METHODS                             #
    # *************************************************************************#

    def derived_calculations(self):
        """


        SummaryMaker.derived_calculations() -> None

        On completing a summary period, looks for lines with derived
        calculations in the source and applies their drivers to target
        summary.
        """
        timeline_summary = self.summaries[self.onkey]
        summary_period = timeline_summary.summary_period
        source = timeline_summary.source
        source_bu = source.bu_directory[self.bu_bbid]
        target_bu = summary_period.bu_directory[self.bu_bbid]

        # loop through drivers in real_bu.drivers and copy all
        # "summary_calculate" or "summary_type" == derive
        # drivers to unit_summary.
        for bbid, dr in source_bu.drivers.dr_directory.items():
            summary_type = self.summary_type(dr)
            if summary_type == 'derive':
                target_bu.drivers.add_item(dr.copy())

        # apply derivations to target financials
        summary_fins = target_bu.financials
        for statement in summary_fins.ordered:
            if statement:
                for line in statement.get_full_ordered():
                    summary_type = self.summary_type(line)
                    if summary_type == 'derive':
                        line.clear()
                        target_bu._derive_line(line)

    def summary_type(self, obj):
        """


        SummaryMaker.summary_type() -> str

        --``obj`` has 'summary_type', or 'sum_over_time', or 'summary_calculate'

        Transitional method. Infers summary type from several potential sources.
        Defaults to 'sum'.
        """
        summary_type = getattr(obj, 'summary_type', None)
        if summary_type is None:
            if getattr(obj, 'sum_over_time', False):
                summary_type = 'sum'
        if summary_type is None:
            if getattr(obj, 'summary_calculate', False):
                summary_type = 'derive'
        if summary_type is None:
            summary_type = 'sum'
        return summary_type
