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
import logging
import bb_settings
import bb_exceptions
import tools.for_printing as views
from data_structures.serializers.chef import data_management as xl_mgmt
from data_structures.system.bbid import ID
from data_structures.system.relationships import Relationships
from data_structures.system.tags_mixin import TagsMixIn
from data_structures.guidance.guide import Guide
from data_structures.guidance.interview_tracker import InterviewTracker
from data_structures.modelling.statement import Statement
from data_structures.system.tags import Tags
from data_structures.valuation.business_summary import BusinessSummary
from data_structures.valuation.company_value import CompanyValue

from . import common_events

from .financials import Financials
from .components import Components
from .equalities import Equalities
from .life import Life as LifeCycle
from .parameters import Parameters
from .capital_structure.cap_table import CapTable




# Constants
# n/a

# Globals
logger = logging.getLogger(bb_settings.LOGNAME_MAIN)

# Classes
class BusinessUnit(TagsMixIn, Equalities):
    """

    Object describes a group of business activity. A business unit can be a
    store, a region, a product, a team, a relationship (or many relationships).
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    cap_table             instance of CapTable class
    complete              bool; if financials are complete for unit in period
    components            instance of Components class, stores business units
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
    type                  str or None; unit's in-model type (e.g., "team")
    used                  set; contains BBIDs of used Topics
    valuation             None or CompanyValue; market view on unit

    FUNCTIONS:
    add_component()       adds unit to instance components
    add_driver()          registers a driver
    archive_path()        archives existing path then sets to blank Statement
    archive_used()        archives existing used topics and sets to blank set
    compute()             consolidates and derives a statement for all units
    copy()                create a copy of this BusinessUnit instance
    fill_out()            runs calculations to fill out financial statements
    get_current_period()  returns current period on BU.model.time_line
    get_financials()      returns Financials from a period or creates a new one
    get_parameters()      returns Parameters from TimeLine, Period, self
    kill()                make dead, optionally recursive
    make_past()           put a younger version of financials in prior period
    recalculate()         reset financials, compute again, repeat for future
    reset_financials()    resets instance and (optionally) component financials
    set_analytics()       attaches an object to instance.analytics
    set_financials()      attaches a Financials object from the right template
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
        TagsMixIn.__init__(self, name)

        self._parameters = Parameters()
        self._type = None
        self.id = ID()
        self.life = LifeCycle()
        self.location = None
        self.size = 1
        self.xl = xl_mgmt.UnitData()

        self.components = None
        self._set_components()  # Only used in copy()

        self.relationships = Relationships(self, model=model)

        # financials must follow relationships in __init__ because we set the
        # period on financials, an the period is retrieved from model, which
        # is stored on relationships.
        self.financials = None
        self.set_financials(fins)

        # Attributes related to Path
        self._stage = None
        self.used = set()
        self.guide = Guide()
        self.interview = InterviewTracker()
        self.summary = None
        self.valuation = CompanyValue()

        # for monitoring, temporary storage for existing path and used sets
        self._path_archive = list()
        self._used_archive = list()
        
        self.cap_table = CapTable()

    @classmethod
    def from_database(cls, portal_data, link_list=list()):
        new = cls(None)
        new.tags = Tags.from_database(portal_data['tags'])
        new._parameters = Parameters.from_database(portal_data['parameters'],
                                                 target='parameters')
        new._type = portal_data['type']
        new.life = LifeCycle.from_database(portal_data['life'])
        new.location = portal_data['location']
        new.size = portal_data['size']

        ids = portal_data['used']
        real_ids = [ID.from_database(id).bbid for id in ids]
        new.used = set(real_ids)
        new.guide = Guide.from_database(portal_data['guide'])
        new.components = [ID.from_database(id).bbid for id in portal_data['components']]
        new.interview = InterviewTracker.from_database(portal_data['interview'],
                                                     link_list)

        summary = portal_data['summary']
        if summary:
            new.summary = BusinessSummary.from_database(summary)
        else:
            # preserve None values here
            new.summary = summary

        valuation = portal_data['valuation']
        if valuation:
            new.valuation = CompanyValue.from_database(valuation)
        else:
            # preserve None values here
            new.valuation = valuation

        stage = portal_data['stage']
        if stage == 'valuation':
            new._stage = new.valuation

        new._path_archive = portal_data['path_archive'] # don't bother reinfl-
        # ating archived paths, they won't be used
        new._used_archive = portal_data['used_archive']

        fins = portal_data.get('financials_structure')
        new_fins = Financials.from_database(fins, new, period=None)
        new.set_financials(new_fins)

        new.cap_table = CapTable.from_database(portal_data['cap_table'])

        return new

    def to_database(self, taxonomy=False):
        data = dict()
        data['parameters'] = list(self._parameters.to_database(target='parameters'))
        data['type'] = self._type
        data['components'] = [k.hex for k in self.components.keys()]
        data['bbid'] = self.id.bbid.hex
        data['life'] = self.life.to_database()
        data['location'] = self.location
        data['name'] = self.name
        data['title'] = self.title
        data['size'] = self.size
        data['tags'] = self.tags.to_database()
        data['financials_structure'] = self.financials.to_database()

        if self._stage is self.valuation and self._stage is not None:
            stage = 'valuation'
        else:
            stage = None

        data['stage'] = stage
        data['used'] = [id.hex for id in self.used]
        data['guide'] = self.guide.to_database()
        data['interview'] = self.interview.to_database()

        data['summary'] = self.summary.to_database() if self.summary else None
        data['valuation'] = self.valuation.to_database() if self.valuation else None

        # for monitoring, temporary storage for existing path and used sets
        data['path_archive'] = self._path_archive
        data['used_archive'] = self._used_archive
        data['taxonomy'] = taxonomy
        data['cap_table'] = self.cap_table.to_database()

        return data

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
        """


        **property**


        Sets ._type. Updates ty_directory when type is changed.
        """
        old_type = self.type
        self._type = value

        model = self.relationships.model
        if model:
            in_model = False
            in_taxonomy = False

            # Determine if bu is in model or taxo_dir
            if self.id.bbid in model.bu_directory:
                if self is model.bu_directory[self.id.bbid]:
                    ty_directory = model.ty_directory
                    in_model = True

            if self.id.bbid in model.taxo_dir.bu_directory:
                if self is model.taxo_dir.bu_directory[self.id.bbid]:
                    ty_directory = model.taxo_dir.ty_directory
                    in_taxonomy = True

            if in_model and in_taxonomy:
                print(self.name + " is both model.bu_dir and taxo_dir!!")
                raise bb_exceptions.BBAnalyticalError

            if in_model or in_taxonomy:
                if old_type in ty_directory:
                    old_id_set = ty_directory.get(old_type)
                    old_id_set.remove(self.id.bbid)
                    # Remove sets if they are empty
                    if len(old_id_set) == 0:
                        ty_directory.pop(old_type)

                new_id_set = ty_directory.setdefault(value, set())
                new_id_set.add(self.id.bbid)
                # Entries are sets of bbids for units that belong to that type

    @type.deleter
    def type(self):
        c = "``type`` is a property; delete prohibited. to represent generic "
        c += "unit, set to None instead."
        raise bb_exceptions.ManagedAttributeError(c)

    def __hash__(self):
        return self.id.__hash__()

    def __str__(self, lines=None):
        """


        BusinessUnit.__str__() -> str


        Method concatenates each line in ``lines``, adds a new-line character at
        the end, and returns a string ready for printing. If ``lines`` is None,
        method calls views.view_as_unit() on instance.
        """
        # Get string list, slap a new-line at the end of every line and return
        # a string with all the lines joined together.
        if not lines:
            lines = views.view_as_base(self)

        # Add empty strings for header and footer padding
        lines.insert(0, "")
        lines.append("")

        box = "\n".join(lines)
        return box

    def add_component(
            self, bu, update_id=True, register_in_dir=True, overwrite=False
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

        If register_in_dir is true, method raises IDCollisionError if the
        period's directory already contains the new business unit's bbid.

        If all id verification steps go smoothly, method delegates insertion
        down to Components.add_item().

        Usage Scenarios:

        Adding a newly created ChildBU:
            ParentBU.add_component(ChildBU, True, True)
        Transferring a ChildBU from one parent to another:
            ParentBU2.add_component(ChildBU, False, False)

        """
        bu.valuation = None
        bu.relationships.set_model(self.relationships.model)

        # Step 1: optionally update ids.
        if update_id:
            bu._update_id(namespace=self.id.bbid, recur=True)

        # Step 2: Add component
        self.components.add_item(bu)

        # Step 3: Register the units. Will raise errors on collisions.
        bu._register_in_dir(recur=True, overwrite=overwrite)

    def remove_component(self, buid):
        """


        BusinessUnit.add_component() -> None


        """
        # Step 1: remove from directories
        mo = self.relationships.model
        bu = self.components[buid]

        mo.ty_directory[bu.type] -= {bu.id.bbid}
        mo.bu_directory.pop(bu.id.bbid)

        # Step 2: remove component
        self.components.remove_item(buid)

    def archive_path(self):
        """


        BusinessUnit.archive_path() -> None


        Method archives existing path to BusinessUnit._path_archive and sets
         the path to a clean Statement().  Method is used by monitoring to
         pre-process before setting the monitoring path.
        """
        if self.stage.path is not None:
            self._path_archive.append(self.stage.path.to_database())

        new_path = Statement()
        self.stage.set_path(new_path)

    def archive_used(self):
        """


        BusinessUnit.archive_used() -> None


        Method archives existing set of used topics to
        BusinessUnit._used_archive and sets used to a new empty set. Method is
        used by monitoring to pre-process before setting the monitoring path.
        """
        used = [id.hex for id in self.used]
        self._used_archive.append(used)
        self.used = set()

    def check_statement_structure(self, statement_name, period=None):
        if not period:
            period = self.relationships.model.get_timeline().current_period

        struct_stmt = getattr(self.financials, statement_name)
        struct_stmt = struct_stmt.copy(clean=True)

        fins = self.get_financials(period)
        fins.__dict__[statement_name] = struct_stmt
        struct_stmt.relationships.set_parent(fins)
        struct_stmt.set_period(period)

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

    def consolidate_fins_structure(self):

        for unit in self.components.get_all():
            unit.consolidate_fins_structure()

        for statement in self.financials.full_order:
            self._consolidate(statement, period=None, struct=True)

        self.relationships.model.clear_fins_storage()

    def copy(self):
        """


        BU.copy() -> BU


        Method returns a new business unit that is a deep-ish copy of the
        instance.

        The new bu starts out as a shallow Tags.copy() copy of the instance.
        The method then sets the following attributes on the new bu to either
        deep or class-specific copies of the instance values:

        - components
        - financials
        - header.profile
        - id (vanilla shallow copy)
        - life

        The class-specific copy methods for components, drivers, and financials
        all return deep copies of the object and its contents. See their
        respective class documentation for mode detail.
        """
        result = copy.copy(self)
        result.tags = self.tags.copy()
        result.relationships = self.relationships.copy()
        # Start with a basic shallow copy, then add tags
        #
        r_comps = self.components.copy()
        result._set_components(r_comps)

        r_fins = self.financials.copy()
        result.set_financials(r_fins)

        result.id = copy.copy(self.id)

        result.guide = copy.deepcopy(self.guide)
        # Have to make a deep copy of guide because it is composed of Counter
        # objects. Guide shouldn't point to a business unit or model
        result.life = self.life.copy()
        result.summary = None
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

        if not period:
            period = self.get_current_period()
        self._load_starting_balance(period)

        for statement in financials.compute_order:
            self.compute(statement, period)

        self._compute_ending_balance(period)

        self._check_start_balance(period)

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
        period.clear()

        # self.reset_financials(period=period)
        self.fill_out(period=period)
        if adjust_future and period and period.future:
            self.recalculate(adjust_future=True, period=period.future)

    def recompute(self, statement_name, period=None, adjust_future=True):
        """


        BusinessUnit.recompute () -> None

        --``statement_name`` is the string name of the statement attribute on
        financials
        --``period`` is an instance of TimePeriod
        --``adjust_future`` is a boolean, whether to run in future periods

        Recompute a particular statement on financials.  If ``adjust_future``
         is True, will repeat for all future snapshots.
        """
        self.reset_statement(statement_name, period=period)
        self.compute(statement_name, period=period)

        if adjust_future and period and period.future:
            self.recompute(statement_name, adjust_future=adjust_future,
                           period=period.future)

    def reset_financials(self, period=None, recur=True):
        """


        BusinessUnit.reset_financials() -> None


        Method resets financials for instance and, if ``recur`` is True, for
        each of the components. Method sets instance.filled to False.
        """
        # self.filled = False
        financials = self.get_financials(period)
        financials.reset()
        if recur:
            pool = self.components.get_all()

            for bu in pool:
                bu.reset_financials(period=period, recur=recur)

    def reset_statement(self, statement_name, period=None, recur=True):
        """


        BusinessUnit.reset_statement() -> None

        --``statement_name`` is the string name of the statement attribute on
        financials
        --``period`` is an instance of TimePeriod
        --``recur`` is a bool; whether to reset components

        Method resets the given statement for this unit and optionally each
        of its components.
        """
        fins = self.get_financials(period)
        statement = getattr(fins, statement_name)
        statement.reset()

        if recur:
            for unit in self.components.get_all():
                unit.reset_statement(statement_name, period=period)

    def set_analytics(self, atx):
        """


        BusinessUnit.set_analytics() -> None


        Method sets instance.analytics to passed-in argument, sets analytics
        object to point to instance as its parent.
        """
        atx.relationships.set_parent(self)
        self.valuation = atx

    def set_financials(self, fins=None):
        """


        BusinessUnit.set_financials() -> None


        Method for initializing instance.financials with a properly configured
        Financials object.

        Method will set instance financials to ``fins``, if caller specifies
        ``fins``. Otherwise, method will set financials to a new Financials
        instance.
        """
        if fins is None:
            fins = Financials(parent=self)

        fins.relationships.set_parent(self)
        self.financials = fins

    def set_name(self, name):
        self.tags.set_name(name)

        mo = self.relationships.model
        if mo:
            if self.id.bbid in mo.bu_directory:
                mo.set_company(mo.get_company())
            elif self.id.bbid in mo.taxo_dir.bu_directory:
                self._update_id(self.id.namespace)
                mo.taxo_dir.refresh_ids()
            else:
                self._update_id(self.id.namespace)
        else:
            self._update_id(self.id.namespace)

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

    def get_current_period(self):
        """


        BusinessUnit.get_current_period() -> TimePeriod

        Convenience method to get current_period from parent model's
        default timeline.
        """
        model = self.relationships.model
        if model:
            return model.get_timeline().current_period

    def get_financials(self, period=None):
        """


        BusinessUnit.get_financials() -> Financials()

        --``period`` TimePeriod

        Returns this BUs financials in a given period.
        If no financials exist, creates a new financials with same structure
        Stores financials in period.financials dict, keyed by BU.id.bbid
        """
        model = self.relationships.model
        now = model.get_timeline().current_period if model else None

        if not period:
            period = now

        if period is None:
            c = "PERIOD IS NONE!!!!! CANNOT GET FINANCIALS"
            raise ValueError(c)

        if self.id.bbid in period.financials:
            # the best case we expect: financials have been assigned to a period
            fins = period.financials[self.id.bbid]
        else:
            # make sure balance sheets have matching structures
            self.financials.check_balance_sheets()

            fins = self.financials.copy(clean=True)
            fins.relationships.set_parent(self)
            fins.period = period
            fins.populate_from_stored_values(period)

            fins.restrict()

            for statement in fins.full_ordered:
                if statement:
                    for line in statement._details.values():
                        line._update_stored_value(recur=False)

            period.financials[self.id.bbid] = fins

        return fins
    
    def get_parameters(self, period=None):
        """


        BusinessUnit.get_financials() -> Financials()

        --``period`` TimePeriod

        Method combines all parameters from reachable sources in order
        of precedence. Driver updates the results with own parameters.
        """
        if not period:
            period = self.get_current_period()
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
                    new_line, position=end_line.position,
                    noclear=True
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
                    start_line.add_line(new_line, position=end.position, noclear=True)

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

        self._consolidate("ending", period)

        self._update_balance(period)
        # Sets ending balance lines to starting values by default

        self._derive("ending", period)
        # Derive() will overwrite ending balance sheet where appropriate

    def _consolidate(self, statement_name, period=None, struct=False):
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
            self._consolidate_unit(unit, statement_name, period, struct=struct)

    def _consolidate_unit(self, sub, statement_name, period=None, struct=False):
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
        if struct:
            sub_fins = sub.financials
            top_fins = self.financials
        else:
            sub_fins = sub.get_financials(period)
            top_fins = self.get_financials(period)

        sub_statement = getattr(sub_fins, statement_name, None)
        top_statement = getattr(top_fins, statement_name, None)

        xl_only = True
        if period:
            if sub.life.conceived(period):
                xl_only = False

        if struct:
            xl_only = False

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

    def _derive_line(self, line, period=None):
        """


        BusinessUnit.derive_line() -> None

        --``line`` is the LineItem to work on

        Method computes the value of a line using drivers stored on the
        instance.  Method builds a queue of applicable drivers for the provided
        LineItem. Method then runs the drivers in the queue sequentially. Each
        LineItem gets a unique queue.

        Method will not derive any lines that are hardcoded or have already
        been consolidated (LineItem.hardcoded == True or
        LineItem.has_been_consolidated == True).
        """

        # Repeat for any details
        if line._details:
            for detail in line.get_ordered():
                if detail.replica:
                    continue
                    # Skip replicas to make sure we apply the driver only once
                    # A replica should never have any details
                else:
                    self._derive_line(detail, period)

        # look for drivers based on line name, line parent name, all line tags
        driver = line.get_driver()
        if driver:
            driver.workOnThis(line, bu=self, period=period)

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
            before_fins = self.get_financials(period.past)
            period_fins = self.get_financials(period)

            period_fins.starting = before_fins.ending

    def _register_in_dir(self, recur=True, overwrite=True):
        """


        BusinessUnit._register_in_dir() -> None


        Method updates the bu_directory on with (bbid:bu).
        Method does nothing if BU is not connected to the Model yet.

        If ``recur`` == True, repeats for every component in instance.

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

        model = self.relationships.model
        if not model:
            # Do nothing if Business Unit is not part of the model yet.
            return

        # Default case
        bu_directory = model.bu_directory
        ty_directory = model.ty_directory

        # If _register_in_dir is called from taxonomy_template.add_component(bu)
        parent_bu_components = self.relationships.parent
        if parent_bu_components:
            # For every ChildBU, its parent is a Components object
            # You must go 2 parent levels up to get to ParentBU
            parent_bu = parent_bu_components.relationships.parent
            if parent_bu:
                if parent_bu.id.bbid in model.taxo_dir.bu_directory:
                    bu_directory = model.taxo_dir.bu_directory
                    ty_directory = model.taxo_dir.ty_directory

        if not overwrite:
            # Check for collisions first, then register if none arise.
            if self.id.bbid in bu_directory:
                c = (
                    "bu_directory already contains an object with "
                    "the same bbid as this unit. \n"
                    "unit id:         {bbid}\n"
                    "known unit name: {name}\n"
                    "new unit name:   {mine}\n\n"
                ).format(
                    bbid=self.id.bbid,
                    name=bu_directory[self.id.bbid].tags.name,
                    mine=self.tags.name,
                )
                raise bb_exceptions.IDCollisionError(c)

        bu_directory[self.id.bbid] = self

        brethren = ty_directory.setdefault(self.type, set())
        brethren.add(self.id.bbid)

        if recur:
            try:
                components = self.components.values()
            except AttributeError:
                components = list()

            for unit in components:
                unit._register_in_dir(recur, overwrite)

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

    def _update_id(self, namespace, recur=True):
        """


        BusinessUnit._update_id() -> None


        Assigns instance a new id in the namespace, based on the instance name.
        If ``recur`` == True, updates ids for all components in the parent
        instance bbid namespace.
        """
        self.id.set_namespace(namespace)
        self.id.assign(self.tags.name)
        self.financials.register(namespace=self.id.bbid)
        # This unit now has an id in the namespace. Now pass our bbid down as
        # the namespace for all downstream components.

        if recur:
            try:
                components = self.components.values()
            except AttributeError:
                components = list()

            for unit in components:
                unit._update_id(namespace=self.id.bbid, recur=True)

            try:
                self.components.refresh_ids()
            except AttributeError:
                pass
                
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
