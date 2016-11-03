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
from chef_settings import DEFAULT_SCENARIOS
from data_structures.system.bbid import ID
from data_structures.system.tags_mixin import TagsMixIn
from .time_line import TimeLine


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
    taxonomy              dict with tree of unit templates
    time_line             list of TimePeriod objects
    transcript            list of entries that tracks Engine processing
    valuation             P; pointer to current period valuation

    FUNCTIONS:
    change_ref_date()     updates timeline to use new reference date
    copy()                returns a copy of Model instance
    from_portal()         class method, extracts model out of API-format
    get_company()         method to get top-level company unit
    get_financials()      method to get financials for a given unit and time
    get_life()            method to get unit life at a given time
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
        #
        self.id = ID()
        self.id.assign(name)
        # Models carry uuids in the origin namespace.
        self.portal_data = dict()
        self.taxonomy = dict()
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


        Pointer to company summary on current period. If current period has no
        content, returns None.
        """
        result = None
        #
        company = self.time_line.current_period.content
        if company:
            # catch periods with empty content
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


        Pointer to company valuation on current period. If current period has no
        content, returns None.
        """
        result = None
        #
        company = self.time_line.current_period.content
        if company:
            # catch periods with empty content
            result = company.valuation
        #
        return result

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

        old_tl = self.get_timeline()

        new_tl = TimeLine(self)
        new_tl.parameters = self.time_line.parameters.copy()
        new_tl.master = self.time_line.master.copy()
        new_tl.build(ref_date=ref_date)
        new_tl.id.set_namespace(self.id.bbid)
        new_tl.current_period.set_content(old_tl.current_period.content)

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
        result._started = self._started
        result.portal_data = self.portal_data.copy()
        result.taxonomy = self.taxonomy.copy()
        result.transcript = self.transcript.copy()
        for key, time_line in self.timelines.items():
            new_tl = time_line.copy()
            new_tl.model = result
            result.set_timeline(new_tl, *key)
        result.scenarios = self.scenarios.copy()
        result.target = self.target

        return result

    def get_company(self):
        """

        Model.get_company() -> BusinessUnit

        Method returns top-level business unit from current period.
        """
        co = self.time_line.current_period.content
        return co

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

    def get_life(self, bbid, period):
        """

        Model.get_life() -> Life

        --``bbid`` is the ID.bbid for the BusinessUnit whose financials you are
         seeking
        --``period`` is an instance of TimePeriod or TimePeriodBase

        Method returns the specified version of Life.
        """
        unit = period.bu_directory[bbid]
        life = unit.life

        return life

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
