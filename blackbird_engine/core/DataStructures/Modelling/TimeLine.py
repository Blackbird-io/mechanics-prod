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
from datetime import date, timedelta
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

    Unless otherwise specified, class expects all dates as datetime.date objects
    and all periods as datetime.timedelta objects.

    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    current_period        period that represents a reference point in time
    id                    instance of PlatformComponents.ID class, for interface
    
    FUNCTIONS:
    add_period()           configures and records period, keyed by end date
    build()               populates instance with adjacent time periods
    configure_period()     connects period to instance namespace id     
    find_period()          returns period that contains queried time point
    extrapolate_all()     use seed to fill out all periods in instance
    extrapolate_dates()   use seed to fill out a range of dates
    get_fwd_start_date()  returns first date of next month
    get_red_end_date()    returns last date of current month
    getOrdered()          returns list of periods ordered by end point
    set_current()          sets instance.current_period to argument
    update_current()       updates current_period for reference or actual date
    ====================  ======================================================
    """
    
    def __init__(self):
        dict.__init__(self)
        self.current_period = None
        self.id = ID()
        #timeline objects support the id interface and pass the model's id down
        #to time periods. the timeline instance itself does not get its own
        #bbid.

    def __str__(self, lines = None):
        """


        Components.__str__(lines = None) -> str


        Method concatenates each line in ``lines``, adds a new-line character at
        the end, and returns a string ready for printing. If ``lines`` is None,
        method calls pretty_print() on instance. 
        """
        if not lines:
            lines = self.pretty_print()
        line_end = "\n"
        result = line_end.join(lines)
        return result

    def add_period(self, period):
        """


        TimeLine.add_period(period) -> None


        Method configures period and records it in the instance under the
        period's end_date. 
        """
        period = self.configure_period(period)
        self[period.end] = period

    def build(self, ref_date = None, fwd = 36, back = 36):
        """


        TimeLine.build([ref_date = None[, fwd = 36[, back = 36]) -> None


        Method creates a chain of TimePeriods with adjacent start and end
        points. The chain is ``fwd`` periods long into the future and ``back``
        periods long into the past.

        Method expects ``ref_date`` to be a datetime.date object. If ref_date
        is left blank, method uses date.today() as the ref date. 

        Method sets instance.current_period to the period covering the reference
        date.
        """
        #
        if not ref_date:
            ref_date = date.today()
        ref_month = ref_date.month
        ref_year = ref_date.year
        #
        current_start_date = date(ref_year, ref_month, 1)
        #
        #make reference period
        fwd_start_date = self.get_fwd_start_date(ref_date)
        current_end_date = fwd_start_date - timedelta(1)
        current_period = TimePeriod(current_start_date, current_end_date)
        self.add_period(current_period)
        self.set_current(current_period)
        #
        back_end_date = current_start_date - timedelta(1)        
        #save known starting point for back chain build before fwd changes it
        #
        #make fwd chain
        for i in range(fwd):
                #pick up where ref period analysis leaves off
                curr_start_date = fwd_start_date
                fwd_start_date = self.get_fwd_start_date(curr_start_date)
                curr_end_date = fwd_start_date - timedelta(1)
                fwd_period = TimePeriod(curr_start_date, curr_end_date)
                self.add_period(fwd_period)
                #
                #first line picks up last value in function scope, so loop
                #should be closed. 
        #
        #make back chain
        for i in range(back):
                curr_end_date = back_end_date
                curr_start_date = date(curr_end_date.year,
                                       curr_end_date.month,
                                       1)
                back_period = TimePeriod(curr_start_date,curr_end_date)
                self.add_period(back_period)
                #
                #close loop:
                back_end_date = curr_start_date - timedelta(1)
        #

    def configure_period(self,period):
        """


        TimeLine.configure_period(period) -> period


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
        seed_date = seed.end
        #
        segments = self.get_segments(seed_date)
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
        for i in range(len(dates)):
            date = dates[i]                
            #with default arguments, start work at the period immediately
            #prior to the current period
            target_period = self[date]
            updated_period = seed.extrapolate_to(target_period)
            #
            #extrapolate_to() always does work on an external object and leaves
            #the target untouched. Manually swap the old period for the new
            #period.
            #
            if i == 0:
                updated_period = self.configure_period(updated_period)
                #on i == 0, extrapolating from the original seed. seed can be
                #external (come from a different model), in which case it would
                #use a different model namespace id for unit tracking.
                #
                #accordingly, when extrapolating from the may-be-external seed,
                #use configure_period() to conform output to current model.
                #
                #subsequent iterations of the loop will start w periods that are
                #already in the model, so method can leave their namespace id
                #configuration as is.
                #
            self[date] = updated_period
            seed = updated_period
        #

    def find_period(self,query):
        """


        TimeLine.find_period(query) -> TimePeriod


        Method returns a time period that includes query. ``query`` can be a
        POSIX timestamp (int or float), datetime.date object, or string in
        "YYYY-MM-DD" format. 
        """
        result = None
        end_date = None
        q_date = None
        if isinstance(query, date):
            q_date = query
        else:            
            try:
                q_date = date.fromtimestamp(query)
            except TypeError:
                num_query = [int(x) for x in query.split("-")]
                #query is a string, split it
                q_date = date(*num_query)
        end_date = self.get_ref_end_date(q_date)
        result = self[end_date]
        return result

    def get_segments(self, ref_date = None):
        """


        TimeLine.get_segments(self, ref_date = None) -> list


        output[0] = list of keys for periods before ref_date
        output[1] = list of ref period (len output[1] == 1)
        output[2] = list of keys for periods after ref_date
        """
        result = None
        #
        if not ref_date:
            ref_date = self.current_period.end
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
            result = date(ref_year+1,1,1)
        else:
            result = date(ref_year,ref_month+1,1)
        return result   

    def get_ref_end_date(self,ref_date):
        """


        TimeLine.get_fwd_end_date(ref_date) -> datetime.date


        Method returns the last date of the month that contains ref_date.
        """
        result = None
        fwd_start_date = self.get_fwd_start_date(ref_date)
        ref_end_date = fwd_start_date - timedelta(1)
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

    def pretty_print(self,dates  = None, sep = "<<", border = "-", hook = True):
        """


        TimeLine.pretty_print([dates = None[, sep = "<<"[, hook = True]]]) -> list


                
        """
        clean_lines = []
        #lines is the final, flat list of strings
        #
        if not dates:
            dates = sorted(self.keys())
        cushion = 1
        hook_char = "}"
        lead = "PERIOD:"
        space = " "
        #
        underscore = "_"
        bu_lines = self.current_period.content.pretty_print()
        bu_width = len(bu_lines[0])
        bu_height = len(bu_lines)
        sep_width = len(sep)
        column_width = bu_width + cushion * 2 + sep_width
        column_count = Globals.screen_width // column_width
##        column_count = 3
        #
        #the first column stays constant from row to row: it's just the lead,
        #plus borders and white space. make all the strings once, then use them
        #for each row. 
        #
        c0_width = len(lead) + cushion + sep_width
        #
        top_pad_c0 = space * c0_width
        top_brdr_c0 = border * c0_width
        calendar_c0 = lead + space * cushion + sep
        bot_brdr_c0 = top_brdr_c0[:]
        hanger_c0 = space * c0_width
        bu_line_c0 = space * c0_width
        bot_pad_c0 = top_pad_c0[:]
        c0 = [top_pad_c0,
              top_brdr_c0,
              calendar_c0,
              bot_brdr_c0,
              hanger_c0]
        c0.extend([bu_line_c0 for i in range(bu_height)])
        c0.append(bot_pad_c0)
        #
        #now, build each row. to do so, walk dates in steps of column_count. for
        #each date, build a column (list) of strings. if the column contains the
        #current date, apply ``box`` post-processing to that column. store each
        #column in the columns list for that row. then, when done with all the
        #dates in the row, zip all of the columns together. the zipped object
        #will contain tuples that represent each display line necessary to show
        #that row: ([c0_line0], [c1_line0], ...).
        #
        #to make a flat string suitable for ``lines``, join all of the elements
        #in a tuple, then append that line to lines. do so for all lines in the
        #row (all tuples in the zipped object).
        #
        #finally, when all the hard work is done, add an empty string at the end
        #of the row
        #
        for i in range(0, len(dates), column_count):
            #
            #build a row of c0 plus column_count date-specific columns
            #
            row = []
            row.append(c0)
            row_dates = dates[i : (i + column_count)]
            #
            for end_date in row_dates:
                #
                #build a column for each date
                #
                period = self[end_date]
                post_processing = False
                if end_date == self.current_period.end:
                    post_processing = True
                #                
                top_pad = space * column_width
                top_brdr = border * column_width
                calendar = end_date.isoformat().center(column_width - sep_width)
                calendar = calendar + sep
                bot_brdr = top_brdr[:]
                hanger = space * column_width
                col_bu_lines = []
                if period.content:
                    bot_brdr = hook_char.center(column_width, border)
                    hanger = "|".center(column_width)
                    for line in period.content.pretty_print():
                        adj_line = line.center(column_width)
                        col_bu_lines.append(adj_line)
                else:
                    for k in range(bu_height):
                        bu_line_blank = space * column_width
                        col_bu_lines.append(bu_line_blank)
                bot_pad = top_pad[:]
                #
                if post_processing:
                    top_pad = space + underscore * (column_width - 2) + space
                    bot_pad = underscore * column_width
                #
                column = [top_pad,
                          top_brdr,
                          calendar,
                          bot_brdr,
                          hanger]
                column.extend(col_bu_lines)
                column.append(bot_pad)
                #
                if post_processing:
                    for j in range(1, len(column)):
                        line = column[j]
                        column[j] = "|" + line[1:-1] + "|"
                #
                row.append(column)
            #
            #now zip the columns together into clean lines
            zipped_row = zip(*row)
            #zipped_row should be a tuple w len == column_count + 1
            for line_elements in zipped_row:
                flat_line = "".join(line_elements)
                clean_lines.append(flat_line)
            else:
                clean_lines.append("")
                #add a blank line after every row               
        #
        return clean_lines
        
    def set_current(self,period):
        """


        TimeLine.set_current(period) -> None


        Method sets instance.current_period to argument.
        """
        self.current_period = period
        
    def update_current(self, ref_date = None):
        """


        TimeLine.update_current([ref_date = None]) -> None


        Method sets instance.current_period to whichever period contains the
        ref_date. If ``ref_date`` == None, method uses current system time. 
        """
        if not ref_date:
            ref_date = date.today()
        ref_period = self.find_period(ref_date)
        self.current_period = ref_period
    
    
