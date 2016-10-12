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
    parse_period          receive a period from the outside, work on it
    which_quarter         determine which quarter and year a period falls into
    add                   monthly -> quarterly, quarterly -> summary
    flush                 round out a summary
    add_content           build a BU structure
    summarize             summarize statements
    add_statement_summary summarize a statement
    add_line_summary      summarize lines, recursively
    wrap                  finish up the very last summaries, cleanup
    ====================  =====================================================
    """

    ANNUAL_KEY = "annual"
    QUARTERLY_KEY = "quarterly"

    def __init__(self, model):
        self._fiscal_year_end = None
        self.model = model
        self.time_line = model.get_timeline()
        self.buid = model.get_company().id.bbid
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
        self.complete_periods = dict()
        self.period_sources = dict()
        for key, periods in (
            (self.QUARTERLY_KEY, 3),
            (self.ANNUAL_KEY, 12),
        ):
            timeline_summary = TimelineBase(periods)
            timeline_summary.id.set_namespace(self.time_line.id.namespace)
            # TODO: remove when there is a singular bu
            timeline_summary.model = self.model
            # output quarter or year being currently processed
            timeline_summary.summary_period = None
            self.summaries[key] = timeline_summary
            self.complete_periods[key] = periods
            self.period_sources[key] = dict()

    def parse_period(self, period):
        """


        SummaryMaker.fiscal_year_end() -> None

        --``period`` monthly TimePeriod on the original time_line

        Main responder. Passes ``period`` to quarterly and annual summaries.
        """
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
        # month end -> quarter info
        self.period_sources[self.QUARTERLY_KEY][period.end] = {
            'period': (yr_close.year, qt_num),
            'enter': qt_start,
            'close': qt_close,
            'into': qt_into,
        }
        # quarter end -> annual info
        self.period_sources[self.ANNUAL_KEY][qt_close] = {
            'period': yr_close.year,
            'enter': yr_start,
            'close': yr_close,
            'into': yr_into,
        }

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
        target = timeline_summary.summary_period

        # check if we stepped out of the target period, roll over
        if not target or target.end < source.end:
            # close out the summary we have been working on
            self.flush()

            # create next target period
            new_info = self.period_sources[self.onkey][source.end]
            enter = new_info['enter']
            close = new_info['close']
            period = TimePeriodBase(enter, close)
            # counter of months used in the summary
            period.periods_used = 0
            # what sort of timeline does the period belong to
            period.summary = self.onkey

            # copy BU structure from time_line.current_period
            summary_unit = self.add_content(period)

            # add to timeline
            period.set_content(summary_unit)
            timeline_summary.add_period(period)
            timeline_summary.summary_period = period

            # special handling of the first time period starting balance:
            # link to the starting balance of the first source period
            if len(timeline_summary) == 1:
                source_fins = self.model.get_financials(self.buid, source)
                period_fins = self.model.get_financials(self.buid, period)
                bal_enter = source_fins.starting.copy()
                bal_enter.link_to(source_fins.starting)
                period_fins.starting = bal_enter

            logger.debug('{}:{} -> {}:{} new {}'.format(
                source.start, source.end, period.start, period.end, self.onkey
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
            source_fins = self.model.get_financials(self.buid, source)
            bal_close = source_fins.ending.copy()
            bal_close.link_to(source_fins.ending)
            target_bu = summary_period.bu_directory[self.buid]
            target_bu.financials.ending = bal_close

            logger.debug('{}:{} -> {}:{} flush {}'.format(
                source.start, source.end,
                summary_period.start, summary_period.end, self.onkey
            ))

            # link starting financials to previous summary
            summary_before = summary_period.past
            if summary_before:
                before_bu = summary_before.bu_directory[self.buid]
                # bal_enter = before_bu.financials.ending.copy()
                # bal_enter.reset()
                # bal_enter.link_to(before_bu.financials.ending)
                # bal_enter.set_name('starting balance sheet')
                # target_bu.financials.starting = bal_enter
                target_bu.financials.starting = before_bu.financials.ending

            # add formula calculations
            self.derived_calculations()

            # add period count
            fins = target_bu.financials
            fins.periods_used = summary_period.periods_used
            full = (fins.periods_used == self.complete_periods[self.onkey])
            fins.complete = full

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
        summary_type = target_line.summary_type
        if target_line._details:
            for new_line in target_line._details.values():
                old_line = source_line.find_first(new_line.name)
                self.add_line_summary(old_line, new_line, label=label)
        elif summary_type in ('derive', 'skip'):
            # driver will do the work if 'derive'
            pass
        elif summary_type in ('sum', 'average'):
            target_line.increment(
                source_line,
                consolidating=True,
                xl_label=label,
                override=True,
                over_time=True
            )
        elif summary_type == 'first':
            # use the first non-None showing up
            if target_line.value is None:
                target_line.set_value(
                    source_line.value, "SummaryMaker", override=False
                )
                target_line.xl.reference.source = source_line
        elif summary_type == 'last':
            # assume period show up in order, last one overrides
            target_line.set_value(
                source_line.value, "SummaryMaker", override=True
            )
            target_line.xl.reference.source = source_line
        elif summary_type:
            c = 'we have not yet implemented summary_type: {}'.format(
                summary_type
            )
            raise bb_exceptions.BBAnalyticalError(c)
        else:
            # this is equivalent to 'last'
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
        source_fins = self.model.get_financials(self.buid, source)

        # summary BU
        timeline_summary = self.summaries[self.onkey]
        target = timeline_summary.summary_period
        target_fins = self.model.get_financials(self.buid, target)

        source_statement = getattr(source_fins, statement_name, None)
        target_statement = getattr(target_fins, statement_name, None)
        if not source_statement:
            return
        if not target_statement:
            target_fins.add_statement(statement_name)
            target_statement = getattr(target_fins, statement_name)

        # label by ISO end date of the source period
        label = format(source.end)
        for source_line in source_statement.get_ordered():
            if source_line.summary_type == 'skip':
                continue
            target_line = target_statement.find_first(source_line.name)
            if not target_line:
                target_line = source_line.copy()
                target_line.set_hardcoded(False)
                target_line.clear(recur=True, force=True)
                target_statement.add_line(target_line)
            self.add_line_summary(source_line, target_line, label=label)

    def add_content(self, period, recur=False):
        """


        SummaryMaker.add_content() -> None

        Create a BU to use as the summary holder.
        """
        template_bu = self.time_line.current_period.bu_directory[self.buid]
        summary_unit = BusinessUnitBase(template_bu.tags.title)

        # intentionally keeping source BU's bbid so we can find it later
        summary_unit.id = copy.deepcopy(template_bu.id)
        summary_unit.period = period
        summary_unit.periods_used = 0
        summary_unit.summary_level = self.onkey
        summary_unit.set_financials(
            Financials(parent=summary_unit, period=period)
        )

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
        summary_period.periods_used += getattr(source, 'periods_used', 1)

        logger.debug('{}:{} -> {}:{} add to {} summary {}'.format(
            source.start, source.end,
            summary_period.start, summary_period.end,
            self.onkey, summary_period.periods_used
        ))

        for name in ["overview", "income", "cash", "ownership"]:
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
            timeline_summary.source = None
        self.period_sources = None
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
        target = timeline_summary.summary_period
        bu = self.model.get_company()

        # apply derivations to target financials
        target_fins = self.model.get_financials(self.buid, target)
        for statement in target_fins.ordered:
            if statement:
                for line in statement.get_full_ordered():
                    if line.summary_type == 'derive':
                        line.clear()
                        bu._derive_line(line, period=target)
