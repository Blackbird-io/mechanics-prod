#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: data_structures.modelling.model
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




#imports
import time
import dill

import BBExceptions
import BBGlobalVariables as Globals

from data_structures.guidance.guide import Guide
from data_structures.guidance.interview_tracker import InterviewTracker
from data_structures.system.bbid import ID
from data_structures.system.tags import Tags

from .header import Header
##from .taxonomy import Taxonomy
from .time_line import TimeLine




#globals
#n/a

#classes
class Model(Tags):
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
    _stage                obj; instance-level state for ``stage``
    _started              bool; instance-level state for ``started`` property
    currentPeriod         pointer to timeline period that covers reference date
    guide                 instance of Guide object
    header                instance of Header object
    id                    instance of ID object, carries bbid for model 
    interview             instance of an InterviewTracker object 
    portal_data           dict; stores data from Portal related to the instance
    stage                 P; pointer to either interview or defined _stage
    started               bool; property, tracks whether engine has begun work
    summary               P; pointer to current period summary
    taxonomy              Taxonomy; collection of prototypical business units
    time_line             list of TimePeriod objects
    transcript            list of entries that tracks Engine processing
    used                  set of bbids for used topics
    valuation             P; pointer to current period valuation

    FUNCTIONS:
    from_portal()         class method, extracts model out of API-format
    start()               sets _started and started to True
    transcribe()          append message and timestamp to transcript
    ====================  ======================================================
    
    ``P`` indicates attributes decorated as properties. See attribute-level doc
    string for more information.
    
    """
    def __init__(self, name):
        Tags.__init__(self,name)
        self._stage = None
        self._started = False
        self.guide = Guide()
        self.header = Header()
        self.id = ID()
        self.id.assignBBID(name)
        #Model uuids exist in the origin namespace
        self.interview = InterviewTracker()
        self.portal_data = dict()
        self.taxonomy = dict()
        self.transcript = []
        self.time_line = TimeLine()
        self.used = set()
        #
        self.time_line.id.setNID(self.id.namespace_id)

    #DYNAMIC ATTRIBUTES
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
            #catch periods with empty content
            result = company.summary
        #
        return result

    @summary.setter
    def summary(self, value):
        c = "Assignment prohibited. ``model.summary`` serves only as a pointer"
        c += " to the current period company summary."
        raise BBExceptions.ManagedAttributeError(c)

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
            #catch periods with empty content
            result = company.valuation
        #
        return result

    @valuation.setter
    def valuation(self, value):
        c = "Assignment prohibited. ``model.valuation`` serves only as a pointer"
        c += " to the current period company valuation."
        raise BBExceptions.ManagedAttributeError(c)

    #METHODS
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
        M = None
        flat_model = portal_model["e_model"]
        #
        if flat_model:
            M = dill.loads(flat_model)
        else:
            business_name = portal_model["business_name"]
            if not business_name:
                business_name = Globals.default_model_name
            M = cls(business_name)
        M.portal_data.update(portal_model)
        del M.portal_data["e_model"]
        return M
    
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
        record = (message,time_stamp)
        self.transcript.append(record)
    
        

