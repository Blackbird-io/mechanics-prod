#re_birth
#
#renovation
#renewal
##renewal has a certain probabiliy (1- churn)
##how do you build in that logic?
##could have drivers?

##basically, probabilistic events are challenging
##challenging because its probabilistic?
##or challenging because its logic?
##may be i should have drivers for this too
##
##the other challenge is that you should ideally adjust this
##externally
##
##but to do that, you may need to reach across time periods
##so may be you go to next:
##
##or may be you just do it in topics, where you configure life
##in discrete increments.
##
##or you have a lottery for who renews and who doesn't. 
##can then think about the difference between expected and observed

#can add kill events
#or can create a little class called LifeEvent: date, kill = True, notes
#or life_starts, life_ends
#

#

#adj life

#imports
import copy
import datetime

import BBExceptions as bb_exceptions




#constants
#n/a

#classes
class Life:
    """

    To paraphrase Yogi Berra, life is just one thing after another.

    rules:
    1. keep keys consistent ("renovation", "merger") #<----------- we should probably add them to this class every time we add one; or to shared knowledge
    2. life span will change to reflect actual death
    3. you can adjust life span and class will move death for you
    4. all event values should be datetime.date
    5. all period values should be datetime.timedelta
    6. Can modify instance _birth and _death event names for advanced functionality (e.g., to treat renovation like a new start to life)
    7. class provides automatic logic for basic life trajectory. you can add your
    own events with external logic for richer life trajectories.
    8. no longer patrols that your maturity and old age percentage kick offs make sense
    (ie, dont cross, are less than 100).

    #common use case 0: configurign template units
         set instance.LIFE_SPAN and GESTATION first
         then when you know date of birth, add that
         can easily override on 
    #common use case 1: renovation extends expected lifespan
        #manually enter a renovation event in self.events
        #then increase span by desired outcome.
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    KEY_CONCEPTION        str; recommended key for conception event
    KEY_BIRTH             str; recommended key for birth event
    KEY_DEATH             str; recommended key for death event
    KEY_MATURITY          str; recommended key for onset of maturity
    KEY_OLD_AGE           str; recommended key for onset of old age 

    GESTATION             timedelta, 365 days by default
    LIFE_SPAN             timedelta, 50 years by default
    MATURITY_PERCENT      int; where maturity begins, < OLD_AGE_PERCENT
    OLD_AGE_PERCENT       int; point where old age begins, should be < 100
    
    age                   timedelta; ref_date minus birth
    alive                 bool; True if ref_date in [birth, death)
    percent               int; age divided by span
    ref_date              timedelta; reference time point for status
    span                  timedelta; time between birth and death

    FUNCTIONS:
    configure_events()    add standard events to instance
    copy()                returns a deep copy
    set_age()             OBSOLETE (legacy interface for configure_events)
    set_ref_date()        set instance ref date
    ====================  ======================================================
    """
    #<-------------------------------------------------------------------------------------------figure out situation with equality; can mix in for now, and go from there
    # Alternative equality solution: compare only age and ref_date. Or can compare percent too. 
    
    KEY_CONCEPTION = "conception"
    KEY_BIRTH = "birth"
    KEY_DEATH = "death"

    KEY_MATURITY = "maturity"
    KEY_OLD_AGE = "old age"
    # These keys should stay constant (can also add kill, renovation)
    
    # Specify default values as days for timedelta.
    GESTATION = datetime.timedelta(365)
    LIFE_SPAN = datetime.timedelta(18250)
    # Default life span is ~50 years: 365 * 50 = 18250 days
    
    MATURITY_PERCENT = 30
    # Assume maturity begins at 30 (first 30% of life spent on growth).
    OLD_AGE_PERCENT = 70
    # Assume old age begins at 70.
    
    def __init__(self):
        self._birth_event_names = {self.KEY_BIRTH}
        self._death_event_names = {self.KEY_DEATH}
        self._ref_date = None
        
        self.events = dict()
    
    @property
    def _clock_starts(self):
        # Return **latest** defined death event
        start_date = None
        defined_names = self._birth_event_names & self.events.keys()

        options = {self.events[k] for k in defined_names}
        if options:
            start_date = max(options)

        return start_date

    @property 
    def _clock_stops(self):
        # Return **earliest** defined death event
        stop_date = None
        defined_names = self._death_event_names & self.events.keys()

        options = {self.events[k] for k in defined_names}
        if options:
            stop_date = min(options)

        return stop_date

    @property
    def age(self):
        """


        **read-only property**


        Instance ref_date minus date of birth (or latest clock start event).
        """
        result = None

        date_of_birth = self._clock_starts
        if date_of_birth is not None:
            result = self.ref_date - date_of_birth
        
        return result
        
    @property
    def alive(self):
        """


        **read-only property**


        True if instance ref date is in [birth, death), False otherwise.
        """
        result = False
        birth = self._clock_starts
        death = self._clock_stops
        if death is None:
            if birth <= self.ref_date:
                result = True
        else:
            if birth <= self.ref_date < death:
                result = True
        #
        return result
    
    @property
    def percent(self):
        """


        **read-only property**


        Quotient of age over span, multiplied by 100 and rounded to integer.
        """
        if self.span is not None:
            result = (self.age/self.span) * 100
            result = round(result)
        return result

    @property
    def ref_date(self):
        """


        **read-only property**


        Reference date for instance.
        """
        return self._ref_date

    @property
    def span(self):
        """


        **property**
        

        Time between birth and death. Setter will change death, maturity, and
        old age, using MATURITY_PERCENT and OLD_AGE_PERCENT. You can specify
        your own percent thresholds for these events, or enter new dates
        directly into instance.events.
        """
        result = None
        expected_death = self._clock_stops
        birth = self._clock_starts
        if expected_death:
            result = expected_death - birth
        return result

    @span.setter
    def span(self, value): 
        birth = self._clock_starts
        death = birth + value
        
        self.events[self.KEY_DEATH] = death
        
        self.events[self.KEY_MATURITY] = (
            birth + (value * self.MATURITY_PERCENT / 100)
            )

        self.events[self.KEY_OLD_AGE] = (
            birth + (value * self.OLD_AGE_PERCENT / 100)
            )

    def set_ref_date(self, value):
        """


        Life.set_ref_date() -> None


        Set instance ref date. Will raise LifeError if value is not a date obj.
        """
        if isinstance(value, datetime.date):
            self._ref_date = value
        else:
            c = "Method expects datetime.date value."
            raise bb_exceptions.LifeError(c)

    def set_age(self, age, ref_date):
        """


        Life.set_age() -> None


        **OBSOLETE**
        
        Legacy interface for configuring events. 
        """
        self.set_ref_date(ref_date)
        birth = ref_date - age
        self.configure_events(birth)
        
    def configure_events(self, date_of_birth, life_span=None, gestation=None):
        """


        Life.configure_standard_events() -> None


        Method sets standard events based on specified or default values.
        """
        self.events[self.KEY_BIRTH] = date_of_birth

        self.span = life_span or self.LIFE_SPAN
        # Span will automatically set the date of death, maturity, and old age.

        gestation = gestation or self.GESTATION
        self.events[self.KEY_CONCEPTION] = date_of_birth - gestation

    def copy(self):
        """


        Life.copy() -> Life


        Return deep copy. 
        """
        result = copy.copy(self)
        result.events = self.events.copy()
        return result
        

    
        
