#PROPRIETARY AND CONFIDENTIAL
#Property of Ilya Podolyako
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Credit Market
#BBGlobalVariables
#By Ilya Podolyako

"""

This module contains settings and functions used in multiple places throughout
the Blackbird environment.

====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a
====================  ==========================================================
"""




#imports
#built-in modules only
from datetime import date




# Constants

###Exceptions:
##class BlackbirdError(Exception): pass
###parent class for all custom errors
##class BBAnalyticalError(BlackbirdError): pass

#Other:
DEBUG_MODE = False
SCREEN_WIDTH = 80
min_progress_per_question = 2
##END_INTERVIEW = "END_interview"
##user_stop = "STOP INTERVIEW"

###Message Status Tools:
##messagePatterns = {}
##p_topicNeeded = (1,0,0)
##p_pendingQuestion = (1,1,0)
##p_pendingResponse = (1,1,1)
##p_endSession = (1,0,1)
##p_blank = (0,0,0)
##
##status_topicNeeded = "topic needed"
##status_pendingQuestion = "pending question"
##status_pendingResponse = "pending response"
##status_endSession = "end session"
##
##messagePatterns[p_topicNeeded] = status_topicNeeded
##messagePatterns[p_pendingQuestion] = status_pendingQuestion
##messagePatterns[p_pendingResponse] = status_pendingResponse
##messagePatterns[p_endSession] = status_endSession
##messagePatterns[p_blank] = status_endSession
##
##def checkMessageStatus(mqrMessage):
##    """
##
##    checkMessageStatus(mqrMessage) -> str
##
##    Function compares the message to known patterns stored in messagePatterns
##    dictionary and returns fit. If message contains the END_INTERVIEW
##    sentinel in last position (ie, message is in xxEND formaT), function
##    returns endSession status without running further logic. 
##    """
##    
##    if mqrMessage[2] == END_INTERVIEW or mqrMessage[2] == user_stop:
##        status = messagePatterns[p_endSession]
##    else:
##        pattern = [0,0,0]
##        for i in range(len(mqrMessage)):
##            if mqrMessage[i]:
##                pattern[i] = True
##        pattern = tuple(pattern)
##        #turn list into a tuple so you can use it as a dict key (lists are
##        #mutable and therefore unhashable)
##        try:
##            status = messagePatterns[pattern]
##        except KeyError:
##            label = "Unusual message format"
##            raise BBAnalyticalError(label)
##            #something odd happening here
##    return status

#Modelling:
DEFAULT_MODEL_NAME = "Blank Blackbird Model"

max_unit_count = 200
mid_unit_count = 20
high_unit_count = 50
#mid and high unit count serve as thresholds for medium and in-depth analysis.
#blackbird will analyze a model with a medium number of units reasonably well,
#and a model with a large number of units carefully. it is up to individual
#topics to support this type of depth control.
batch_count = 100
batch_count = min(batch_count, max_unit_count)
#batch count is the number of units that a company with more units than the
#max count will be split into. as batch_count goes up, models become more
#granular and more unwieldy. batch_count <= max_unit_count. the two parameters
#are distinct because Blackbird may want to capture full detail on a 200-store
#business if that means a performance hit, but when dealing with 10,000 clients
#optimize to something more compact. 

#Market
cc_haircut = 0.20
default_inflation = 0.03
user_correction = 0.10

#Calendar
t0 = date(2015, 6, 16)
fix_ref_date = True
#whether models always start on the same date; keep True for testing
days_in_month = 30
days_in_year = 365




