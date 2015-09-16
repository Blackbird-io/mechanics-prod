#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: Model
"""

Module defines Model class.

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

from DataStructures.Analysis.BusinessSummary import BusinessSummary
from DataStructures.Guidance.Guide import Guide
from DataStructures.Guidance.interview_tracker import InterviewTracker
from DataStructures.Platform.ID import ID
from DataStructures.Platform.Tags import Tags

from .Header import Header
##from .Taxonomy import Taxonomy
from .TimeLine import TimeLine




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
    path                  property; dynamic pointer to interview or other path
    portal_data           dict; stores data from Portal related to the instance
    started               bool; property, tracks whether engine has begun work
    summary               dict or obj; instance of BusinessSummary
    taxonomy              Taxonomy; collection of prototypical business units
    time_line              list of TimePeriod objects

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
        self.summary = BusinessSummary()
        self.taxonomy = dict()
        self.transcript = []
        self.time_line = TimeLine()
        self.used = set()
        #
        self.time_line.id.setNID(self.id.namespace_id)

    class dyn_current_manager:
        def __get__(self,instance,owner):
            return instance.time_line.current_period

        def __set__(self,instance,value):
            c = ""
            c += "Model.currentPeriod is a write-only attribute. Modifications"
            c += "\nmust go through Model.time_line"            
            raise BBExceptions.ManagedAttributeError(c)

    currentPeriod = dyn_current_manager()

    @property
    def stage(self):
        """
        pass-through at first, otherwise points to where you want to
        """
        result = self._stage
        if result is None:
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
        "``started`` property; once True, difficult to undo."
        return self._started

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

        result = self._path
        if result is None:
            result = self.interview.path
        return result

    @path.setter
    def path(self, value):
        self._path = value

    @path.deleter
    def path(self):
        self._path = None

    @property
    def started(self):
        """


        **read-only property**


        Property returns instance _path when that attribute points to a True
        object, or instance.interview.path otherwise.

        Since the default value for instance._path is None, property starts out
        by pointing to interview.path and switches only if someone affirmatively
        sets it to a different referent.
        
        Setter sets path to value.
        """
        return self._started
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
    
        

