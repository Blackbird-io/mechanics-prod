#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: TimeLine
"""

Module defines TimeLine class. TimeLines are dictionaries of time periods with
custom search methods.

====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
TimeLine              collection of TimePeriod objects indexed by end date
====================  ==========================================================
"""




#imports
import datetime
import time
import BBExceptions
import BBGlobalVariables as Globals

from DataStructures.Platform.ID import ID

from .TimePeriod import TimePeriod




#globals
#n/a

#classes
class TimeLine(dict):
    """

    A TimeLine is a dictionary of TimePeriod objects keyed by ending date.
    The TimeLine helps manage, configure, and search TimePeriods. 

    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    current_period        period that represents a reference point in time
    id                    instance of PlatformComponents.ID class, for interface
    
    FUNCTIONS:
    addPeriod()           configures and records period, keyed by end date
    build()               populates instance with adjacent time periods
    configurePeriod()     connects period to instance namespace id     
    findPeriod()          returns period that contains queried time point
    extrapolate_all()     use seed to fill out all periods in instance
    extrapolate_dates()   use seed to fill out a range of dates
    get_fwd_start_date()  returns first date of next month
    get_red_end_date()    returns last date of current month
    getOrdered()          returns list of periods ordered by end point
    setCurrent()          sets instance.current_period to argument
    updateCurrent()       updates current_period for reference or actual date
    ====================  ======================================================
    """
    
    def __init__(self):
        dict.__init__(self)
        self.current_period = None
        self.id = ID()
        #timeline objects support the id interface and pass the model's id down
        #to time periods. the timeline instance itself does not get its own
        #bbid.

    def addPeriod(self, period):
        """


        TimeLine.addPeriod(period) -> None


        Method configures period and records it in the instance under the
        period's end_date. 
        """
        period = self.configurePeriod(period)
        self[period.end_date] = period

    def build(self, ref_in_seconds = None, fwd = 36, back = 36):
        """


        TimeLine.build([ref_in_seconds = None[, fwd = 36[, back = 36]) -> None


        Method creates a chain of TimePeriods with adjacent start and end
        points. The chain is ``fwd`` periods long into the future and ``back``
        periods long into the past.

        Method expects ``ref_in_seconds`` to be a POSIX timestamp (seconds since
        Epoch) that represents the reference date. If ``ref_in_seconds`` is left
        blank, method uses current system time (time.time()) as the ref date. 

        Method sets instance.current_period to the period covering the reference
        date.

        Method relies on ``datetime`` and ``time`` modules to manage time and
        date counts. 
        """
        #
        if not ref_in_seconds:
            ref_in_seconds = time.time()
        ref_date = datetime.date.fromtimestamp(ref_in_seconds)
        ref_month = ref_date.month
        ref_year = ref_date.year
        #
        curr_start_date = datetime.date(ref_year,ref_month,1)
        #
        #make reference period
        fwd_start_date = self.get_fwd_start_date(ref_date)
        curr_start_sec = time.mktime(curr_start_date.timetuple())
        fwd_start_sec = time.mktime(fwd_start_date.timetuple())
        curr_end_sec = fwd_start_sec - 1       
        current_period = TimePeriod(curr_start_sec, curr_end_sec)
        self.addPeriod(current_period)
        self.setCurrent(current_period)
        #
        back_end_sec = curr_start_sec - 1
        #save known starting point for back chain build before fwd changes it
        #
        #make fwd chain
        for i in range(fwd):
                #pick up where ref period analysis leaves off
                curr_start_date = fwd_start_date
                curr_start_sec = fwd_start_sec
                fwd_start_date = self.get_fwd_start_date(curr_start_date)
                fwd_start_sec = time.mktime(fwd_start_date.timetuple())
                curr_end_sec = fwd_start_sec - 1
                fwd_period = TimePeriod(curr_start_sec,curr_end_sec)
                self.addPeriod(fwd_period)
                #
                #first line picks up last value in function scope, so loop
                #should be closed. 
        #
        #make back chain
        for i in range(back):
                curr_end_sec = back_end_sec
                curr_end_date = datetime.date.fromtimestamp(curr_end_sec)
                curr_start_date = datetime.date(curr_end_date.year,
                                                curr_end_date.month,
                                                1)
                curr_start_sec = time.mktime(curr_start_date.timetuple())
                back_period = TimePeriod(curr_start_sec,curr_end_sec)
                self.addPeriod(back_period)
                #
                #close loop:
                back_end_sec = curr_start_sec - 1
        #

    def configurePeriod(self,period):
        """


        TimeLine.configurePeriod(period) -> period


        Method sets period's namespace id to that of the TimeLine, then returns
        period. 
        """
        tl_nid = self.id.namespace_id
        period.id.setNID(tl_nid)
        #Period has only a pointer to the Model.namespace_id; periods dont have
        #their bbids.
        return period
        
    def extrapolate_all(self, seed = None):
        """


        TimeLine.extrapolate_all(seed = None) -> None


        Method extrapolates all periods in instance sequentially from seed. If
        seed not specified, method uses instance.current_period.

        Method expects ``seed`` to be a TimePeriod instance. Method will not
        change seed during operation. 
        """
        if not seed:
            seed = self.current_period
        seed_date = seed.ends
        segments = M.get_date_segments(seed_date)
        past = segments[0]
        future = segments[-1]
        #
        self.extrapolate_dates(seed, past, work_backward = True)
        self.extrapolate_dates(seed, future)
        #

    def extrapolate_dates(self, seed, dates, work_backward = False):
        """


        TimeLine.extrapolate_dates(seed, dates, [work_backward = False]) -> None


        Method extrapolates seed to the first date in dates, then sequentially
        extrapolates remaining dates from each other.
        
        Method expects ``seed`` to be an instance of TimePeriod. Seed can be
        external to the caller TimeLine.

        Method expects ``dates`` to be a series of endpoints for the periods in
        instance the caller is targeting. In other words, instance must contain
        a period corresponding to each date in ``dates``.

        Dates can contain gaps. Method will always extrapolate from one date to
        its neighbor. Extrapolation works by requesting that each object in a
        content structure extrapolate itself and any of its subordinates.
        For time-sensitive objects like BusinessUnits, that process should
        automatically adjust to the target date regardless of how far away that
        date is from the instance's reference date.

        If ``work_backward`` is True, method will go through dates
        last-one-first.
        """
        #
        if work_backward:
            dates = dates[::-1]
            #reverse order, so go from newest to oldest
        #
        for date in dates:
            #with default arguments, start work at the period immediately
            #prior to the current period
            target_period = self[date]
            seed.extrapolate_to(target_period)
            seed = target_period
        #

    def findPeriod(self,query):
        """


        TimeLine.findPeriod(query) -> TimePeriod


        Method returns a time period that includes query. ``query`` can be a
        POSIX timestamp (int or float), datetime.date object, or string in
        "YYYY-MM-DD" format. 
        """
        result = None
        end_date = None
        q_date = None
        if isinstance(query,datetime.date):
            q_date = query
        else:            
            try:
                q_date = datetime.date.fromtimestamp(query)
            except TypeError:
                num_query = [int(x) for x in query.split("-")]
                #query is a string, split it
                q_date = datetime.date(*num_query)
        end_date = self.get_ref_end_date(q_date)
        result = self[end_date]
        return result

    def get_date_segments(self, ref_date = None):
        """


        TimeLine.get_date_segments(self, ref_date = None) -> list


        output[0] = list of keys for periods before ref_date
        output[1] = list of ref period (len output[1] == 1)
        output[2] = list of keys for periods after ref_date
        """
        result = None
        if not ref_date:
            ref_date = self.ref_date
        #
        ref_end = self.get_ref_end_date(ref_date)
        #
        dates = sorted(self.keys())
        ref_spot = dates.index(ref_end)
        future_dates = dates[(ref_spot + 1 ): ]
        past_dates = dates[:ref_spot]
        result = [past_dates, [ref_end], future_dates]
        return result
    
    def get_fwd_start_date(self,ref_date):
        """


        TimeLine.get_fwd_start_date(ref_date) -> datetime.date


        Method returns the starting date of the next month. 
        """
        result = None
        ref_day = ref_date.day
        ref_month = ref_date.month
        ref_year = ref_date.year
        if ref_month == 12:
            result = datetime.date(ref_year+1,1,1)
        else:
            result = datetime.date(ref_year,ref_month+1,1)
        return result   

    def get_ref_end_date(self,ref_date):
        """


        TimeLine.get_fwd_end_date(ref_date) -> datetime.date


        Method returns the last date of the month that contains ref_date.
        """
        result = None
        fwd_start_date = self.get_fwd_start_date(ref_date)
        fwd_start_time = time.mktime(fwd_start_date.timetuple())
        ref_end_time = fwd_start_time - 1
        ref_end_date = datetime.date.fromtimestamp(ref_end_time)
        result = ref_end_date
        return result        
    
    def getOrdered(self):
        """


        TimeLine.getOrdered() -> list

        
        Method returns list of periods in instance, ordered from earliest to
        latest endpoint.
        """
        result = []
        for end_date in sorted(self.keys()):
            period = self[end_date]
            result.append(period)
        return result

    def setCurrent(self,period):
        """


        TimeLine.setCurrent(period) -> None


        Method sets instance.current_period to argument.
        """
        self.current_period = period
        
    def updateCurrent(self, ref_date = None):
        """


        TimeLine.updateCurrent([ref_date = None]) -> None


        Method sets instance.current_period to whichever period contains the
        ref_date. If ``ref_date`` == None, method uses current system time. 
        """
        if not ref_date:
            ref_date = datetime.date.today()
        ref_period = self.findPeriod(ref_date)
        self.current_period = ref_period
    
    
