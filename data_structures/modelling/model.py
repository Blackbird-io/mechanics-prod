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
from data_structures.modelling.financials import Financials
from data_structures.system.bbid import ID
from data_structures.modelling.business_unit import BusinessUnit
from data_structures.modelling.line_item import LineItem
from data_structures.modelling.dr_container import DriverContainer
from data_structures.system.tags_mixin import TagsMixIn
from data_structures.system.summary_maker import SummaryMaker
from tools.parsing import date_from_iso
from .time_line import TimeLine
from .taxo_dir import TaxoDir
from .taxonomy import Taxonomy

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
    of another business unit, they represent the same real life reference within
    a given model.

    A Model should contain a single instance of the same business unit for each
    unit's bbid. Each TimePeriod in the TimeLine should contain a instance of
    Financials that are keyed by that business unit's bbid.

    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    bu_directory          dict; key = bbid, val = business units
    id                    instance of ID object, carries bbid for model
    interview             property; points to target BusinessUnit.interview
    portal_data           dict; stores data from Portal related to the instance
    report_summary        dict: stores data that Portal reads for reporting
    stage                 property; points to target BusinessUnit.stage
    started               bool; property, tracks whether engine has begun work
    summary               P; pointer to current period summary
    target                P; pointer to target BusinessUnit
    taxo_dir              instance of TaxoDir, has a dict {bbid: taxonomy units}
    taxonomy              dict with tree of business unit templates
    topic_list            list of topic names run on model
    time_line             list of TimePeriod objects
    transcript            list of entries that tracks Engine processing
    ty_directory          dict; key = strings, val = sets of bbids
    valuation             P; pointer to current period valuation

    FUNCTIONS:
    calc_summaries()      creates or updates standard summaries for model
    change_ref_date()     updates timeline to use new reference date
    clear_fins_storage()  clears financial data from non SSOT financials
    copy()                returns a copy of Model instance
    create_timeline()     creates a timeline with the specified attributes
    get_company()         method to get top-level company unit
    get_financials()      method to get financials for a given unit and time
    get_line()            finds LineItem from specified parameters
    get_lowest_units()    return list of units w/o components from bbid pool
    get_tagged_units()    return dict of units (by bbid) with specified tags
    get_timeline()        method to get timeline at specific resolution (m,q,a)
    get_units()           return list of units from bbid pool
    populate_xl_data()    method populates xl attr on all line items pre-chop
    prep_for_monitoring_interview()  sets up path entry point for reporting
    prep_for_revision_interview()  sets up path entry point for revision
    prep_summaries()      creates SummaryMaker based on default timeline
    register()            registers item in model namespace
    set_company()         method sets BusinessUnit as top-level company
    set_timeline()        method sets default timeline
    start()               sets _started and started to True
    to_portal()           creates a flattened version of model for Portal
    transcribe()          append message and timestamp to transcript

    CLASS METHODS:
    from_portal()         class method, extracts model out of API-format
    ====================  ======================================================

    ``P`` indicates attributes decorated as properties. See attribute-level doc
    string for more information.
    """

    def __init__(self, name):
        TagsMixIn.__init__(self, name)

        self._company = None
        self._ref_date = None
        self._started = False

        self.drivers = DriverContainer()

        self.id = ID()
        self.id.assign(name)
        # Models carry uuids in the origin namespace.

        self.portal_data = dict()

        self.report_summary = None

        self.taxo_dir = TaxoDir(model=self)
        self.taxonomy = Taxonomy(self.taxo_dir)

        self.timelines = dict()
        time_line = TimeLine(self)
        self.set_timeline(time_line)

        self.transcript = []

        # business units
        self.target = None
        self.bu_directory = dict()
        self.ty_directory = dict()

        # scenarios parameters
        self.scenarios = dict()
        for s in DEFAULT_SCENARIOS:
            self.scenarios[s] = dict()

        self.summary_maker = None

        # read-only attribute
        self._processing_status = 'intake'

        self.topic_list = []

    # DYNAMIC ATTRIBUTES
    @property
    def interview(self):
        return self.target.interview

    @property
    def processing_status(self):
        return self._processing_status

    @property
    def ref_date(self):
        return self._ref_date

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

        # Make blank TaxoDir structure
        M.taxo_dir = TaxoDir(M)
        
        # set processing stage
        M._processing_status = M.portal_data.pop('processing_status', 'intake')

        link_list = list()
        # first deserialize BusinessUnits into directory
        temp_directory = dict()
        for flat_bu in portal_model.get('business_units', list()):
            rich_bu = BusinessUnit.from_portal(flat_bu, link_list)
            rich_bu.relationships.set_model(M)
            temp_directory[flat_bu['bbid']] = rich_bu

        # now rebuild structure
        company_id = portal_model.get('company', None)
        if company_id:
            def build_bu_structure(seed, directory):
                component_list = seed.components
                seed.components = None
                seed._set_components()
                for component_id in component_list:
                    sub_bu = directory[component_id]
                    seed.add_component(sub_bu)
                    build_bu_structure(sub_bu, directory)

            top_bu = temp_directory[company_id]
            build_bu_structure(top_bu, temp_directory)
            M.set_company(top_bu)

        # TaxoDir
        data = portal_model.get('taxo_dir', None)
        if data:
            M.taxo_dir = TaxoDir.from_portal(data, M, link_list)
        else:
            M.taxo_dir = TaxoDir(M)

        # Taxonomy
        data = portal_model.get('taxonomy', None)
        if data:
            M.taxonomy = Taxonomy.from_portal(data, M.taxo_dir)
        else:
            M.taxonomy = Taxonomy(M.taxo_dir)

        # Target
        target_id = portal_model.get('target', None)
        if target_id:
            try:
                M.target = M.bu_directory[target_id]
            except KeyError:
                M.target = M.taxo_dir.bu_directory[target_id]

        # reinflate timelines
        if portal_model.get('timelines'):
            timelines = {}
            for data in portal_model['timelines']:
                key = (data['resolution'], data['name'])
                timelines[key] = TimeLine.from_portal(data, model=M)
            M.timelines = timelines

        # reinflate summary maker, if any
        if M.summary_maker:
            tnam = M.summary_maker['timeline_name']
            temp_sm = SummaryMaker(M, timeline_name=tnam, init=False)
            temp_sm._fiscal_year_end = M.summary_maker['_fiscal_year_end']
            M.summary_maker = temp_sm

        drivers = portal_model.get('drivers')
        if drivers:
            M.drivers = DriverContainer.from_portal(drivers)
        else:
            M.drivers = DriverContainer()

        return M

    def to_portal(self):
        """

        Model.to_portal() -> dict

        Method yields a serialized representation of self.

        NEED TO MAKE SURE WE CAPTURE FINS FROM EACH BU
        """
        result = dict()

        result['company'] = self._company.id.bbid if self._company else None
        result['target'] = self.target.id.bbid if self.target else None

        if self.target:
            print('TARGET TO: ' + self.target.name)

        # pre-process financials in the current period, make sure they get
        # serialized in th database to maintain structure data
        bu_list = list()
        for id, bu in self.bu_directory.items():
            bu_list.append(bu.to_portal())

        result['business_units'] = bu_list
        result['taxonomy'] = self.taxonomy.to_portal()
        result['taxo_dir'] = self.taxo_dir.to_portal()

        # serialized representation has a list of timelines attached
        # with (resolution, name) as properties
        timelines = []
        for (resolution, name), time_line in self.timelines.items():
            data = {
                'resolution': resolution,
                'name': name,
            }
            # add serialized periods
            data.update(time_line.to_portal())
            timelines.append(data)

        result['timelines'] = timelines
        result['drivers'] = self.drivers.to_portal()

        return result

    def calc_summaries(self):
        """


        Model.calc_summaries() -> None

        Method deletes existing summaries and recalculates.
        """
        try:
            self.timelines.pop(('quarterly', 'default'))
            self.timelines.pop(('annual', 'default'))
        except KeyError:
            # explicitly silence
            pass

        summary_builder = SummaryMaker(self)

        tl = self.get_timeline('monthly', 'default')
        seed = tl.current_period

        for period in tl.iter_ordered(open=seed.end):
            if period.end >= seed.end:
                summary_builder.parse_period(period)

        summary_builder.wrap()

    def change_ref_date(self, ref_date, build=False):
        """


        Model.change_ref_date() -> None

        --``ref_date`` is datetime.date to use as the reference date for updated
                       timeline

        Method updates time_line to use adjusted ref_date.
        """
        ntls = len(self.timelines.values())
        all_periods_exist = True
        for tl in self.timelines.values():
            per = tl.find_period(ref_date)
            if not per:
                all_periods_exist = False

        if build and ntls == 1:
            new_tl = TimeLine(self)
            new_tl.parameters = self.time_line.parameters.copy()
            new_tl.master = self.time_line.master
            new_tl.build(ref_date=ref_date)
            new_tl.id.set_namespace(self.id.bbid)
            self.set_timeline(new_tl, overwrite=True)
        elif build and ntls > 1:
            c = "ERROR: Cannot build arbitrary timelines."
            raise (ValueError(c))
        elif not all_periods_exist and not build:
            c = "ERROR: TimePeriod corresponding to ref_date does not exist " \
                "in all timelines."
            raise (ValueError(c))

        self._ref_date = ref_date

    def clear_fins_storage(self):
        """


        Model.clear_fins_storage() --> None


        Method clears financial values and xl data storage after modification
        to SSOT financials.
        """
        for tl in self.timelines.values():
            for per in tl.values():
                per.clear()

    def copy(self):
        """


        Model.copy() -> obj


        Method creates a copy of instance and returns it.  Delegates to
        relevant classes to copy attributes.
        """
        result = Model(self.tags.title)
        result._ref_date = self._ref_date
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

    def create_timeline(
            self, resolution='monthly', name='default', add=True,
            overwrite=False
    ):
        """

        Model.create_timeline() -> TimeLine

        --``resolution`` is 'monthly', 'quarterly', 'annually' or any available
          summary resolution'

        Method creates a timeline and adds it to the dictionary of own
        timelines.
        """
        time_line = TimeLine(self, resolution=resolution, name=name)
        if add:
            self.set_timeline(
                time_line, resolution=resolution, name=name,
                overwrite=overwrite
            )
        return time_line

    def get_company(self, buid=None):
        """

        Model.get_company() -> BusinessUnit

        Method returns model.company or a business unit with a specific bbid.
        """
        if buid:
            return self.bu_directory[buid]
        else:
            return self._company

    def get_financials(self, bbid, period):
        """

        Model.get_financials() -> Financials

        --``bbid`` is the ID.bbid for the BusinessUnit whose financials you are
         seeking
        --``period`` is an instance of TimePeriod

        Method returns the specified version of financials.
        """
        if period and bbid in period.financials:
            fins = period.financials[bbid]
        else:
            unit = self.bu_directory[bbid]
            fins = unit.get_financials(period)

        return fins

    def get_line(self, **kargs):
        """

        Model.get_line() -> LineItem

        --``bbid`` is bbid of line
        --``buid`` is BU id

        Method finds a LineItem matching the locator.
        """
        period_end = kargs['period']
        bbid = ID.from_portal(kargs['bbid']).bbid
        buid = ID.from_portal(kargs['buid']).bbid
        fins_attr = kargs['financials_attr']
        if period_end:
            key = (
                kargs.get('resolution', 'monthly'),
                kargs.get('name', 'default'),
            )
            time_line = self.timelines[key]
            if isinstance(period_end, str):
                period_end = date_from_iso(period_end)
            period = time_line[period_end]
        else:
            period = self.time_line.current_period
        financials = self.get_financials(buid, period)
        line = financials.find_line(bbid, fins_attr)
        return line

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

    def get_timeline(self, resolution='monthly', name='default'):
        """

        Model.get_timeline() -> TimeLine

        --``resolution`` is 'monthly', 'quarterly', 'annually' or any available
          summary resolution'
        --``name`` is 'default', 'actual', forecast', 'budget'

        Method returns the timeline for specified resolution (if any).
        """
        key = (resolution, name)
        if key in self.timelines:
            return self.timelines[key]

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

    def populate_xl_data(self):
        """


        Model.populate_xl_data() -> None

        Method populates "xl" attributes on all line items in preparation for
        chopping.
        """
        # once all LineItems have been reconstructed, rebuild links among them
        for time_line in self.timelines.values():
            for period in time_line.iter_ordered():
                for bu in self.bu_directory.values():
                    fins = bu.get_financials(period)
                    for statement in fins.full_ordered:
                        if statement:
                            for line in statement.get_full_ordered():
                                if not line.xl.built:
                                    id = line.id.bbid.hex
                                    new_data = period.get_xl_info(id)
                                    new_data.format = line.xl.format
                                    new_data.built = True
                                    line.xl = new_data

    def prep_for_monitoring_interview(self):
        """


        Model.prep_monitoring_interview() -> None


        Function sets path for monitoring interview after projections are set.
        Function runs after pressing the "update" button on the model card.
        """
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

    def prep_for_revision_interview(self):
        """


        prep_revision_interview() -> None


        Function sets path for monitoring interview after projections are set.
        Function runs after pressing the "update" button on the model card.
        """
        # set company as target
        co = self.get_company()
        co._stage = None
        self.target = co

        # preserve existing path and set fresh BU.used and BU.stage.path
        co.archive_path()
        co.archive_used()

        # set monitoring path:
        new_line = LineItem("revision path")
        self.target.stage.path.append(new_line)

        if not self.target.stage.focal_point:
            self.target.stage.set_focal_point(new_line)

    def prep_summaries(self):
        """


        Model.prep_summaries() -> SummaryMaker


        Create a SummaryMaker instance with default timelines.
        """
        self.summary_maker = SummaryMaker(self)
        return self.summary_maker

    def register(self, bu, update_id=True, overwrite=False, recur=True):
        """


        Model.register() -> None


        Manually add unit to bu_directory and ty_directory.
        Typically will only be used by set_company()
        After the company is set, the best way to add units to a model is to run
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
                    "bu_directory already contains an object with "
                    "the same bbid as this unit. \n"
                    "unit id:         {bbid}\n"
                    "known unit name: {name}\n"
                    "new unit name:   {mine}\n\n"
                ).format(
                    bbid=bu.id.bbid,
                    name=self.bu_directory[bu.id.bbid].tags.name,
                    mine=bu.tags.name,
                )
                raise bb_exceptions.IDCollisionError(c)

        self.bu_directory[bu.id.bbid] = bu

        # Setdefault returns dict[key] if value exists, or sets dict[key]=set()
        brethren = self.ty_directory.setdefault(bu.type, set())
        brethren.add(bu.id.bbid)

        bu.relationships.set_model(self)

        if recur:
            for child_bu in bu.components.values():
                self.register(child_bu, update_id=False,
                              overwrite=overwrite, recur=recur)

    def set_company(self, company):
        """

        Model.set_company() -> None

        Method sets the company as the top-level unit.
        """
        self.bu_directory.clear()
        self.ty_directory.clear()
        self.register(company, update_id=True, overwrite=False, recur=True)
        self._company = company

    def set_timeline(
            self, time_line, resolution='monthly', name='default',
            overwrite=False
    ):
        """

        Model.set_timeline() -> None

        --``resolution`` is 'monthly', 'quarterly', 'annually' or any available
          summary resolution'
        --``name`` is 'default', 'actual', forecast', 'budget'

        Method adds the timeline for specified resolution (if any).
        """
        key = (resolution, name)
        if key in self.timelines and not overwrite:
            c = (
                "TimeLine (resolution='{}', name='{}') "
                "already exists".format(*key)
            )
            raise KeyError(c)

        time_line.resolution = resolution
        time_line.name = name

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
