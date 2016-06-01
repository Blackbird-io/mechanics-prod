#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: data_structures.modelling.life
"""

Module defines Life class, a significantly streamlined tool for tracking
business evolution over time. Life events are largely compatible with legacy
topics.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
Life                  object that tracks how attributes evolve over time
====================  ==========================================================
"""




#imports
import copy
import datetime

import bb_exceptions

from . import common_events
from .equalities import Equalities




#constants
#n/a

#classes
class Life(Equalities):
    """

    To paraphrase Yogi Berra, life is just one thing after another.

    This class aimed to significantly simplify the old LifeCycle concept.
    Accordingly, it strips out most value management and leaves its data
    largerly exposed. Topics can thus record events freely and drivers /
    formulas can run their own evaluations of those events.

    All event values should be in datetime.date. All duration inputs should
    be timedelta objects. 

    Rules for a good life:
    
    1. Keep your keys consistent; use those on class or in common_events
    2. Your life span will change if you die suddenly
    3. You can use configure_events() to quickly build a common trajectory
    4. You can manually change or add events to customize the object
    5. Life won't catch your mistakes if, for example, you reach old age before
       maturity. That's just going to mean your object fits in poorly elsewhere
       in the ecosystem.

    Sample use case 1:
      GOAL: Configure a template unit for model taxonomy
      >>>...
      >>>store_template.LIFE_SPAN = datetime.timedelta(20*365)
      >>>store_template.set_gestation(datetime.timedelta(1.5*365))
      >>>store_template.set_percent_maturity(0.15)

      Now, when you want to represent a specific unit:
      >>>uws = store_template.copy()
      >>>uws.configure_events(date_of_birth=datetime.date(1920,04,01)

    Sample use case 2:
      GOAL: Renovate a store to extend its lifespan
      >>>...
      >>>today = datetime.date(2020, 6, 1)
      >>>chelsea.life.events[common_events.KEY_RENOVATION] = today
      >>>chelsea.life.events[chelsea.life.KEY_DEATH] = datetime.date(2040, 6, 1)

      Store will now die later but its other events won't change. You can change
      chelsea.span if you want to move all of the events along at the same time.

    Sample use case 3:
      GOAL: To simulate probabilistic churn in a population of subscribers

      This is a complex task. Each customer has a known life that matches their
      subscription. At the end of each subscription period, the customer may
      renew or not. The customer's expected life may therefore be larger than
      their known life. Each renewal period will extend the known life.

      Since we designed Life to be a simple, lightweight object, complex logic
      like this use case should generally reside in Topics. Those topics can
      implement their decisions by running:
      >>>...
      >>>long_time_subscriber.life.events[common_events.KEY_RENEWAL] = today
      >>>k_death = long_time_subscriber.life.KEY_DEATH
      >>>expected_termination = long_time_subscriber.life.events[k_death]
      >>>contract_length = datetime.timedelta(5*365)
      >>>long_time_subscriber.life.events[k_death] = expected_termination + contract_length

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
    PERCENT_MATURITY      int; where maturity begins, < OLD_AGE_PERCENT
    PERCENT_OLD_AGE       int; point where old age begins, should be < 100
    
    age                   timedelta; ref_date minus birth
    alive                 bool; True if ref_date in [birth, death)
    conceived             bool; True if conception < ref_date
    events                dict; 
    percent               int; age divided by span
    ref_date              timedelta; reference time point for status
    span                  timedelta; time between birth and death

    FUNCTIONS:
    configure_events()    add standard events to instance
    copy()                returns a deep copy
    get_latest()          get name and date for most recent event
    set_ref_date()        set instance ref date
    set_gestation()       sets custom gestation period
    set_percent_maturity()  sets custom maturity trigger
    set_percent_old_age()   sets custom old age trigger
    ====================  ======================================================
    """
    keyAttributes = ["_ref_date", "events"]
    # On calls to __eq__ and __ne__, Equalities will check only these attributes
    
    KEY_CONCEPTION = common_events.KEY_CONCEPTION
    KEY_BIRTH = common_events.KEY_BIRTH
    KEY_DEATH = common_events.KEY_DEATH

    KEY_MATURITY = common_events.KEY_MATURITY
    KEY_OLD_AGE = common_events.KEY_OLD_AGE
    # These keys should stay constant (can also add kill, renovation)
    
    # Specify default values as days for timedelta.
    GESTATION = datetime.timedelta(365)
    LIFE_SPAN = datetime.timedelta(18250)
    # Default life span is ~50 years: 365 * 50 = 18250 days
    
    PERCENT_MATURITY = 30
    # Assume maturity begins at 30 (first 30% of life spent on growth).
    PERCENT_OLD_AGE = 70
    # Assume old age begins at 70.
    
    def __init__(self):
        self._birth_event_names = {self.KEY_BIRTH}
        self._death_event_names = {self.KEY_DEATH}
        # Can modify these for advanced functionality. For example, if you
        # want your unit to be born again on a "rebranding" event.
        self._ref_date = None
        
        self.events = dict()
    
    @property
    def _clock_starts(self):
        # Return **latest** defined birth event.
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
    def conceived(self):
        """


        **read-only property**


        True if conception < ref_date, False otherwise. Generally represents
        point when an object can start affecting its environment.
        """
        result = False
        conception = self.events.get(self.KEY_CONCEPTION)
        if conception:
            if conception < self.ref_date:
                result = True
        return result
        
    @property
    def percent(self):
        """


        **read-only property**


        Quotient of age over span, multiplied by 100 and rounded to integer.
        """
        result = None
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
        old age, using PERCENT_MATURITY and PERCENT_OLD_AGE. You can specify
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
            birth + (value * self.PERCENT_MATURITY / 100)
            )

        self.events[self.KEY_OLD_AGE] = (
            birth + (value * self.PERCENT_OLD_AGE / 100)
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

        if life_span is None:
            life_span = self.LIFE_SPAN
        self.span = life_span
        # Span will automatically set the date of death, maturity, and old age.

        if gestation is None:
            gestation = self.GESTATION
        self.events[self.KEY_CONCEPTION] = date_of_birth - gestation

    def copy(self):
        """


        Life.copy() -> Life


        Return deep copy. 
        """
        # Use shallow copy to start, manually copy mutable objects (for speed).
        result = copy.copy(self)
        result._birth_event_names = self._birth_event_names.copy()
        result._death_event_names = self._death_event_names.copy()
        result.events = self.events.copy()
        
        return result

    def get_latest(self, ref_date=None):
        """


        Life.get_latest() -> (string, datetime.date)


        Return name and date for most recent event. Uses instance ref_date by
        default.
        """
        event_name = None
        event_date = None
        
        if ref_date is None:
            ref_date = self.ref_date
        
        last_to_first = sorted(self.events.items(), key=lambda i: i[1], reverse=True)

        for event_name, event_date in last_to_first:
            if event_date <= ref_date:
                break
            else:
                continue
            
        return (event_name, event_date) 

    def set_gestation(self, value):
        """


        Life.set_gestation() -> None


        Set custom gestation period. Expects timedelta.
        """
        self.GESTATION = value
        
    def set_percent_maturity(self, value):
        """


        Life.set_percent_maturity() -> None


        Set custom maturity trigger as percent of life. Expects float in [0,1].
        """
        self.PERCENT_MATURITY = value

    def set_percent_old_age(self, value):
        """


        Life.set_percent_old_age() -> None


        Set custom old age trigger as percent of life. Expects float in [0,1].
        """
        self.PERCENT_OLD_AGE = value

    

    
        
