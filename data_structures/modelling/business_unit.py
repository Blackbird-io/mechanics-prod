# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL

# Blackbird Environment
# Module: data_structures.modelling.business_unit
"""

Module defines BusinessUnit class.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
BusinessUnit          structured snapshot of a business at a given point in time
ParameterManager      manager class for unit parameters over time
====================  ==========================================================
"""




# Imports
import copy

import bb_exceptions

from data_structures.guidance.guide import Guide
from data_structures.guidance.interview_tracker import InterviewTracker
from data_structures.modelling.statement import Statement
from data_structures.valuation.business_summary import BusinessSummary
from data_structures.valuation.company_value import CompanyValue

from . import common_events

from .business_unit_base import BusinessUnitBase
from .components import Components
from .equalities import Equalities
from .history_line import HistoryLine
from .life import Life as LifeCycle
from .parameters import Parameters




# Constants
# n/a

# Globals
# n/a

# Classes
class BusinessUnit(BusinessUnitBase, Equalities):
    """

    Object describes a group of business activity. A business unit can be a
    store, a region, a product, a team, a relationship (or many relationships),
    etcetera.
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    components            instance of Components class, stores business units
    drivers               dict; tag/line name : set of driver bbids
    filled                bool; True if fill_out() has run to completion
    financials            instance of Financials object
    guide                 instance of Guide object
    id                    instance of ID object
    interview             instance of InterviewTracker object
    life                  instance of Life object
    location              placeholder for location functionality
    parameters            flexible storage for data that shapes unit performance
    relationships         instance of Relationships class
    size                  int; number of real-life equivalents obj represents
    stage                 property; returns non-public stage or interview
    summary               None or BusinessSummary; investment summary
    type                  str or None; unit's in-model type (e.g., "team")
    used                  set; contains BBIDs of used Topics
    valuation             None or CompanyValue; market view on unit

    FUNCTIONS:
    add_component()       adds unit to instance components
    add_driver()          registers a driver
    archive_path()        archives existing path then sets to blank Statement
    archive_used()        archives existing used topics and sets to blank set
    compute()             consolidates and derives a statement for all units
    fill_out()            runs calculations to fill out financial statements
    kill()                make dead, optionally recursive
    make_past()           put a younger version of unit in prior period
    recalculate()         reset financials, compute again, repeat for future
    reset_financials()    resets instance and (optionally) component financials
    set_analytics()       attaches an object to instance.analytics
    set_financials()      attaches a Financials object from the right template
    set_history()         connect instance to older snapshot, optionally recur
    synchronize()         set components to same life, optionally recursive
    ====================  ======================================================
    """

    irrelevantAttributes = ["all",
                            "filled",
                            "guide",
                            "id",
                            "parent",
                            "part_of"]

    _UPDATE_BALANCE_SIGNATURE = "Update balance"

    def __init__(self, name, fins=None, model=None):
        BusinessUnitBase.__init__(self, name, fins=fins, model=model)

        self._type = None

        self.components = None
        self._set_components()

        self.filled = False

        self.guide = Guide()
        self.interview = InterviewTracker()
        self._stage = None
        self.used = set()

        self.life = LifeCycle()
        self.location = None

        self.size = 1
        self.summary = BusinessSummary()
        self.valuation = CompanyValue()

        # attrs from BusinessUnitBase
        self.complete = True
        self.periods_used = 1

        self._parameters = Parameters()

        # for monitoring, temporary storage for existing path and used sets
        self._path_archive = list()
        self._used_archive = list()

    @property
    def parameters(self):
        params = self._parameters

        try:
            period_params = self.period.unit_parameters[self.id.bbid]
        except AttributeError:
            pass
        except KeyError:
            pass
        else:
            params.update(period_params)

        return params

    @property
    def stage(self):
        """


        **property**


        When instance._stage points to a True object, property returns the
        object. Otherwise property returns model.interview.

        Since the default value for instance._path is None, property starts out
        with a ``pass-through``, backwards-compatible value.

        Setter sets _stage to value.

        Deleter sets _stage to None to restore default pass-through state.
        """
        result = self._stage
        if not result:
            result = self.interview

        return result

    @stage.setter
    def stage(self, value):
        self._stage = value

    @stage.deleter
    def stage(self):
        self._stage = None

    @property
    def type(self):
        """


        **property**


        Getter returns instance._type.

        Setter registers instance bbid under the new value key and removes old
        registration (when instance.period is defined).

        Deletion prohibited.
        """
        return self._type

    @type.setter
    def type(self, value):
        #
        old_type = self.type
        self._type = value
        #
        if self.period and old_type:
            old_entry = self.period.ty_directory.get(old_type)
            old_entry.remove(self.id.bbid)

            new_entry = self.period.ty_directory.setdefault(value, set())
            new_entry.add(self.id.bbid)
            # Entries are sets of bbids for units that belong to that type

    @type.deleter
    def type(self):
        c = "``type`` is a property; delete prohibited. to represent generic "
        c += "unit, set to None instead."
        raise bb_exceptions.ManagedAttributeError(c)

    def __hash__(self):
        return self.id.__hash__()

    def add_component(
            self, bu, update_id=True, register_in_period=True, overwrite=False
    ):
        """


        BusinessUnit.add_component() -> None


        Method prepares a bu and adds it to instance components.

        Method always sets bu namespace_id to instance's own namespace_id. If
        ``updateID`` is True, method then assigns a new bbid to the instance.

        Method raises IDNamespaceError if the bu's bbid falls outside the
        instance's namespace id. This is most likely if updateID is False and
        the bu retains an old bbid from a different namespace (e.g., when
        someone inserts a business unit from one model into another without
        updating the business unit's bbid).

        If register_in_period is true, method raises IDCollisionError if the
        period's directory already contains the new business unit's bbid.

        If all id verification steps go smoothly, method delegates insertion
        down to Components.add_item().

        Usage Scenarios:

        Adding a newly created ChildBU:
            ParentBU.add_component(ChildBU, True, True)
        Transferring a ChildBU from one parent to another:
            ParentBU2.add_component(ChildBU, False, False)
        Transferring a ChildBU to a ParentBU in a different period
            ParentBU3.add_component(ChildBU, False, True)

        """
        bu.summary = None
        bu.valuation = None

        # optionally update ids.
        if update_id:
            bu._update_id(namespace=self.id.bbid, recur=True)

        # register to model
        model = self.relationships.model
        model.register(bu, update_id=False, overwrite=overwrite, recur=True)

        self.components.add_item(bu)

    def addDriver(self, newDriver, *otherKeys):
        """

        **OBSOLETE**

        Legacy interface for add_driver().
        """
        return self.add_driver(newDriver, *otherKeys)

    def add_driver(self, newDriver, *otherKeys):
        """


        BusinessUnit.add_driver() -> None


        Method registers a driver to names and tags of lines it supports.
        Method delegates all work to DrContainer.addItem().
        """
        newDriver.validate(parent=self)
        # Validation call will throw DefinitionError if driver does not have
        # sufficient data to run in this instance at the time of insertion.

        # Topics may inject drivers into business units at time A with the
        # intent that these drivers work only at some future time B (when their
        # work conditions or other logic has been satisfied). Time B may be
        # arbitrarily far away in the future. This method looks to avoid
        # confusing future errors by making sure that the Topic author is aware
        # of the required formula parameters at the time the Topic runs.

        self.drivers.add_item(newDriver, *otherKeys)

    def archive_path(self):
        """


        BusinessUnit.archive_path() -> None


        Method archives existing path to BusinessUnit._path_archive and sets
         the path to a clean Statement().  Method is used by monitoring to
         pre-process before setting the monitoring path.
        """
        if self.stage.path is not None:
            self._path_archive.append(self.stage.path)

        new_path = Statement()
        self.stage.set_path(new_path)

    def archive_used(self):
        """


        BusinessUnit.archive_used() -> None


        Method archives existing set of used topics to
        BusinessUnit._used_archive and sets used to a new empty set. Method is
        used by monitoring to pre-process before setting the monitoring path.
        """
        self._used_archive.append(self.used)
        self.used = set()

    def compute(self, statement_name, period=None):
        """


        BusinessUnit.compute() -> None

        --``statement`` name of statement to operate on

        Method recursively runs consolidation and derivation logic on
        statements for instance and components.
        """
        if not period:
            period = self.relationships.model.get_timeline().current_period

        for unit in self.components.get_all():
            unit.compute(statement_name, period=period)

        self._consolidate(statement_name, period)
        self._derive(statement_name, period)

    def copy(self):
        """


        BU.copy() -> BU


        Method returns a new business unit that is a deep-ish copy of the
        instance.

        The new bu starts out as a shallow Tags.copy() copy of the instance.
        The method then sets the following attributes on the new bu to either
        deep or class-specific copies of the instance values:

        - components
        - drivers
        - financials
        - header.profile
        - id (vanilla shallow copy)
        - life

        The class-specific copy methods for components, drivers, and financials
        all return deep copies of the object and its contents. See their
        respective class documenation for mode detail.
        """
        result = BusinessUnitBase.copy(self)

        result.guide = copy.deepcopy(self.guide)
        # Have to make a deep copy of guide because it is composed of Counter
        # objects. Guide shouldn't point to a business unit or model
        result.life = self.life.copy()
        result.summary = BusinessSummary()
        result.valuation = CompanyValue()
        result._parameters = self._parameters.copy()

        result._stage = None
        result.used = set()

        r_interview = self.interview.copy()
        result.interview = r_interview

        return result

    def fill_out(self, period=None):
        """


        BusinessUnit.fill_out() -> None


        Method is the driver for filling out instance financials.

        Will no-op if instance.filled is True. Otherwise, will consolidate and
        derive overview, income, and cash statements for the instance and its
        components. Then, will process balance sheets.  At conclusion, method
        sets instance.filled to True to make sure that subsequent calls do not
        increment existing values.

        NOTE: consolidate() blocks derive() on the same lineitem.

        Once a non-None value is written into a Lineitem at one component,
        BusinessUnit.derive() will never run again for that LineItem, either at
        that component or any parent or ancestor of that component.
        """
        financials = self.get_financials(period)
        if not financials.filled:
            if not period:
                period = self.relationships.model.get_timeline().current_period
            self._load_starting_balance(period)

            for statement in financials.compute_order:
                self.compute(statement, period)

            self._compute_ending_balance(period)

            self._check_start_balance(period)

            self.filled = True
            financials.filled = True

    def kill(self, date=None, recur=True):
        """


        BusinessUnit.kill() -> None


        Enters a death event on the specified date. Also enters a ``killed``
        event.

        If ``date`` is None, uses own ref_date. If ``recur`` is True, repeats
        for all components.
        """
        if date is None:
            date = self.life.ref_date
        self.life.events[self.life.KEY_DEATH] = date
        self.life.events[common_events.KEY_KILLED] = date
        if recur:
            for unit in self.components.values():
                unit.kill(date, recur)

    def make_past(self, overwrite=False):
        """


        BusinessUnit.make_past() -> None


        --``overwrite``: if True, will replace existing instance.past

        Create a past for instance.

        Routine operates by making an instance copy, fitting the copy to the
        n-1 period (located at instance.period.past), and then recursively
        linking all of the instance components to their younger selves.
        """
        model = self.relationships.model
        period = model.get_timeline().current_period

        self.get_financials(period.past)

        for bu in self.components.get_all():
            bu.make_past()

    def recalculate(self, adjust_future=True, period=None):
        """


        BusinessUnit.recalculate () -> None


        Recalculate instance finanicals. If ``adjust_future`` is True, will
        repeat for all future snapshots.
        """
        self.reset_financials(period=period)
        self.fill_out(period=period)
        if adjust_future and period and period.future:
            self.recalculate(adjust_future=True, period=period.future)

    def reset_financials(self, period=None, recur=True):
        """


        BusinessUnit.reset_financials() -> None


        Method resets financials for instance and, if ``recur`` is True, for
        each of the components. Method sets instance.filled to False.
        """
        self.filled = False
        financials = self.get_financials(period)
        financials.reset()
        if recur:
            pool = self.components.get_all()

            for bu in pool:
                bu.reset_financials(period=period, recur=recur)

    def set_analytics(self, atx):
        """


        BusinessUnit.set_analytics() -> None


        Method sets instance.analytics to passed-in argument, sets analytics
        object to point to instance as its parent.
        """
        atx.relationships.set_parent(self)
        self.valuation = atx

    def set_history(self, history, clear_future=True, recur=True):
        """


        BusinessUnit.set_history() -> None


        Set history for instance; repeat for components (by bbid) if recur is
        True.
        """
        HistoryLine.set_history(self, history, clear_future=clear_future)

        # Use dedicated logic to handle recursion.
        if recur:
            for bbid, unit in self.components.items():
                mini_history = history.components[bbid]
                unit.set_history(mini_history)

        self.reset_financials(recur=False)
        # Reset financials here because we just connected a new starting
        # balance sheet.

    def synchronize(self, recur=True):
        """


        BusinessUnit.synchronize() -> None


        Set life on all components to copy of caller. If ``recur`` is True,
        repeat all the way down.
        """
        for unit in self.components.values():
            unit.life = self.life.copy()
            if recur:
                unit.synchronize()

    def peer_locator(self):
        """


        BusinessUnit.peer_locator() -> BusinessUnit

        Given a parent container from another time period, return a function
        locating a copy of ourselves within that container.
        """

        def locator(time_period, create=True, **kargs):
            if self.id.bbid not in time_period.bu_directory:
                if create and time_period.end == self.period.past_end:
                    self.make_past()
            peer = time_period.bu_directory.get(self.id.bbid)
            return peer
        return locator

    def get_parameters(self, period=None):
        """


        BusinessUnitBase.get_financials() -> Financials()

        --``period`` TimePeriod

        Method combines all parameters from reachable sources in order
        of precedence. Driver updates the results with own parameters.
        """
        if not period:
            period = self.period
        time_line = period.relationships.parent

        # Specific parameters trump general ones. Start with time_line, then
        # update for period (more specific). Driver trumps with own parameters.
        params = dict()
        if hasattr(time_line, 'parameters'):
            params.update(time_line.parameters)
        if hasattr(period, 'parameters'):
            params.update(period.parameters)
        params.update(self._parameters)
        if hasattr(period, 'unit_parameters'):
            params.update(period.unit_parameters.get(self.id.bbid, {}))

        return params

    # *************************************************************************#
    #                           NON-PUBLIC METHODS                             #
    # *************************************************************************#

    def _build_directory(self, recur=True, overwrite=True):
        """


        BusinessUnit._build_directory() -> (id_directory, ty_directory)


        Register yourself and optionally your components, by type and by id
        return id_directory, ty_directory
        """

        # return a dict of bbid:unit
        id_directory = dict()
        ty_directory = dict()
        if recur:
            for unit in self.components.values():
                lower_level = unit._build_directory(
                    recur=True, overwrite=overwrite
                )
                lower_ids = lower_level[0]
                lower_ty = lower_level[1]
                id_directory.update(lower_ids)
                ty_directory.update(lower_ty)

            # update the directory for each unit in self
        if self.id.bbid in id_directory:
            if not overwrite:
                c = "Can not overwrite existing bbid"
                raise bb_exceptions.BBAnalyticalError(c)

        id_directory[self.id.bbid] = self
        this_type = ty_directory.setdefault(self.type, set())
        this_type.add(self.id.bbid)

        return id_directory, ty_directory

    def _check_start_balance(self, period):
        """


        BusinessUnit._check_start_balance() -> None

        Compares starting and ending balances. Adds missing lines to starting
        balance to keep layout consistent.
        """

        pool = self.components.get_all()
        for unit in pool:
            unit._check_start_balance(period)

        financials = self.get_financials(period)
        for end_line in financials.ending.get_ordered():
            start_line = financials.starting.find_first(end_line.name)
            if start_line:
                self._check_line(start_line, end_line)
            else:
                new_line = end_line.copy()
                new_line.clear(force=True)
                financials.starting.add_line(
                    new_line, position=end_line.position
                )

    def _check_line(self, start_line, end_line):
        """


        BusinessUnit._check_line() -> None

        Compares starting and ending balances. Adds missing lines to starting
        balance to keep layout consistent.
        """

        if end_line._details:
            for end in end_line.get_ordered():
                start = start_line.find_first(end.name)
                if start:
                    self._check_line(start, end)
                else:
                    new_line = end.copy()
                    new_line.clear(force=True)
                    start_line.add_line(new_line, position=end.position)

    def _compute_ending_balance(self, period):
        """


        BusinessUnit._compute_ending_balance() -> None


        Method recursively fills out balance sheets for instance and components.
        Method adjusts shape of ending and starting balance sheets, runs
        consolidation logic, updates balance sheets, then runs derivation logic.
        """

        for unit in self.components.get_all():
            unit._compute_ending_balance(period)

        financials = self.get_financials(period)
        ending_balance = financials.ending
        starting_balance = financials.starting

        ending_balance.increment(
            starting_balance, consolidating=False, over_time=True
        )
        ending_balance.reset()
        # Our goal is to pick up shape, so clear values.

        # By default, the ending balance sheet should look the same as the
        # starting one. Here, we copy the starting structure and zero out
        # the values. We will fill in the values later through
        # consolidate(), update_balance(), and derive().

        self._consolidate("ending", period)

        self._update_balance(period)
        # Sets ending balance lines to starting values by default

        self._derive("ending", period)
        # Derive() will overwrite ending balance sheet where appropriate

    def _consolidate(self, statement_name, period=None):
        """


        BusinessUnit.consolidate() -> None


        Method iterates through instance components in order and consolidates
        each living component into instance using BU.consolidate_unit()
        """
        pool = self.components.get_all()
        # Need stable order to make sure we pick up peer lines from units in
        # the same order. Otherwise, their order might switch and financials
        # would look different (even though the bottom line would be the same).

        for unit in pool:
            self._consolidate_unit(unit, statement_name, period)

    def _consolidate_unit(self, sub, statement_name, period=None):
        """


        BusinessUnit.consolidate_unit() -> None


        -- ``sub`` should be a BusinessUnit object
        --``statement_name`` is the name of the financial statement to work on

        Method consolidates value of line items from sub's statement to
        same statement in instance financials.  Usually sub is a
        constituent/component of the instance, but this is not mandatory.

        Method delegates to Statement.increment() for actual consolidation work.
        """
        # Step Only: Actual consolidation
        sub_fins = sub.get_financials(period)
        top_fins = self.get_financials(period)
        sub_statement = getattr(sub_fins, statement_name, None)
        top_statement = getattr(top_fins, statement_name, None)

        if sub.life.conceived(period):
            xl_only = False
        else:
            xl_only = True

        if sub_statement and top_statement:
            top_statement.increment(
                sub_statement,
                consolidating=True,
                xl_only=xl_only,
                xl_label=sub.title,
            )

    def _derive(self, statement_name, period=None):
        """


        BusinessUnit.derive() -> None

        --``statement_name`` is the name of the financial statement to work on

        Method walks through lines in statement and delegates to
        BusinessUnit._derive_line() for all substantive derivation work.
        """
        financials = self.get_financials(period)
        this_statement = getattr(financials, statement_name, None)

        if this_statement:
            for line in this_statement.get_ordered():
                self._derive_line(line, period)

    def _fit_to_period(self, time_period, recur=True):
        """


        BusinessUnit._fit_to_period() -> None


        Set pointer to timeperiod and synchronize ref date to period end date.
        If ``recur`` == True, repeat for all components.
        """
        self.period = time_period
        self.life.set_ref_date(time_period.end)

        if recur:
            for unit in self.components.values():
                unit._fit_to_period(time_period, recur)

    def _load_starting_balance(self, period):
        """


        BusinessUnit._load_balance() -> None


        Connect starting balance sheet to past if available, copy shape to
        ending balance sheet.
        """

        pool = self.components.get_ordered()
        # Need stable order to make sure we pick up peer lines from units in
        # the same order. Otherwise, their order might switch and financials
        # would look different (even though the bottom line would be the same).

        for unit in pool:
            unit._load_starting_balance(period)

        if period.past:
            period_fins = self.get_financials(period)
            before_fins = self.get_financials(period.past)
            if before_fins:
                period_fins.starting = before_fins.ending
                # bal_start = before_fins.ending.copy()
                # bal_start.link_to(before_fins.ending)
                # bal_start.set_name('starting balance sheet')
                # period_fins.starting = bal_start
                # Connect to the past

    def _register_in_period(self, recur=True, overwrite=True):
        """


        BusinessUnit._register_in_period() -> None


        Method updates the bu_directory on the instance period with the contents
        of instance.components (bbid:bu). If ``recur`` == True, repeats for
        every component in instance.

        If ``overwrite`` == False, method will raise an error if any of its
        component bbids is already in the period's bu_directory at the time of
        call.

        NOTE: Method will raise an error only if the calling instance's own
        components have ids that overlap with the bu_directory. To the extent
        any of the caller's children have an overlap, the error will appear only
        when the recursion gets to them. As a result, by the time the error
        occurs, some higher-level or sibling components may have already updated
        the period's directory.
        """
        # UPGRADE-S: Can fix the partial-overwrite problem by refactoring this
        # routine into 2 pieces. build_dir(recur=True) would walk the tree and
        # return a clean dict. update_dir(overwrite=bool) would compare that
        # dict with the existing directory and raise an error if there is
        # an overlap. Also carries a speed benefit, cause only compare once.

        if not overwrite:
            if self.id.bbid in self.period.bu_directory:
                c = (
                    "TimePeriod.bu_directory already contains an object with "
                    "the same bbid as this unit. \n"
                    "unit id:         {bbid}\n"
                    "known unit name: {name}\n"
                    "new unit name:   {mine}\n\n"
                ).format(
                    bbid=self.id.bbid,
                    name=self.period.bu_directory[self.id.bbid].tags.name,
                    mine=self.tags.name,
                )
                print(self.period.bu_directory)
                raise bb_exceptions.IDCollisionError(c)

        # Check for collisions first, then register if none arise.
        self.period.bu_directory[self.id.bbid] = self

        brethren = self.period.ty_directory.setdefault(self.type, set())
        brethren.add(self.id.bbid)

        if recur:
            for unit in self.components.values():
                unit._register_in_period(recur, overwrite)

    def _set_components(self, comps=None):
        """


        BusinessUnit._set_components() -> None


        Method sets instance.components to the specified object, sets object to
        point to instance as its parent. If ``comps`` is None, method generates
        a clean instance of Components().
        """
        if not comps:
            comps = Components()
        comps.relationships.set_parent(self)
        self.components = comps

    def _update_balance(self, period):
        """


        BusinessUnit._load_balance() -> None


        Connect starting balance sheet to past if available, copy shape to
        ending balance sheet.
        """
        financials = self.get_financials(period)
        starting_balance = financials.starting
        ending_balance = financials.ending

        # Method expects balance sheet to come with accurate tables. We first
        # build the table in load_balance(). We then run consolidate(), which
        # will automatically update the tables if it changes the statement.

        if starting_balance and ending_balance:

            for name, starting_line in starting_balance._details.items():

                if starting_line.has_been_consolidated:
                    continue
                elif starting_line.value is not None:
                    ending_line = ending_balance.find_first(starting_line.name)
                    self._update_lines(starting_line, ending_line)

    def _update_lines(self, start_line, end_line):
        """


        BusinessUnit._update_lines() -> None


        Tool for BusinessUnit._update_balance().  Method recursively walks
        through top-level LineItem details from the starting balance sheet
        ``start_line`` and assigns their values to the matching line in the
        ending balance sheet ``end_line``.
        """

        if start_line._details:
            for name, line in start_line._details.items():
                ending_line = end_line.find_first(line.tags.name)

                self._update_lines(line, ending_line)
        else:
            if end_line.has_been_consolidated:
                pass
            elif start_line.value is not None:
                end_line.set_value(start_line.value,
                                   self._UPDATE_BALANCE_SIGNATURE)
