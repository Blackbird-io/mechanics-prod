# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL
# Blackbird Environment
# Module: data_structures.modelling.model
"""

Module defines Model class, a container that fully describes a company's past,
present, and future.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
Model                 structured snapshots of a company across time periods
====================  ==========================================================
"""




# imports
import pickle
import time

import bb_exceptions
import bb_settings
import tools.for_tag_operations
from chef_settings import DEFAULT_SCENARIOS
from data_structures.system.bbid import ID
from data_structures.modelling.line_item import LineItem
from data_structures.system.tags_mixin import TagsMixIn
from .time_line import TimeLine
from .taxo_dir import TaxoDir


# constants
# n/a

# classes
class Model(TagsMixIn):
    """

    This class provides a form of a standard time model of business performance.
    A Model object revolves around a Timeline, which consists of a list of
    snapshots of the business at different points in wall time. Each such
    snapshot is an instance of a TimePeriod object.

    Each Model instance has its own namespace_id derived from the origin
    Blackbird UUID. The Model's namespace_id is the source of truth for business
    units within that model. In other words, business units have ids that are
    unique within the Model. If a business unit has an id that's equal to that
    of another business unit, they represent the same real life referent within
    a given model.

    A Model can and should contain multiple instances of the same business unit,
    as determined by the business unit's bbid. Each TimePeriod in the TimeLine
    should contain its instance for the BusinessUnit to show how it evolves over
    time.

    On the other hand, each BusinessUnit should only appear once per TimePeriod,
    because within a given Model, the BusinessUnit can only have single state
    at a given point in time.

    To enforce the above requirement, each TimePeriod has a directory of all
    business units that exist within it. The directory is a dictionary of
    pointers to BUs, keyed by bbid, available at TimePeriod.bu_directory. The
    directory cuts across all levels of the BusinessUnit hierarchy within the
    TimePeriod: it includes keys for the top-level BU (TimePeriod.content) and
    any children, grandchildren, etc that BU may have.

    All BusinessUnits within a TimePeriod use the directory to check whether
    they can add a new business unit as a component. If the business unit's bbid
    is already in the directory, they cannot. If it is new to the TimePeriod,
    they can.
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    id                    instance of ID object, carries bbid for model
    interview             property; points to target BusinessUnit.interview
    portal_data           dict; stores data from Portal related to the instance
    stage                 property; points to target BusinessUnit.stage
    started               bool; property, tracks whether engine has begun work
    summary               P; pointer to current period summary
    target                P; pointer to target BusinessUnit
    taxo_dir              instance of TaxoDir, directory of taxonomy templates
    taxonomy              dict with tree of business unit templates
    time_line             list of TimePeriod objects
    transcript            list of entries that tracks Engine processing
    valuation             P; pointer to current period valuation

    FUNCTIONS:
    change_ref_date()     updates timeline to use new reference date
    copy()                returns a copy of Model instance
    from_portal()         class method, extracts model out of API-format
    get_company()         method to get top-level company unit
    get_financials()      method to get financials for a given unit and time
    get_timeline()        method to get timeline at specific resolution (m,q,a)
    start()               sets _started and started to True
    transcribe()          append message and timestamp to transcript
    ====================  ======================================================

    ``P`` indicates attributes decorated as properties. See attribute-level doc
    string for more information.
    """
    def __init__(self, name):
        TagsMixIn.__init__(self, name)

        self._started = False
        self.ref_date = None
        self.id = ID()
        self.id.assign(name)
        # Models carry uuids in the origin namespace.
        self.portal_data = dict()

        self.taxonomy = dict()
        self.taxo_dir = TaxoDir(model=self)
        self.taxo_dir.id.set_namespace(self.id.bbid)
        self.taxo_dir.id.assign(seed='taxonomy directory')

        self.transcript = []
        time_line = TimeLine(self)
        time_line.id.set_namespace(self.id.bbid)
        # dict holding various timelines
        self.timelines = dict()
        # main TimeLine is (resolution='monthly', actual=False)
        self.set_timeline(time_line)

        self.bu_directory = {}
        self.ty_directory = {}

        self.scenarios = dict()
        for s in DEFAULT_SCENARIOS:
            self.scenarios[s] = dict()

        self.company = None
        self.target = None
        # target is BU from which to get path and interview info, default
        # points to top-level business unit/company


    # DYNAMIC ATTRIBUTES
    @property
    def interview(self):
        return self.target.interview

    @property
    def stage(self):
        return self.target.stage

    @property
    def started(self):
        """


        **read-only property**


        Once True, difficult to undo (a toggle that sticks).
        """
        return self._started

    @property
    def summary(self):
        """


        **read-only property**


        Pointer to company summary.
        """
        company = self.get_company()
        if company:
            result = company.summary
            return result

    @summary.setter
    def summary(self, value):
        c = "Assignment prohibited. ``model.summary`` serves only as a pointer"
        c += " to the current period company summary."
        raise bb_exceptions.ManagedAttributeError(c)

    @property
    def valuation(self):
        """


        **read-only property**


        Pointer to company valuation on current period.
        """
        company = self.get_company()
        if company:
            # catch periods with empty content
            return company.valuation

    @valuation.setter
    def valuation(self, value):
        c = (
            "Assignment prohibited. "
            "``model.valuation`` serves only as a pointer "
            "to the current period company valuation."
        )
        raise bb_exceptions.ManagedAttributeError(c)

    @property
    def time_line(self):
        return self.get_timeline()

    @time_line.setter
    def time_line(self, time_line):
        return self.set_timeline(time_line)

    # METHODS
    @classmethod
    def from_portal(cls, portal_model):
        """


        Model.from_portal(portal_model) -> Model


        **CLASS METHOD**

        Method extracts a Model from portal_model.

        Method expects ``portal_model`` to be a string serialized by dill (or
        pickle).

        If portal_model does not specify a Model object, method creates a new
        instance. Method stores all portal data other than the Model in the
        output's .portal_data dictionary.
        """
        flat_model = portal_model["e_model"]

        if flat_model:
            M = pickle.loads(flat_model)
            business_name = portal_model["business_name"]
            if business_name:
                M.set_name(business_name)
        else:
            business_name = portal_model["business_name"]
            if not business_name:
                business_name = bb_settings.DEFAULT_MODEL_NAME
            M = cls(business_name)

        M.portal_data.update(portal_model)
        del M.portal_data["e_model"]

        return M

    def change_ref_date(self, ref_date):
        """


        Model.change_ref_date() -> None

        --``ref_date`` is datetime.date to use as the reference date for updated
                       timeline

        Method updates time_line to use adjusted ref_date.
        """

        if self.time_line.has_been_extrapolated:
            return

        new_tl = TimeLine(self)
        new_tl.parameters = self.time_line.parameters.copy()
        new_tl.master = self.time_line.master
        new_tl.build(ref_date=ref_date)
        new_tl.id.set_namespace(self.id.bbid)

        self.ref_date = ref_date
        self.set_timeline(new_tl, overwrite=True)

    def clear_excel(self):
        self.time_line.clear_excel()

    def copy(self):
        """


        Model.copy() -> obj


        Method creates a copy of instance and returns it.  Delegates to
        relevant classes to copy attributes.
        """
        result = Model(self.tags.title)
        result.ref_date = self.ref_date
        result._started = self._started
        result.portal_data = self.portal_data.copy()
        result.taxonomy = self.taxonomy.copy()
        result.transcript = self.transcript.copy()
        for key, time_line in self.timelines.items():
            new_tl = time_line.copy()
            new_tl.model = result
            result.set_timeline(new_tl, *key, overwrite=True)
        result.scenarios = self.scenarios.copy()
        result.target = self.target

        return result

    def get_company(self, buid=None):
        """

        Model.get_company() -> BusinessUnit

        Method returns top-level business unit from current period.
        """
        if buid:
            return self.bu_directory[buid]
        if self.company:
            return self.company
        return self.get_timeline().current_period.content

    def set_company(self, company):
        """

        Model.set_company() -> None

        Method sets the company as the top-level unit.
        """
        self.bu_directory.clear()
        self.ty_directory.clear()
        self.register(company, update_id=True, overwrite=False, recur=True)
        self.company = company

    def get_financials(self, bbid, period):
        """

        Model.get_financials() -> Financials

        --``bbid`` is the ID.bbid for the BusinessUnit whose financials you are
         seeking
        --``period`` is an instance of TimePeriod or TimePeriodBase

        Method returns the specified version of financials.
        """
        if bbid in period.financials:
            fins = period.financials[bbid]
        elif bbid in period.bu_directory:
            unit = period.bu_directory[bbid]
            fins = unit.get_financials(period)
        else:
            unit = self.time_line.current_period.content
            fins = unit.get_financials(period)

        return fins

    def get_timeline(self, resolution='monthly', actual=False):
        """

        Model.get_timeline() -> TimeLine

        --``resolution`` is 'monthly', 'quarterly', 'annually' or any available
          summary resolution'

        Method returns the timeline for specified resolution (if any).
        """
        key = (resolution, actual)
        if key in self.timelines:
            return self.timelines[key]

    def prep_for_monitoring_interview(self):
        """


        prep_monitoring_interview(portal_model) -> PortalModel

        --``portal_model`` is an instance of PortalModel

        Function sets path for monitoring interview after projections are set.
        Function runs after pressing the "update" button on the model card.
        """
        if not self.started:
            self.start()

        # set company as target
        co = self.get_company()
        co._stage = None
        self.target = co

        # preserve existing path and set fresh BU.used and BU.stage.path
        co.archive_path()
        co.archive_used()

        # set monitoring path:
        new_line = LineItem("monitoring path")
        self.target.stage.path.append(new_line)

        if not self.target.stage.focal_point:
            self.target.stage.set_focal_point(new_line)

    def set_timeline(
        self, time_line, resolution='monthly', actual=False, overwrite=False
    ):
        """

        Model.set_timeline() -> None

        --``resolution`` is 'monthly', 'quarterly', 'annually' or any available
          summary resolution'

        Method adds the timeline for specified resolution (if any).
        """
        key = (resolution, actual)
        if key in self.timelines and not overwrite:
            c = (
                "TimeLine (resolution='{}', actual='{}') "
                "already exists".format(*key)
            )
            raise KeyError(c)

        time_line.actual = actual
        time_line.resolution = resolution

        self.timelines[key] = time_line

    def start(self):
        """


        Model.start() -> None


        Method sets instance._started (and ``started`` property) to True.
        """
        self._started = True

    def transcribe(self, message):
        """


        Model.transcribe(message) -> None


        Appends a tuple of (message ,time of call) to instance.transcript.
        """
        time_stamp = time.time()
        record = (message, time_stamp)
        self.transcript.append(record)

    def get_units(self, pool):
        """


        Model.get_units() -> list


        Method returns a list of objects from instance.bu_directory that
        correspond to each bbid in ``pool``. Method sorts pool prior to
        processing.

        Method expects ``pool`` to be an iterable of bbids.
        """
        pool = sorted(pool)
        # make sure to sort pool for stable output order
        units = []
        for bbid in pool:
            u = self.bu_directory[bbid]
            units.append(u)
        return units

    def get_lowest_units(self, pool=None, run_on_empty=False):
        """


        Model.get_lowest_units() -> list


        Method returns a list of units in pool that have no components.

        Method expects ``pool`` to be an iterable of bbids.

        If ``pool`` is None, method will build its own pool from all keys in
        the instance's bu_directory. Method will raise error if asked to run
        on an empty pool unless ``run_on_empty`` == True.
        """
        if pool is None:
            pool = sorted(self.bu_directory.keys())
        else:
            pool = sorted(pool)
        # make sure to sort pool for stable output order
        #
        if any([pool, run_on_empty]):
            foundation = []
            for bbid in pool:
                bu = self.bu_directory[bbid]
                if bu.components:
                    continue
                else:
                    foundation.append(bu)
            #
            return foundation
            #
        else:
            c = "``pool`` is empty, method requires explicit permission to run."
            raise bb_exceptions.ProcessError(c)

    def get_tagged_units(self, *tags, pool=None):
        """


        Model.get_tagged_units() -> dict


        Return a dictionary of units (by bbid) that carry the specified tags.

        If ``pool`` is None, uses bu_directory.
        Delegates all selection work to tools.for_tag_operations.get_tagged()
        """
        if not pool:
            pool = self.bu_directory.values()
            # We want a consistent order for the pool across run times
            pool = list(pool)
            pool.sort(key=lambda bu: bu.id.bbid)

        tagged_dict = tools.for_tag_operations.get_tagged(pool, *tags)

        return tagged_dict

    def register(
            self, bu, update_id=True, overwrite=True, recur=True
    ):
        """


        Model.register() -> None


        Manually add unit to period. Unit will conform to period and appear
        in directories. Use sparingly: designed for master (taxonomy) period.

        NOTE: content should generally have a tree structure, with a
        single bu node on top. That node will manage all child relationships.
        Accordingly, the best way to add units to a model is to run
        bu.add_component(new_unit).

        If ``update_id`` is True, method will assign unit a new id in the
        model's namespace. Parameter should be True when adding a top-level
        unit, False when adding child units.
        """
        # Make sure unit has an id in the right namespace.
        if update_id:
            bu._update_id(namespace=self.id.namespace, recur=True)
        if not bu.id.bbid:
            c = "Cannot add content without a valid bbid."
            raise bb_exceptions.IDError(c)

        if not overwrite:
            # Check for collisions first, then register if none arise.
            if bu.id.bbid in self.bu_directory:
                c = (
                    "TimePeriod.bu_directory already contains an object with "
                    "the same bbid as this unit. \n"
                    "unit id:         {bbid}\n"
                    "known unit name: {name}\n"
                    "new unit name:   {mine}\n\n"
                ).format(
                    bbid=bu.id.bbid,
                    name=self.bu_directory[bu.id.bbid].tags.name,
                    mine=bu.tags.name,
                )
                print(self.bu_directory)
                raise bb_exceptions.IDCollisionError(c)

        self.bu_directory[bu.id.bbid] = bu

        brethren = self.ty_directory.setdefault(bu.type, set())
        brethren.add(bu.id.bbid)

        bu.relationships.set_model(self)
        now = self.get_timeline().current_period
        now.financials[bu.id.bbid] = bu.financials

        if recur:
            for unit in bu.components.values():
                self.register(
                    unit, update_id=update_id, overwrite=overwrite, recur=recur
                )

