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
import copy

from datetime import date, datetime, timedelta

import bb_settings
import tools.for_printing as views

from data_structures.system.bbid import ID
from tools.parsing import date_from_iso
from .parameters import Parameters
from .time_period import TimePeriod




# globals
logger = logging.getLogger(bb_settings.LOGNAME_MAIN)


# classes
class TimeLine(dict):
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
    name                  str; corresponds with Model.time_line key
    parameters            Parameters object, specifies shared parameters
    ref_date              datetime.date; reference date for the model
    resolution            string; 'monthly', 'annual'..etc. Model.time_line key

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

    def __init__(self, model, resolution='monthly', name='default', interval=1):
        dict.__init__(self)
        self.id = ID()
        # Timeline objects support the id interface and pass the model's id
        # down to time periods. The Timeline instance itself does not get
        # its own bbid.

        self.model = model
        self.resolution = resolution
        self.name = name
        self.interval = interval
        self.master = None
        self.parameters = Parameters()
        self.has_been_extrapolated = False
        self.ref_date = None

        self.id.set_namespace(model.id.bbid)

    @property
    def current_period(self):
        """


        **property**


        Getter returns instance._current_period. Setter stores old value for
        reversion, then sets new value. Deleter sets value to None.
        """
        if len(self):
            cp = self.find_period(self.model.ref_date)
            return cp

    def __str__(self, lines=None):
        """


        Components.__str__(lines = None) -> str


        Method concatenates each line in ``lines``, adds a new-line character at
        the end, and returns a string ready for printing. If ``lines`` is None,
        method calls pretty_print() on instance.
        """
        if not lines:
            lines = views.view_as_time_line(self)
        line_end = "\n"
        result = line_end.join(lines)
        return result

    @classmethod
    def from_portal(cls, portal_data, model):
        """

        TimeLine.from_portal(portal_data) -> TimeLine

        **CLASS METHOD**

        Method extracts a TimeLine from portal_data.
        """
        key = tuple(portal_data[k] for k in ('resolution', 'name'))
        new = cls(
            model,
            resolution=portal_data['resolution'],
            name=portal_data['name'],
        )
        if portal_data['interval'] is not None:
            new.interval = portal_data['interval']
        if portal_data['ref_date']:
            new.ref_date = date_from_iso(portal_data['ref_date'])
        if portal_data['has_been_extrapolated'] is not None:
            new.has_been_extrapolated = portal_data['has_been_extrapolated']
        if portal_data['parameters'] is not None:
            new.parameters = Parameters.from_portal(portal_data['parameters'])

        obj = model.timelines[key]
        new.master = obj.master

        for data in portal_data['periods']:
            period = TimePeriod.from_portal(data)
            new.add_period(obj[period.end])

        return new

    def to_portal(self):
        """

        TimeLine.to_portal() -> dict

        Method yields a serialized representation of self.
        """
        periods = [
            period.to_portal() for period in self.values()
        ]
        result = {
            'periods': periods,
            'interval': self.interval,
            'ref_date': format(self.ref_date) if self.ref_date else None,
            'has_been_extrapolated': self.has_been_extrapolated,
            'parameters': list(self.parameters.to_portal()),
        }
        return result

    def copy_structure(self):
        """


        TimeLine.copy_structure() -> TimeLine

        Method returns a copy of self linked to parent model and with the same
        layout.
        """
        result = type(self)(self.model)
        result.ref_date = copy.copy(self.ref_date)
        result.parameters = self.parameters.copy()
        for old_period in self.iter_ordered():
            new_period = old_period.copy(clean=True)
            result.add_period(new_period)

        if self.master:
            result.master = result[self.master.end]

        return result

    def build(
        self, ref_date=None,
        fwd=DEFAULT_PERIODS_FORWARD, back=DEFAULT_PERIODS_BACK, year_end=True,
    ):
        """


        TimeLine.build() -> None


        Method creates a chain of TimePeriods with adjacent start and end
        points. The chain is at least ``fwd`` periods long into the future
        and ``back`` periods long into the past. Forward chain ends on a Dec.

        Method expects ``ref_date`` to be a datetime.date object.

        Method sets instance.current_period to the period covering the reference
        date. Method also sets master to a copy of the current period.
        """
        if not ref_date:
            ref_date = self.model.ref_date
        self.ref_date = ref_date

        ref_month = ref_date.month
        ref_year = ref_date.year

        current_start_date = date(ref_year, ref_month, 1)

        # Make reference period
        fwd_start_date = self._get_fwd_start_date(ref_date)
        current_end_date = fwd_start_date - timedelta(1)
        current_period = TimePeriod(
            current_start_date, current_end_date, model=self.model
        )
        self.add_period(current_period)

        # Add master period
        self.master = self.model.taxo_dir

        # Now make the chain
        back_end_date = current_start_date - timedelta(1)
        # Save known starting point for back chain build before fwd changes it.

        # Make fwd chain
        i = 0
        while True:
            # pick up where ref period analysis leaves off
            curr_start_date = fwd_start_date
            fwd_start_date = self._get_fwd_start_date(curr_start_date)
            curr_end_date = fwd_start_date - timedelta(1)
            fwd_period = TimePeriod(
                curr_start_date, curr_end_date, model=self.model
            )
            self.add_period(fwd_period)
            i += 1
            if i >= fwd and (not year_end or fwd_period.end.month == 12):
                break
            # first line picks up last value in function scope, so loop
            # should be closed.

        # Make back chain
        for i in range(back):
            curr_end_date = back_end_date
            curr_start_date = date(
                curr_end_date.year, curr_end_date.month, 1
            )
            back_period = TimePeriod(
                curr_start_date, curr_end_date, model=self.model
            )
            self.add_period(back_period)
            # close loop:
            back_end_date = curr_start_date - timedelta(1)

    def clear(self):
        """


        TimeLine.clear() -> None


        Clear content from past and future, preserve current_period.
        """
        for period in self.iter_ordered():
            if period.end != self.current_period.end:
                period.clear()
        # have to dereference history
        # have to do so recursively, to make sure that none of the objects
        # retain their external pointers.

    def clear_future(self, seed=None):
        """


        TimeLine.clear_future() -> None


        Clear content from all periods after seed. Method expects a period as
        ``seed``, will use instance.current_period if seed is None.
        """
        if seed is None:
            seed = self.current_period
        for period in self.iter_ordered():
            if period.end > seed.end:
                period.clear()

    def copy(self):
        """


        TimeLine.copy() -> TimeLine


        Method returns a copy of the instance.
        """
        result = copy.copy(self)
        for key, value in self.items():
            result[key] = value.copy()
            result[key].relationships.set_parent(result)
        result.has_been_extrapolated = self.has_been_extrapolated
        return result

    def add_period(self, period):
        """


        Timeline.add_period() -> None

        --``period`` is a TimePeriod object

        Method configures period and records it in the instance under the
        period's end_date.
        """
        period = self._configure_period(period)
        self[period.end] = period

    def iter_ordered(self, open=None, exit=None, shut=None):
        """


        Timeline.iter_ordered() -> iter

        --``open`` date, soft start, if falls in period, iteration starts
        --``exit`` date, soft stop, if falls in period, last shown
        --``shut`` date, hard stop, if not exact period end, iteration stops

        Method iterates over periods in order, starting with the one in which
        ``open`` falls, and ending with the one including ``exit`` and
        not following ``shut``.
        """
        for end_date, period in sorted(self.items()):
            if open and open > period.end:
                continue
            if exit and exit < period.start:
                break
            if shut and shut < period.end:
                break
            yield period

    def get_ordered(self):
        """


        Timeline.get_ordered() -> list


        Method returns list of periods in instance, ordered from earliest to
        latest endpoint.
        """
        return list(self.iter_ordered())

    def extrapolate(self, seed=None, calc_summaries=True):
        """


        TimeLine.extrapolate() -> None


        Extrapolate current period to future dates.  Make quarterly and annual
        financial summaries.  Updates all summaries contained in
        instance.summaries.
        """
        if seed is None:
            seed = self.current_period

        company = self.model.get_company()
        company.reset_financials(period=seed)
        company.fill_out(period=seed)

        summary_maker = self.model.prep_summaries()

        for period in self.iter_ordered(open=seed.end):
            if period.end > seed.end:
                logger.info(period.end)
                # reset content and directories
                period.clear()
                # combine tags
                period.tags = seed.tags.extrapolate_to(period.tags)
                # propagate parameters from past to current
                period.combine_parameters()
                # copy and fill out content
                company.reset_financials(period=period)
                company.fill_out(period=period)

            if bb_settings.MAKE_ANNUAL_SUMMARIES and calc_summaries:
                if period.end >= self.current_period.end:
                    summary_maker.parse_period(period)

            # drop future periods that have been used up to keep size low
            if bb_settings.DYNAMIC_EXTRAPOLATION:
                if period.past and period.past.past:
                    if period.past.past.end > self.current_period.end:
                        period.past.past.financials.clear()

        if bb_settings.MAKE_ANNUAL_SUMMARIES and calc_summaries:
            summary_maker.wrap()

        # import devhooks
        # devhooks.picksize(self)
        self.has_been_extrapolated = True

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
            dates = dates[::-1]
            # Reverse order, so go from newest to oldest

        for i in range(len(dates)):

            date = dates[i]
            # With default arguments, start work at the period immediately
            # prior to the current period

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

    def extrapolate_statement(self, statement_name, seed=None):
        """


        TimeLine.extrapolate_statement() -> None


        Extrapolates a single statement forward in time. DOES NOT MAKE
        SUMMARIES.
        """
        if seed is None:
            seed = self.current_period

        company = self.model.get_company()
        orig_fins = company.get_financials(period=seed)
        orig_statement = getattr(orig_fins, statement_name)
        orig_statement.reset()
        company.compute(statement_name, period=seed)

        for period in self.iter_ordered(open=seed.end):
            if period.end > seed.end:
                new_fins = company.get_financials(period=period)
                new_stat = getattr(new_fins, statement_name, None)
                if new_stat is None:
                    # need to add statement
                    new_stat = orig_statement.copy(clean=True)
                    new_fins.add_statement(statement_name, statement=new_stat)
                    company.compute(statement_name, period=period)
                else:
                    # compute what is already there
                    company.compute(statement_name, period=period)

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
                # query is a string, split it
                q_date = date(*num_query)
        end_date = self._get_ref_end_date(q_date)
        result = self.get(end_date)
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
        future_dates = dates[(ref_spot + 1):]
        past_dates = dates[:ref_spot]
        result = [past_dates, [ref_end], future_dates]
        return result

    # *************************************************************************#
    #                           NON-PUBLIC METHODS                             #
    # *************************************************************************#

    def _get_fwd_start_date(self, ref_date):
        """


        TimeLine.get_fwd_start_date() -> datetime.date


        Method returns the starting date of the next month.
        """
        ref_month = ref_date.month
        ref_year = ref_date.year
        if ref_month == 12:
            result = date(ref_year + 1, 1, 1)
        else:
            result = date(ref_year, ref_month + 1, 1)
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

    def _configure_period(self, period):
        """


        Timeline._configure_period() -> period


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
