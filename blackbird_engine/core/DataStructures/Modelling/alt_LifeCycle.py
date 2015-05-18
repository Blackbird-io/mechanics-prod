#alt lifecycle
#

#figure out what methods BU.extrapolate uses.
#change LifeStage to a dict w 2 keys
#should configure default stages w youth, maturity, decline stages
#specify equality rules (all non-dash attr values?)


#imports
import BBExceptions
import BBGlobalVariables as Globals

import Tools.Parsing

from .Stages import Stages
from .LifeStage import LifeStage




#globals
seconds_from_iso = Tools.Parsing.seconds_from_iso
seconds_from_years = Tools.Parsing.seconds_from_years
#
conc_posix_max = seconds_from_iso(Globals.conception_date_max)
conc_posix_min = seconds_from_iso(Globals.conception_date_min)
#
gest_secs_def = seconds_from_years(Globals.gestation_years_def)
gest_secs_max = seconds_from_years(Globals.gestation_years_max)
#
ref_posix_max = seconds_from_iso(Globals.ref_date_min)
ref_posix_min = seconds_from_iso(Globals.ref_date_max)
#
span_secs_def = seconds_from_years(Globals.life_span_years_def)
span_secs_max = seconds_from_years(Globals.life_span_years_max)

#classes
class LifeCycle:
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
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================
    DATA:
    _date_of_conception   int; local state, POSIX date when work on obj begins
    _date_of_death        int; local state, min(date killed, dob + span)
    _gestation            int; local state, seconds btwn conception and birth 
    _ref_date             int; local state, obj shows status w/r/to this moment
    _span                 int >= 0; local state, max obj life span in seconds
    _stages               Stages instance; covers birth to death for max life
    #
    age                   float in [gestation * -1, span); P, get ref minus dob
    alive                 bool; P, get True iff ref date in [birth, death)
    gestating             bool; P, get True iff ref date in [conception, birth)
    gestation             int; P, get _gestation, set for int [0, max)
    date_of_birth         int; P, get doc + gestation
    date_of_conception    int; P, get _doc, set for int [min, max)
    date_of_death         int; P, get _dod
    dead                  bool; P, True iff doc < dod < ref_date 
    ref_date              int; P, get _ref_date
    percent               int; P, int(age / life_span * 100)
    span                  int; P, get _span, set for int [0, max)
    stage                 str; P, name of current stage    

    FUNCTIONS:
    kill()                set date of death to argument or ref_date
    set_ref_date()        set ref_date to timestamp argument
    ====================  ======================================================

    ``P`` indicates attributes decorated as properties. See attribute-level doc
    string for more information.
    """
    def __init__(self):
        self._date_of_conception = None
        self._date_of_death = None
        self._gestation = gest_secs_def
        self._ref_date = None
        self._span = span_secs_def
        self._stages = Stages()
        #
        for (name, start) in Globals.default_life_stages:
            new = LifeStage(name, start)
            self._stages.add_stage(new)

    @property
    def age(self):
        """


        **read-only property**


        Property returns the difference between ref_date and date_of_birth for
        instance. Only objects with a ref_date greater than date_of_conception
        have a valid age.
        """
        result = None
        if self.date_of_conception <= self.ref_date:
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
        if self.ref_date > self.date_of_birth:
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
        value = int(value)
        if conc_posix_min <= value < conc_posix_max:
            self._date_of_conception = value
        else:
            c = "Conception must occur in [%s, %s)."
            c = c % (Globals.conception_date_min, Globals.conception_date_max)
            raise BBExceptions.LifeCycleError(c)
        
    @property
    def date_of_death(self):
        if not self._date_of_death:
            #instance.kill() can force a value for _dod
            if all(self.ref_date, self.date_of_birth, self.span):
                expected_dod = self.date_of_birth + self.span
                if self.ref_date > expected_dod:
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

        Property setter accepts values between 0 and the seconds equivalent of
        Globals.gestation_years_max. Setter raises LifeCycleError otherwise.

        Setter always sets period to nearest integer. 
        """
        return self._gestation

    @gestation.setter
    def gestation(self, value):
        value = int(value)
        try:
            if 0 <= value < gest_secs_max:
                self._span = value
            else:
                c = "Gestation must be an integer in [0, %s)." % gest_secs_max
                raise BBExceptions.LifeCycleError(c)
        except TypeError:
            c = "Gestation must be an integer in [0, %s)." % gest_secs_max
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
        if all(self.age, self.span):
            result = (self.age / self.span) * 100
            result = int(result)
        #
        return result
    
    @property
    def span(self):
        """


        **property**


        Property returns instance life span in seconds. By default, instance
        life span is set to a value that corresponds to
        Globals.life_span_years_def.

        Property setter accepts values between 0 and the seconds equivalent of
        Globals.life_span_years_max. Setter raises LifeCycleError otherwise.

        Setter always sets period to nearest integer. 
        """
        return self._span

    @span.setter
    def span(self, value):
        value = int(value)
        try:
            if 0 <= value < span_secs_max:
                self._span = value
            else:
                c = "Life span must be an integer in [0, %s)." % span_secs_max
                raise BBExceptions.LifeCycleError(c)
        except TypeError:
            c = "Life span must be an integer in [0, %s)." % span_secs_max
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
        result = current.get("name")
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
                c = "kill() requires valid POSIX date of death or instance"
                c += " ref_date."
                raise BBExceptions.LifeCycleError(c)
        #
        self._date_of_death = new_dod
        #

    def set_ref_date(self, new_ref):
        """


        LifeCycle.set_ref_date(new_ref) -> None


        Method sets instance ref date to ``new_ref,`` rounded to the nearest
        integer. Method expects new_ref to show date as seconds since Epoch.
        Method accepts negative new_ref values for dates prior to the beginning
        of the Epoch. 
        
        Method raises LifeCycleError if new_ref falls outside of [earliest,
        latest) range specified in Globals.
        """
        new_ref = int(new_ref)
        #
        if ref_posix_min <= new_ref < ref_posix_max:
            self._ref_date = new_ref
        else:
            c = "Object requires a POSIX ref date in [%s, %s)."
            c = c % (Globals.ref_date_min, Globals.ref_date_max)
            raise BBExceptions.LifeCycleError(c)
    
    

    
        
