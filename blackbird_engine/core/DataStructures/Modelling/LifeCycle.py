#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: LifeCycle
"""

Module defines LifeCycle class. 

====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
LifeCycle             objects that track evolution over time

====================  ==========================================================
"""




#imports
import copy
import time
import BBExceptions

from BBGlobalVariables import *

from .Equalities import Equalities
from .LifeStage import LifeStage




#globals
#n/a

#classes
class LifeCycle(Equalities):
    """

    This class contains attributes that describe the lifecycle of the real-world
    referent for certain objects (e.g., BusinessUnits).

    1) ALL TIME VALUES ARE STORED AS SECONDS.
    Periods are stored as floating point numbers of seconds. Ages or time
    periods are stored as seconds since the Epoch. All arguments passed to
    methods should be in seconds.
    
    Age may exceed time since the beginning of the Epoch (44 years), in which
    case dateBorn will be a negative floating point number. In such an event,
    the standard Python time module will be unable to convert it back to a
    local time.
    
    2) There are three default allLifeStages: growth (0-30), maturity (31-80),
    and decline(81-100). Numbers in parentheses represent starting and ending
    values for Lifecycle.percentDone associated with the lifestage. User may
    pass in their own list of Lifestage objects.

    NOTE: Drivers may rely on a known life stage set. 
    ACCORDINGLY, CARE SHOULD BE TAKEN WHEN INTRODUCING NON-DEFAULT LIFESTAGES
    TO AN OBJECT.

    3) A number of attributes appear as class-level variables that are managed
    by descriptors.
    
    The descriptors provide dynamically computed values that do no get stale and
    should not be in logical conflict with each other. Writes to such managed
    attributes are prohibited; methods should be used instead to ensure
    coherency after the update.

    Attributes that begin with a single underscore are instance-level state
    storage for the managed class-level objects.

    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================
    DATA:
    _age                  (instance-level state)
    _alive                (instance-level state)
    _born                 (instance-level state) 
    _currentLifeStageName (instance-level state)
    _currentLifeStageNumber  (instance-level state)
    _dateBorn             (instance-level state)
    _dateDied             (instance-level state)
    _dateKilled           (instance-level state)
    _dead                 (instance-level state)
    _killed               (instance-level state)
    _percentDone          (instance-level state)
    _refDate              (instance-level state)
    age                   difference btwn refDate and dateBorn
    alive                 bool
    allLifeStages         list of applicable lifeStage objects
    born                  bool
    currentLifeStageName  w/r/to allLifeStages
    currentLifeStageNumber  w/r/to allLifeStages
    dateBorn              in seconds, set as a function of age
    dateDied              in seconds, if applicable
    dateKilled            in seconds, if applicable
    dead                  bool
    killed                bool
    lifeSpan              total length of life (in seconds)
    percentDone           age / lifespan * 100
    refDate               point in time that represents the present

    FUNCTIONS:
    kill()                kill instance
    makeOlder()           reduce dateBorn
    makeYounger()         increase dateBorn
    moveForwardInTime()   increase refDate
    moveBackwardInTime()  reduce refDate
    setInitialAge()       sets age and appropriate dateBorn for refDate
    setLifeSpan()         sets lifeSpan for instance
    setLifeStages()       sets lifestages for instance
    setRefDate()          sets refDate for instance
    showLifeStages()      returns pretty string of life stages
    ====================  ======================================================
    
    """
    #class-level comparison rules:
    skipPrefixes = ["_","dyn""allLifeStages"]
    #skip instance-level state for dynamic attributes to improve accuracy (may
    #not refresh on time) and speed. 
    
    def __init__(self,age = None, lifeSpan = None, allLifeStages = "default"):
        self.lifeSpan = lifeSpan
        if allLifeStages == "default":
            stage1 = LifeStage(stageName="growth",
                               stageStarts=0,stageEnds=30)
            stage1.makeFirst()
            stage2 = LifeStage(stageName = "maturity",
                               stageStarts = 31, stageEnds = 80)
            stage3 = LifeStage(stageName = "decline",
                               stageStarts = 81, stageEnds = 100)
            stage3.makeLast()
            self.allLifeStages = [stage1, stage2, stage3]
        else:
            self.allLifeStages = allLifeStages  
        #instance state attributes for class-level dynamically managed
        #attributes follow:
        self._refDate = None
        self._age = None
        self._percentDone = None
        self._born = False
        self._alive = False     
        self._killed = False
        self._dead = False
        self._dateBorn = None
        self._dateKilled = None
        self._dateDied = None
        self._currentLifeStageName = None
        self._currentLifeStageNumber = None
        if age:
            self.setInitialAge(age)
        if lifeSpan:
            self.setLifeSpan(lifeSpan)
            self.percentDone

    class dynRefDateManager():
        def __get__(self,instance,owner):
            return instance._refDate

        def __set__(self,instance,value):
            comment = "refDate is a managed attribute, write prohibited."
            raise BBExceptions.ManagedAttributeError(comment)

    refDate = dynRefDateManager()

    def setRefDate(self,refDate):
        """

        LifeCycle.setRefDate(refDate) -> None

        instance.refDate specifies the point in time that counts as the present.
        date values greater than refDate are then the future; those less than
        the refDate are the past. 

        Method sets instance._refDate to refDate. refDate should be in seconds
        since Epoch.
        """
        self._refDate = refDate

    def setInitialAge(self, newAge = 0, refDate = None):
        """

        LifeCycle.setInitialAge([newAge=0,][refDate=None]) -> None

        Method sets instance's newAge, refDate, and dateBorn to satisfy the
        following (intuitive) condition:
          dateBorn + age = refDate

        All date inputs should be in seconds. 

        If ``refDate`` is None, method will use the UMT value at time of call
        (time.time()). As a result, every object will have a unique refDate
        by default (unless the operation is faster than the system clock
        resolution). 

        When building out a population of peer objects, users should fix the
        refDate externally and provide it as a constructor.
        
        This method should generally be used once per object, to commit it to
        some timeline. Thereafter, the object can move along the timeline, which
        would change .refDate The object's dateBorn would stay the same and age
        would change accordingly. The object would then evolve as specified
        elsewhere in its construction.
        """
        #Generally shouldn't feed in a negative number here
        if not refDate:
            refDate = time.time()
        self.setRefDate(refDate)
        self._dateBorn = self.refDate-newAge

    class dynamicAgeManager():
        """

        Descriptor object that manages the .age class-level attribute.
        The age of an object is the arithmetic difference between the object's
        ``refDate`` and ``dateBorn``. On get calls, the descriptor updates the
        instance's ._age attribute.
        
        Direct write is prohibited.        
        """
        def __get__(self,instance,owner):
            #routes LifeCycle.age to instance._age
            try:
                updatedAge = instance.refDate - instance._dateBorn
            except (TypeError,AttributeError):
                updatedAge = None
            instance._age = updatedAge
            return instance._age

        def __set__(self,instance,value):
            raise BBExceptions.ManagedAttributeError("Use methods to adjust LifeCycle.age")

    #age is a class-level attribute of LifeCycle objects that references an
    #instance of the descriptor.
    age = dynamicAgeManager()

    def setLifeSpan(self, newLifeSpan = 0):
        """

        LifeCycle.setLifeSpan([newLifeSpan = 0]) -> None

        Method sets an instance's lifespan to the specified value. Value must be
        greater than zero and should be enumerated in seconds. 
        """
        self.lifeSpan = newLifeSpan

    class dynamicPercentDone:
        """

        Descriptor that enables dynamic computation of an instance's completion
        level for its lifespan, in percent (``percentDone``).

        percentDone = int(age / lifeSpan * 100)

        percentDone can be negative (pre-birth) or greater than 100 (after
        death).
        
        Descriptor returns None on errors or if instance age or lifespan not
        properly defined. 

        Direct write to LifeCycle.percentDone prohibited and results in an error.
        """
        def __get__(self, instance, owner):
            result = None
            if instance.lifeSpan:                
                try:
                    result = int(instance.age/instance.lifeSpan*100)
                    instance._percentDone = result       
                except ValueError:
                    #runs if there are any errors during the attempted computation
                    #(e.g., because age or lifeSpan still have default None values)
                    pass
            return result
                        
        def __set__(self,instance,value):
            comment = "LifeCycle.percentDone is a managed attribute."
            raise BBExceptions.ManagedAttributeError(comment)

    #class attribute, references an instance of the dynamicPercentDone descriptor
    #above
    percentDone = dynamicPercentDone()

    def makeOlder(self, increment = 2592000):
        """

        LifeCycle.makeOlder([increment=2592000]) -> None
        
        Method decreases instance's ``dateBorn`` by the increment. Increment
        should be specified in seconds. Default increment value is number of
        seconds in 30 days. 

        If increment is not positive, raises LifeCycleError.
        """
        if increment <= 0:
            raise BBExceptions.LifeCycleError("Must specify a positive time increment.")
        self._dateBorn = self.dateBorn - increment
        #must set the underscore attribute, because non-underscore is
        #managed and write-prohibited
        
    def makeYounger(self, increment = 2592000):
        """

        LifeCycle.makeOlder([increment=2592000]) -> None
        
        Method increases instance's ``dateBorn`` by the increment. Increment
        should be specified in seconds. Default increment value is number of
        seconds in 30 days. 

        If increment is not positive, raises LifeCycleError.
        """
        if increment <= 0:
            raise BBExceptions.LifeCycleError("Must specify a positive time increment.")
        self._dateBorn = self.dateBorn + increment
        #must set the underscore attribute, because non-underscore is
        #managed and write-prohibited

    def kill(self,date=None):
        """

        LifeCycle.kill([date=None]) -> None

        Method that turns objects that are alive into objects that are dead. If
        object is not alive, running the method will not change any of the
        object's attributes.

        If date not specified, method uses time at call. 
        """
        if self.alive:
            #change instance-level attributes (underscore names). should only be
            #changing non-underscore class values through methods
            self._alive = False
            self._killed = True
            self._dead = True
            if date:
                self_dateKilled = date
            else:
                self._dateKilled = time.time()
            self._dateDied = self._dateKilled

    def moveForwardInTime(self, increment = 2592000):
        """

        LifeCycle.moveForwardInTime([increment=2592000]) -> None

        Method increases the instance's refDate by the increment. Increment
        should be specified in seconds. Default increment value is number of
        seconds in 30 days.

        Raises LifeCycleError if increment is not positive.
        """
        if increment <= 0:
            raise BBExceptions.LifeCycleError("Must specify a positive time increment.")
        hiRefDate = self.refDate + increment
        self.setRefDate(hiRefDate)

    def moveBackwardInTime(self, increment = 2592000):
        """

        LifeCycle.moveBackwardInTime([increment=2592000]) -> None

        Method decreases the instance's refDate by the increment. Increment
        should be specified in seconds. Default increment value is number of
        seconds in 30 days.

        Raises LifeCycleError if increment is not positive.
        """
        if increment <= 0:
            raise BBExceptions.LifeCycleError("Must specify a positive time increment.")
        lowRefDate = self.refDate - increment
        self.setRefDate(lowRefDate)

    def setLifeStages(self, stages): 
        """

        LifeCycle.setLifeStages(stages) -> None

        ``stages`` should be a container of lifecycle objects. Method sets
        instance.allLifeStages to a deep copy of stages (to prevent
        forced cross-referencing).

        If looking to force references to one set of mutable lifecycle objects
        (i.e., to bind a population to a uniform lifecycle), modify
        attribute directly. 
        """
        self.allLifeStages = copy.copy(stages)

    def showLifeStages(self):
        """

        LifeCycle.showLifeStages() -> view

        View is a string showing __str__ for each lifeStage
        """
        view = ""
        for stage in self.allLifeStages:
            view = view + str(stage)
        return view
    
    class dynLifeManager:
        """

        Descriptor that maintains logical consistency across status attributes.
        
        NOTE: This descriptor NEVER sets "_born" or "_killed."
        This descriptor also generally does not set timestamps, except when the
        object dies a "natural death" (its age exceeds its lifeSpan).

        Each instance of the descriptor requires the user to specify a target
        attribute that the descriptor will manage. On __get__, descriptor will
        return the instance level state of the underscore version of the target
        attribute (instance._killed for targetAttribute = "killed").

        The descriptor runs through conforming logic for all managed names on
        every get call. 

        Direct writes to managed attributes are prohibited and return an error. 
        """    
        def __init__(self,targetAttribute):
            self.targetAttribute = targetAttribute
            self.references = {}
            
        def __get__(self,instance,owner):
            #Alignment logic based on assumption that ._born, age, lifespan, and
            #._killed are independently specified. 
            if instance.age == None or instance.age < 0:
                pass
            else: 
                instance._born = True
                if instance.lifeSpan == None:
                    if instance._killed != True:
                        instance._alive = True
                        instance._dead = False
                        #age is at or above 0, and instance hasn't been killed
                        #therefore, it must be alive and not dead,
                        #because there is no natural end of life (lifespan
                        #unspecified)
                    else:
                        pass
                        #Lifestages don't exist because the instance is dead and
                        #no lifespan anyways.
                        #
                        #Summary: without a specified lifespan, only way an
                        #instance that's been born can die is through a kill()
                else:
                    #lifeSpan defined, age > 0, object born, need to check other
                    #status: has it died (naturally or from killing) 
                    if instance._killed:
                        instance._currentLifeStageName = None
                        instance._currentLifeStageNumber = None
                        #someone ran kill() method, which aligns most status
                        #attributes on its own
                    else:
                        if instance.percentDone <= 100:
                            instance._alive = True
                            instance._dead = False
                            for stage in instance.allLifeStages:
                                if stage.starts <= instance.percentDone <= stage.ends:
                                    instance._currentLifeStageName = stage.name
                                    instance._currentLifeStageNumber = instance.allLifeStages.index(stage)
                                    break
                        else:
                            #instance exceeded 100% of lifespan
                            instance._alive = False
                            instance._dead = True
                            instance._dateDied = instance._dateBorn + instance.lifeSpan
                            instance._currentLifeStageName = None
                            instance._currentLifeStageNumber = None
            tAttr = "_" + self.targetAttribute
            tStatus = getattr(instance,tAttr)
            return tStatus
 
        def __set__(self,instance,value):
            comment = "managed attribute, write prohibited."
            raise BBExceptions.ManagedAttributeError(comment)
        
    #create class-level attributes to be managed by the dynLifeManager
    #descriptor; construct each instance of the descriptor to return the right
    #targetAttribute
    born = dynLifeManager(targetAttribute = "born")
    alive = dynLifeManager(targetAttribute = "alive")
    killed = dynLifeManager(targetAttribute = "killed")
    dead = dynLifeManager(targetAttribute = "dead")
    dateBorn = dynLifeManager(targetAttribute = "dateBorn")
    dateKilled = dynLifeManager(targetAttribute = "dateKilled")
    dateDied = dynLifeManager(targetAttribute = "dateDied")
    currentLifeStageName = dynLifeManager(targetAttribute = "currentLifeStageName")
    currentLifeStageNumber = dynLifeManager(targetAttribute = "currentLifeStageNumber")
