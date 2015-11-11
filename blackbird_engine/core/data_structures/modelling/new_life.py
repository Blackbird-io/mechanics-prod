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
import datetime

import BBExceptions as bb_exceptions

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

    DEFAULT_GESTATION     timedelta, 365 days
    DEFAULT_LIFE_SPAN     timedelta, 50 years
    DEFAULT_GROWTH_PERCENT    number, 30 percent
    DEFAULT_DECLINE_PERCENT   number, 30 percent 
    
    age                   timedelta; ref_date minus birth
    alive                 bool; True if ref_date in [birth, death)
    percent               int; age divided by span
    ref_date              timedelta; reference time point for status
    span                  timedelta; time between birth and death

    FUNCTIONS:
    set_age()             creates appropriate birth event and optionally others
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
    DEFAULT_GESTATION = datetime.timedelta(365)
    DEFAULT_LIFE_SPAN = datetime.timedelta(18250)
    # Default life span is ~50 years: 365 * 50 = 18250 days
    
    DEFAULT_GROWTH_PERCENT = 0.30
    # Assume first 30% of life is spent on growth
    DEFAULT_DECLINE_PERCENT = 0.30
    # Assume last 30% of life is spent in decline
    
    def __init__(self):
        self._birth_event_names = {KEY_BIRTH}
        self._death_event_names = {KEY_DEATH}
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

        options = {self.events[k] for k in self._death_events}
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
        

        Time between birth and death. Setter will change death date.
        """
        result = None
        expected_death = self._clock_stops
        birth = self._clock_starts
        if expected_death:
            result = death - birth

    @span.setter(self):
    def span(self, value): 
        birth = self._clock_start
        self.events[self.KEY_DEATH] = birth + value

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

    def set_age(self, time_alive, as_of_date, set_all=True):
        """


        Life.set_age() -> None


        Set birth so instance has age == time_alive when ref_date == as_of_date.
        If set_all==True, set other standard events as well. 
        """
        self.set_ref_date(as_of_date)

        date_of_birth = self.ref_date - time_alive
        self.events[self.KEY_BIRTH] = date_of_birth
        
        if set_all:
            if not self.span:
                self.span = self.DEFAULT_LIFE_SPAN
                # Span will automatically set the date of death
                
            self.events[self.KEY_CONCEPTION] = (
                date_of_birth - self.DEFAULT_GESTATION)

            self.events[self.KEY_MATURITY] = (
                date_of_birth + (self.span * self.DEFAULT_GROWTH_PERIOD))

            self.events[self.KEY_OLD_AGE] = (
                self.events[self.KEY_DEATH] - (self.span * self.DEFAULT_DECLINE_PERIOD))

    
        
