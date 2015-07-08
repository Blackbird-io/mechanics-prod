#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: DataStructures.Modelling.LifeCycle.
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
LifeCycle             object that tracks how attributes evolve over time
====================  ==========================================================
"""




#imports
import copy
import time

import BBExceptions
import BBGlobalVariables as Globals

from .Equalities import Equalities
from .Stages import Stages
from .LifeStage import LifeStage




#globals
#n/a

#classes
class LifeCycle(Equalities):
    """

    The LifeCycle class represents how an object develops over time.

    Blackbird shows ``age`` with respect to an instance's date_of_birth,
    regardless of whether the ref_date is before or after the date of birth
    (i.e., whether the date of birth is projected or actual).
    
    Blackbird does not differentiate between ``projected`` and ``actual`` dates:
    dates have the same validity whether they are larger or smaller than an
    instance's ref_date. 

    Blackbird uses the convention that life begins at birth. Accordingly,
    instances of LifeCycle will only show non-None percent completion and life
    stages after their date of birth. In Blackbird, an object is not alive
    during gestation: ``gestating`` is a status distinct from ``alive``.
    
    Blackbird uses the convention that an object can die any time after
    conception. If a caller ``kills`` an instance during gestation, that
    instance will become dead (instance.dead == True) without ever having been
    alive.
    
    LifeCycle object store all time values as an integer POSIX timestamp: number
    of seconds since Jan. 1, 1970.  All LifeCycle periods include the lower bound
    and exclude the upper bound.

    The LifeCycle class supports equivalence comparisons through the Equalities
    mix-in class.

    LifeCycle equivalence analysis runs across all properties and ignores
    attributes beginning with "_" (see skipPrefixes). The comparison of two
    LifeCycle objects will thus come out equal if they have identical state at
    the current point in time (including life stage name), even if their state
    will diverge at other points in time because they have different life stage
    patterns. 
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================
    
    ``TD`` means datetime.timedelta
    
    DATA:
    _date_of_conception   date; local state, date when work on obj begins
    _date_of_death        date; local state, min(date killed, dob + span)
    _gestation            TD; local state, seconds btwn conception and birth 
    _ref_date             date; local state, obj shows status w/r/to this moment
    _span                 TD >= 0; local state, maximum obj life span
    _stages               Stages instance; covers birth to death for max life
    #
    age                   TD: in [gestation * -1, span); P, get ref minus dob
    alive                 bool; P, get True iff ref date in [birth, death)
    churn                 num; rate of cancellations per segment
    gestating             bool; P, get True iff ref date in [conception, birth)
    gestation             TD; P, get _gestation, set for int [0, max)
    date_of_birth         date; P, get doc + gestation
    date_of_conception    date; P, get _doc, set for int [min, max)
    date_of_death         date; P, get _dod
    dead                  bool; P, True iff doc < dod < ref_date
    lead                  TD; period to locate or create unit
    mean                  TD; average life span for population
    ref_date              date; P, get _ref_date
    percent               int; P, int(age / life_span * 100)
    segment               TD; contract or other term when status changes
    skipPrefixes          list; CLASS attribute, configures equivalence checks
    sigma                 TD; standard deviation of sample from mean age
    span                  TD; P, get _span, set for int [0, max)
    stage                 str; P, name of current stage    

    FUNCTIONS:
    copy()                returns a new instance with a dict-copy of _stages
    kill()                set date of death to argument or ref_date
    set_age()             set conception date from age and ref
    set_ref_date()        set ref_date to timestamp argument
    ====================  ======================================================

    ``P`` indicates attributes decorated as properties. See attribute-level doc
    string for more information.
    """

    #Customize Equality comparison rules; compare properties only, skip instance
    #state. Alternatively, can check only _attributes, excluding _stages, and
    #``stage``. Equivalence for LifeCycle objects requires that the object's
    #current state look identical, but permits differences at other points in
    #time (ie, different pattern of life stages). 
    skipPrefixes = ["_"]
                            
    def __init__(self):
        self._date_of_conception = None
        self._date_of_death = None
        self._gestation = copy.copy(Globals.gestation_period_def)
        self._ref_date = None
        self._span = copy.copy(Globals.life_span_def)
        self._stages = Stages()
        #
        for (name, start) in Globals.default_life_stages:
            new = LifeStage(name, start)
            self._stages.add_stage(new)
        #
        self.churn = None
        self.lead = None
        self.mean = None
        self.sigma = None
        self.segment = None

    @property
    def age(self):
        """


        **read-only property**


        datetime.timedelta object expressing instance age.

        Property computes age as the difference between ref_date and
        date_of_birth. 

        Only objects with a ref_date greater than date_of_conception and less
        than date_of_death have a valid age. In other words, objects only have
        an age between conception and death. 
        """
        result = None
        if self.date_of_conception <= self.ref_date < self.date_of_death:
            result = self.ref_date - self.date_of_birth
        return result

    @property
    def alive(self):
        """


        **read-only property**


        Property returns True if ref_date is larger than date_of_birth for the
        instance, and less than date_of_death (if one exists for the instance).

        False otherwise. 
        """
        result = False
        if self.date_of_birth <= self.ref_date:
            result = True
        if self.date_of_death:
            if self.date_of_death < self.ref_date:
                result = False
        #
        return result

    @property
    def date_of_birth(self):
        """


        **read-only property**


        Property returns date that is ahead of instance conception by the
        instance gestation. 
        """
        result = self.date_of_conception + self.gestation
        return result
    
    @property
    def date_of_conception(self):
        """


        **property**


        Property returns instance _date_of_conception.

        Property setter accepts values between Globals.conception_date_min and
        Globals.conception_date_max, in seconds. Setter raises LifeCycleError
        otherwise.

        Setter sets date to nearest integer.
        """
        return self._date_of_conception

    @date_of_conception.setter
    def date_of_conception(self, value):
        if Globals.conception_date_min <= value < Globals.conception_date_max:
            self._date_of_conception = value
        else:
            c = "Conception must occur in [%s, %s)."
            c = c % (Globals.conception_date_min, Globals.conception_date_max)
            raise BBExceptions.LifeCycleError(c)
        
    @property
    def date_of_death(self):
        """


        **read-only property**


        Property returns pre-existing _date_of_death, or, if none exists,
        computes the expected date of death (sum of dob and span), sets
        _date_of_death to the expected value, and then returns the same.
        """
        if not self._date_of_death:
            #instance.kill() can force a value for _dod
            if all([self.ref_date, self.date_of_birth, self.span]):
                expected_dod = self.date_of_birth + self.span
                self._date_of_death = expected_dod
        #
        return self._date_of_death
    
    @property
    def dead(self):
        """


        **read-only property**


        Property returns True for instances where date of death is larger than
        or equal to date of conception and the ref date is equal to or larger
        than the date of death (conception <= death <= ref).

        NOTE: If object is killed during gestation, it will be dead without
        having ever been alive.
        """
        #
        #can only be dead with a defined date_of_death
        #
        result = False
        if self.date_of_conception and self.date_of_death:
            if self.date_of_conception <= self.date_of_death:
                if self.date_of_death <= self.ref_date:
                    result = True
                #
            #
        return result

    @property
    def gestating(self):
        """


        **read-only property**


        Property returns True iff instance ref_date is between conception and
        birth and instance has not yet died.        
        """
        result = False
        if self.date_of_conception <= self.ref_date < self.date_of_birth:
            result = True
        if result:
            if self.date_of_death <= self.ref_date:
                result = False
            #correct result if instance died before ref_date;
        #
        return result

    @property
    def gestation(self):
        """


        **property**


        Property returns instance._gestation state. By default, instances have
        a gestation period

        Setter accepts datetime.timedelta values in (0, Globals.gestation_max).
        Setter raises LifeCycleError otherwise.
        """
        return self._gestation

    @gestation.setter
    def gestation(self, value):
        if Globals.gestation_period_min <= value < Globals.gestation_period_max:
            self._gestation = value
        else:
            c = "Gestation must be a timedelta object in [%s, %s)."
            c = c % (Globals.gestation_period_min,
                     Globals.gestation_period_max)
            raise BBExceptions.LifeCycleError(c)

    @property
    def percent(self):
        """


        **read-only property**


        Property returns age divided by span, multiplied by 100 and rounded to
        the nearest integer. 
        """
        result = None
        #
        if all([self.age, self.span]):
            result = (self.age / self.span) * 100
            result = round(result)
        #
        return result
    

    @property
    def ref_date(self):
        """


        **read-only property**


        Property returns _ref_date.
        """
        return self._ref_date

    @property
    def span(self):
        """


        **property**


        Property returns instance life span in seconds. By default, instance
        life span is set to Globals.life_span_years_def.

        Property setter accepts timedelta-type values between min and max
        defined in Globals. Setter raises LifeCycleError otherwise.
        """
        return self._span

    @span.setter
    def span(self, value):
        if Globals.life_span_min <= value < Globals.life_span_max:
            self._span = value
        else:
            c = "Life span must be a timedelta object in [%s, %s)."
            c  = c % (Globals.life_span_min.days,
                      Globals.life_span_max.days)
            raise BBExceptions.LifeCycleError(c)
        
    @property
    def stage(self):
        """


        **read-only property**


        Property returns name of stage that covers current point in life,
        measured by percent completion.        
        """
        result = None
        current = self._stages.find_stage(self.percent)
        if current:
            result = current.get("name")
        return result
    
    def copy(self):
        """


        LifeCycle.copy() -> LifeCycle


        Method returns a new LifeCycle object. Result is a shallow copy of
        instance with a dict-specific deep copy of ``_stages``.
        """
        result = copy.copy(self)
        result._stages = self._stages.copy()
        return result

    def kill(self, new_dod = None):
        """


        LifeCycle.kill(new_dod) -> None


        Method sets date of death for instance to argument. If ``new_dod``
        is not True, method uses instance ref_date. Method raises error if
        instance does not specify a True ref_date. 
        """
        if not new_dod:
            if self.ref_date:
                new_dod = self.ref_date
            else:
                c = "kill() requires valid date of death or instance ref_date."
                raise BBExceptions.LifeCycleError(c)
        #
        self._date_of_death = new_dod
        #

    def set_age(self, fixed_age, ref_date):
        """


        LifeCycle.set_age(fixed_age, ref_date) -> None

        Method expects:
        -- ``fixed_age`` to be a timedelta object
        -- ``ref_date`` to be a date object

        Method computes a date of conception that generates the desired age
        at ref_date and sets instance properties accordingly.
        """
        self._ref_date = ref_date
        estimated_conception = ref_date - fixed_age - self.gestation
        self.date_of_conception = estimated_conception
        
    def set_ref_date(self, new_ref):
        """


        LifeCycle.set_ref_date(new_ref) -> None


        Method sets instance ref date to ``new_ref``. Method expects
        ``new_ref`` to be a datetime object.  
        
        Method raises LifeCycleError if new_ref falls outside of [earliest,
        latest) range specified in Globals.
        """
        #
        if Globals.ref_date_min <= new_ref < Globals.ref_date_max:
            self._ref_date = new_ref
        else:
            c = "Object requires a date in [%s, %s)."
            c = c % (Globals.ref_date_min.isoformat(),
                     Globals.ref_date_max.isoformat())
            raise BBExceptions.LifeCycleError(c)
    
    

    
        
