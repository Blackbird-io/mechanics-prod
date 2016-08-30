# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL
# Blackbird Environment
# Module: data_structures.modelling.time_line
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
TimeLine              collection of TimePeriod objects indexed by end date
====================  ==========================================================
"""




# imports
import logging

from datetime import date, datetime, timedelta

import bb_settings

from data_structures.system.bbid import ID
from data_structures.system.summary_maker import SummaryMaker

from .parameters import Parameters
from .time_line_base import TimelineBase
from .time_period import TimePeriod




# globals
logger = logging.getLogger(bb_settings.LOGNAME_MAIN)


# classes
class TimeLine(TimelineBase):
    """

    A TimeLine is a dictionary of TimePeriod objects keyed by ending date.
    The TimeLine helps manage, configure, and search TimePeriods.

    Unless otherwise specified, class expects all dates as datetime.date objects
    and all periods as datetime.timedelta objects.

    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    current_period        P; pointer to the period that represents the present
    id                    instance of PlatformComponents.ID class, for interface
    master                TimePeriod; unit templates that fall outside of time
    parameters            Parameters object, specifies shared parameters
    summary_builder       SummaryBuilder; makes financial summaries

    FUNCTIONS:
    build()               populates instance with adjacent time periods
    clear()               delete content from past and future periods
    clear_future()        delete content from future periods
    extrapolate()         use seed to fill out all future periods in instance
    extrapolate_dates()   use seed to fill out a range of dates
    find_period()         returns period that contains queried time point
    get_segments()        split time line into past, present, and future
    get_ordered()         returns list of periods ordered by end point
    link()                connect adjacent periods
    revert_current()      go back to the prior current period
    update_current()      updates current_period for reference or actual date
    ====================  ======================================================
    """
    DEFAULT_PERIODS_FORWARD = 60
    DEFAULT_PERIODS_BACK = 1

    def __init__(self):
        TimelineBase.__init__(self, interval=1)

        self._current_period = None
        self._old_current_period = None

        self.master = None
        self.parameters = Parameters()
        self.summary_builder = None
        self.has_been_extrapolated = False

    @property
    def current_period(self):
        """


        **property**


        Getter returns instance._current_period. Setter stores old value for
        reversion, then sets new value. Deleter sets value to None.
        """
        return self._current_period

    @current_period.setter
    def current_period(self, value):
        self._old_current_period = self._current_period
        self._current_period = value

    @current_period.deleter
    def current_period(self):
        self.current_period = None

    def __str__(self, lines=None):
        """


        Components.__str__(lines = None) -> str


        Method concatenates each line in ``lines``, adds a new-line character at
        the end, and returns a string ready for printing. If ``lines`` is None,
        method calls pretty_print() on instance.
        """
        if not lines:
            lines = self._make_pretty_strings()
        line_end = "\n"
        result = line_end.join(lines)
        return result

    def build(self,
              ref_date,
              fwd=DEFAULT_PERIODS_FORWARD,
              back=DEFAULT_PERIODS_BACK):
        """


        TimeLine.build() -> None


        Method creates a chain of TimePeriods with adjacent start and end
        points. The chain is ``fwd`` periods long into the future and ``back``
        periods long into the past.

        Method expects ``ref_date`` to be a datetime.date object.

        Method sets instance.current_period to the period covering the reference
        date. Method also sets master to a copy of the current period.
        """
        if not ref_date:
            ref_date = date.today()
        ref_month = ref_date.month
        ref_year = ref_date.year

        current_start_date = date(ref_year, ref_month, 1)

        # Make reference period
        fwd_start_date = self._get_fwd_start_date(ref_date)
        current_end_date = fwd_start_date - timedelta(1)
        current_period = TimePeriod(current_start_date, current_end_date)
        self.add_period(current_period)
        self.current_period = current_period

        # Add master period
        self.master = current_period.copy()

        # Now make the chain
        back_end_date = current_start_date - timedelta(1)
        # Save known starting point for back chain build before fwd changes it.

        # Make fwd chain
        for i in range(fwd):
                #pick up where ref period analysis leaves off
                curr_start_date = fwd_start_date
                fwd_start_date = self._get_fwd_start_date(curr_start_date)
                curr_end_date = fwd_start_date - timedelta(1)
                fwd_period = TimePeriod(curr_start_date, curr_end_date)
                self.add_period(fwd_period)
                #
                #first line picks up last value in function scope, so loop
                #should be closed.

        # Make back chain
        for i in range(back):
                curr_end_date = back_end_date
                curr_start_date = date(curr_end_date.year,
                                       curr_end_date.month,
                                       1)
                back_period = TimePeriod(curr_start_date, curr_end_date)
                self.add_period(back_period)
                #
                #close loop:
                back_end_date = curr_start_date - timedelta(1)

    def clear(self):
        """


        TimeLine.clear() -> None


        Clear content from past and future, preserve current_period.
        """
        past, present, future = self.get_segments()
        to_delete = past + future
        for date in to_delete:
            period = self[date]
            period.clear()
        #<-----------------------------------------------------------------have to dereference history
            # have to do so recursively, to make sure that none of the objects retain their external
            # pointers.

    def clear_future(self, seed=None):
        """


        TimeLine.clear_future() -> None


        Clear content from all periods after seed. Method expects a period as
        ``seed``, will use instance.current_period if seed is None.
        """
        past, present, future = self.get_segments(seed.end)
        for date in future:
            self[date].clear()

    def copy(self):
        """


        TimeLine.copy() -> obj


        Method returns a copy of the instance.
        """
        result = TimelineBase.copy(self)
        result.has_been_extrapolated = self.has_been_extrapolated
        result.summary_builder = self.summary_builder.copy()
        result.summary_builder.time_line = result

        if self.current_period:
            result._current_period = result[self.current_period.end]

        if self._old_current_period:
            result._old_current_period = result[self._old_current_period.end]

        return result

    def extrapolate(self, seed=None):
        """


        TimeLine.extrapolate() -> None


        Extrapolate current period to future dates.  Make quarterly and annual
        financial summaries.  Updates all summaries contained in
        instance.summaries.
        """
        if seed is None:
            seed = self.current_period

        seed.content.reset_financials()
        seed.content.fill_out()

        if seed.past.content:
            seed.past.content.reset_financials()
            seed.past.content.fill_out()

        self.summary_builder = SummaryMaker(self)

        # for the timing of extrapolation
        time_begin = datetime.now()

        for period in self.iter_ordered(open=seed.end):
            if period.end > seed.end:

                # for the timing of this iteration
                time_start = datetime.now()

                # reset content and directories
                period.clear()
                # combine tags
                period.tags = seed.tags.extrapolate_to(period.tags)
                # propagate parameters from past to current
                period.combine_parameters()
                # copy and fill out content
                if seed.content:
                    new_content = seed.content.copy()
                    period.set_content(new_content, updateID=False)
                    period.content.reset_financials()
                    period.content.fill_out()
                seed = period

                # log time spent in this step and total
                time_cease = datetime.now()
                time_stamp = (time_cease - time_start).total_seconds()
                time_total = (time_cease - time_begin).total_seconds()
                logger.debug(
                    '{} -> {} extrapolation {:6.2f} sec, {:6.2f} total'.format(
                    seed.end, period.end, time_stamp, time_total
                ))

            if bb_settings.MAKE_ANNUAL_SUMMARIES:
                if period.end >= self.current_period.end:
                    self.summary_builder.parse_period(period)

            # drop future periods that have been used up to keep size low
            if bb_settings.DYNAMIC_EXTRAPOLATION:
                if period.past and period.past.past:
                    if period.past.past.end > self.current_period.end:
                        period.past.content.reset_financials()
                        period.past.past.clear()

        self.summary_builder.wrap()
        self.has_been_extrapolated = True

    def extrapolate_all(self, seed=None):
        """

        **OBSOLETE**

        Backwards extrapolation is obsolete.
        Legacy interface for TimeLine.extrapolate()
        """
        return self.extrapolate(seed)

    def extrapolate_dates(self, seed, dates, backward=False):
        """


        TimeLine.extrapolate_dates() -> None


        Method extrapolates seed to the first date in dates, then sequentially
        extrapolates remaining dates from each other.

        Method expects ``seed`` to be an instance of TimePeriod. Seed can be
        external to the caller TimeLine.

        Method expects ``dates`` to be a series of endpoints for the periods in
        instance the caller is targeting. In other words, instance must contain
        a period corresponding to each date in ``dates``.

        Dates can contain gaps. Method will always extrapolate from one date to
        its neighbor. Extrapolation works by requesting that each object in a
        content structure extrapolate itself and any of its subordinates.
        For time-sensitive objects like BusinessUnits, that process should
        automatically adjust to the target date regardless of how far away that
        date is from the instance's reference date.

        If ``work_backward`` is True, method will go through dates
        last-one-first.
        """
        #
        if backward:
            dates = reversed(dates)
            # Reverse order, so go from newest to oldest

        for i, date in enumerate(dates):
            # With default arguments, start work at the period immediately
            # after the current period

            target_period = self[date]
            updated_period = seed.extrapolate_to(target_period)
            # extrapolate_to() always does work on an external object and leaves
            # the target untouched. Manually swap the old period for the new
            # period.

            if i == 0:
                updated_period = self._configure_period(updated_period)

                # On i == 0, extrapolating from the original seed. seed can be
                # external (come from a different model), in which case it would
                # use a different model namespace id for unit tracking.
                #
                # Accordingly, when extrapolating from the may-be-external seed,
                # use configure_period() to conform output to current model.
                #
                # Subsequent iterations of the loop will start w periods that are
                # already in the model, so method can leave their namespace id
                # configuration as is.

            self[date] = updated_period
            seed = updated_period

    def find_period(self, query):
        """


        TimeLine.find_period() -> TimePeriod


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
                #query is a string, split it
                q_date = date(*num_query)
        end_date = self._get_ref_end_date(q_date)
        result = self[end_date]
        return result

    def get_segments(self, ref_date=None):
        """


        TimeLine.get_segments() -> list


        Method returns a list of the past, present, and future segments of the
        instance, with respect to the ref_date. If ``ref_date`` is None, method
        counts current period as the present.

        output[0] = list of keys for periods before ref_date
        output[1] = list of ref period (len output[1] == 1)
        output[2] = list of keys for periods after ref_date
        """
        if not ref_date:
            ref_date = self.current_period.end
        ref_end = self._get_ref_end_date(ref_date)
        #
        dates = sorted(self.keys())
        ref_spot = dates.index(ref_end)
        future_dates = dates[(ref_spot + 1 ): ]
        past_dates = dates[:ref_spot]
        result = [past_dates, [ref_end], future_dates]
        return result

    def getOrdered(self):
        """

        **OBSOLETE**

        Legacy interface for TimeLine.get_ordered()
        """
        return self.get_ordered()

    def revert_current(self):
        """


        TimeLine.revert_current() -> None


        Method reverts instance.current_period to preceding value.
        """
        self.current_period = self._old_current_period

    def update_current(self, ref_date=None):
        """


        TimeLine.update_current() -> None


        Method sets instance.current_period to whichever period contains the
        ref_date. If ``ref_date`` == None, method uses current system time.
        """
        if not ref_date:
            ref_date = date.today()
        ref_period = self.find_period(ref_date)
        self.current_period = ref_period

    #*************************************************************************#
    #                          NON-PUBLIC METHODS                             #
    #*************************************************************************#

    def _get_fwd_start_date(self, ref_date):
        """


        TimeLine.get_fwd_start_date() -> datetime.date


        Method returns the starting date of the next month.
        """
        result = None
        ref_day = ref_date.day
        ref_month = ref_date.month
        ref_year = ref_date.year
        if ref_month == 12:
            result = date(ref_year+1,1,1)
        else:
            result = date(ref_year,ref_month+1,1)
        return result

    def _get_ref_end_date(self, ref_date):
        """


        TimeLine._get_ref_end_date() -> datetime.date


        Method returns the last date of the month that contains ref_date.
        """
        result = None
        fwd_start_date = self._get_fwd_start_date(ref_date)
        ref_end_date = fwd_start_date - timedelta(1)
        result = ref_end_date
        return result

    def _make_pretty_strings(self, dates=None, sep="<<", border="-", hook=True):
        """


        TimeLine._make_pretty_strings() -> list


        Method returns a list of strings. Strings are raw: they do NOT end in
        new-line characters.

        When printed in order, the strings illustrate the instance contents for
        each date in ``dates``. Illustration follows the form:


        Row Label       Graphic
        ------------------------------------------------------------------------
        top_pad	        	  __________________
        top_brdr  	---------|------------------|---------------------------
        calendar	PERIOD: <|   2015-06-01    <|   2015-07-01  <<    . . .
        bot_brdr	---------|---------}--------|---------------------------
        hanger		         |         |        |
        bu_line	        	 | +==============+ |
        bu_line		         | |              | |
        bu_line	        	 | |  BU CONTENT  | |
        bu_line		         | |     . . .    | |
        bu_line	        	 | |              | |
        bu_line		         | +==============+ |
        bot_pad	        	 |__________________|
        \n
        """
        clean_lines = []
        #lines is the final, flat list of strings
        #
        if not dates:
            dates = sorted(self.keys())
        cushion = 1
        hook_char = "}"
        lead = "PERIOD:"
        space = " "
        #
        underscore = "_"
        bu_lines = list()
        if self.current_period.content:
            bu_lines = self.current_period.content._get_pretty_lines()
        bu_width = 20
        # default width should be a setting (probably same as bu view)
        if bu_lines:
            bu_width = len(bu_lines[0])
        bu_height = len(bu_lines)
        sep_width = len(sep)
        column_width = bu_width + cushion * 2 + sep_width
        column_count = bb_settings.SCREEN_WIDTH // column_width
##        column_count = 3
        #
        #the first column stays constant from row to row: it's just the lead,
        #plus borders and white space. make all the strings once, then use them
        #for each row.
        #
        c0_width = len(lead) + cushion + sep_width
        #
        top_pad_c0 = space * c0_width
        top_brdr_c0 = border * c0_width
        calendar_c0 = lead + space * cushion + sep
        bot_brdr_c0 = top_brdr_c0[:]
        hanger_c0 = space * c0_width
        bu_line_c0 = space * c0_width
        bot_pad_c0 = top_pad_c0[:]
        c0 = [top_pad_c0,
              top_brdr_c0,
              calendar_c0,
              bot_brdr_c0,
              hanger_c0]
        c0.extend([bu_line_c0 for i in range(bu_height)])
        c0.append(bot_pad_c0)
        #
        #now, build each row. to do so, walk dates in steps of column_count. for
        #each date, build a column (list) of strings. if the column contains the
        #current date, apply ``box`` post-processing to that column. store each
        #column in the columns list for that row. then, when done with all the
        #dates in the row, zip all of the columns together. the zipped object
        #will contain tuples that represent each display line necessary to show
        #that row: ([c0_line0], [c1_line0], ...).
        #
        #to make a flat string suitable for ``lines``, join all of the elements
        #in a tuple, then append that line to lines. do so for all lines in the
        #row (all tuples in the zipped object).
        #
        #finally, when all the hard work is done, add an empty string at the end
        #of the row
        #
        for i in range(0, len(dates), column_count):
            #
            #build a row of c0 plus column_count date-specific columns
            #
            row = []
            row.append(c0)
            row_dates = dates[i : (i + column_count)]
            #
            for end_date in row_dates:
                #
                #build a column for each date
                #
                period = self[end_date]
                post_processing = False
                if end_date == self.current_period.end:
                    post_processing = True
                #
                top_pad = space * column_width
                top_brdr = border * column_width
                calendar = end_date.isoformat().center(column_width - sep_width)
                calendar = calendar + sep
                bot_brdr = top_brdr[:]
                hanger = space * column_width
                col_bu_lines = []
                if period.content:
                    bot_brdr = hook_char.center(column_width, border)
                    hanger = "|".center(column_width)
                    for line in period.content._get_pretty_lines():
                        adj_line = line.center(column_width)
                        col_bu_lines.append(adj_line)
                else:
                    for k in range(bu_height):
                        bu_line_blank = space * column_width
                        col_bu_lines.append(bu_line_blank)
                bot_pad = top_pad[:]
                #
                if post_processing:
                    top_pad = space + underscore * (column_width - 2) + space
                    bot_pad = underscore * column_width
                #
                column = [top_pad,
                          top_brdr,
                          calendar,
                          bot_brdr,
                          hanger]
                column.extend(col_bu_lines)
                column.append(bot_pad)
                #
                if post_processing:
                    for j in range(1, len(column)):
                        line = column[j]
                        column[j] = "|" + line[1:-1] + "|"
                #
                row.append(column)
            #
            #now zip the columns together into clean lines
            zipped_row = zip(*row)
            #zipped_row should be a tuple w len == column_count + 1
            for line_elements in zipped_row:
                flat_line = "".join(line_elements)
                clean_lines.append(flat_line)
            else:
                clean_lines.append("")
                #add a blank line after every row
        #
        return clean_lines
