#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Engine
#Module: tools.for_calendar

"""

Module contains functions for analyzing time and date. 
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
find_most_recent()    return date from pool that most closely precedes query

CLASSES:
n/a
====================  ==========================================================
"""




#imports
import BBExceptions

from datetime import date

from . import parsing as for_parsing




#globals
#n/a

#functions
def find_closest(query_date, date_pool):
    #index query in pool (n), then compare distance to n-1, n+1
    pass

def find_most_recent(query_date, date_pool):
    """


    find_most_recent(query_date, date_pool) -> datetime.date


    Function returns the date in pool that most closely precedes query date. If
    query date is itself in pool, function will return query_date.

    ``date_pool`` should be a container of sortable objects
    
    Selection algorithm sorts a set of date_pool contents together with
    query_date and returns the value that precedes query_date.

    Function raises an error if query_date is earlier than every item in pool. 
    """
    last_known = None
    #
    if not isinstance(query_date, date):
        query_date = for_parsing.date_from_iso(query_date)
        #if query is not a valid date, try to convert it
    #
    if query_date in date_pool:
        last_known = query_date
    else:
        w_query = set(date_pool) | {query_date}
        w_query = sorted(w_query)
        i_query = w_query.index(query_date)
        if i_query == 0:
            c = "Query is earliest date in pool."
            raise BBExceptions.BBAnalyticalError(c, query_date)
        else:
            i_prior = i_query - 1
            last_known = w_query[i_prior]
    #
    return last_known    
