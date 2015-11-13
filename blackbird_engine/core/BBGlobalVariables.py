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
default_inflation     num; expected inflation at macro equilibrium
messagePatterns       dictionary of message patterns and related statuses
p_topicNeeded         bool pattern for ``topic needed`` messages (M__)
p_pendingQuestion     bool pattern for ``pending question`` messages (MQ_)
p_pendingResponse     bool pattern for ``pending response`` messages (MQR)
p_endSession          bool pattern for ``endSession`` messages (M_R)
p_blank               bool pattern for blank messages (___)
status_topicNeeded    string
status_pendingQuestion  string
status_pendingResponse  string
status_endSession       string
user_correction       num; expected difference between user input and actual

FUNCTIONS:
checkStatus()         compare message to known patterns, returns fit
====================  ==========================================================
"""




#imports
#built-in modules only
from datetime import date, timedelta




#globals

#Tags:
dropDownReplicaTag = "dropdownreplica"
doNotTouchTag = "DO NOT TOUCH"
topicTag = "topic"
questionTag = "question"
ACTIVETag = "active"
trumpTag = "TRUMP"
tOneTime = "one-time"
#integrate below into a real rule
uninheritableTags = [doNotTouchTag, dropDownReplicaTag]
#check usage (should only be in Financials module), replace

#Method Signatures:
signatures = {}
signatures["BusinessUnit.consolidate"] = "consolidated by %s"
#
signatures["Financials.manageDropDownReplicas"] = "manageDDR"
signatures["Financials.updateSummaries"] = "updateSummaries"
#
signatures["LineItem.__init__"] = "__init__"
signatures["LineItem.clear"] = "LineItem.resetValue"
signatures["LineItem.ex_to_default"] = "LineItem.ex_to_default"
signatures["LineItem.ex_to_special"] = "LineItem.ex_to_special"

#Exceptions:
#(may be redundant w LTDEX_0_ObjectLibraries.Exceptions because the Globals
#module CANNOT import anything other than built-in libraries).
class BlackbirdError(Exception): pass
#parent class for all custom errors
class BBAnalyticalError(BlackbirdError): pass

#Other:
SCREEN_WIDTH = 80
min_progress_per_question = 2
misfitLabel = "MISFIT"  #<---------------------------------------------------------eliminate
END_INTERVIEW = "END_interview"
user_stop = "STOP INTERVIEW"

#Message Status Tools:
messagePatterns = {}
p_topicNeeded = (1,0,0)
p_pendingQuestion = (1,1,0)
p_pendingResponse = (1,1,1)
p_endSession = (1,0,1)
p_blank = (0,0,0)

status_topicNeeded = "topic needed"
status_pendingQuestion = "pending question"
status_pendingResponse = "pending response"
status_endSession = "end session"

messagePatterns[p_topicNeeded] = status_topicNeeded
messagePatterns[p_pendingQuestion] = status_pendingQuestion
messagePatterns[p_pendingResponse] = status_pendingResponse
messagePatterns[p_endSession] = status_endSession
messagePatterns[p_blank] = status_endSession

def checkMessageStatus(mqrMessage):
    """

    checkMessageStatus(mqrMessage) -> str

    Function compares the message to known patterns stored in messagePatterns
    dictionary and returns fit. If message contains the END_INTERVIEW
    sentinel in last position (ie, message is in xxEND formaT), function
    returns endSession status without running further logic. 
    """
    
    if mqrMessage[2] == END_INTERVIEW or mqrMessage[2] == user_stop:
        status = messagePatterns[p_endSession]
    else:
        pattern = [0,0,0]
        for i in range(len(mqrMessage)):
            if mqrMessage[i]:
                pattern[i] = True
        pattern = tuple(pattern)
        #turn list into a tuple so you can use it as a dict key (lists are
        #mutable and therefore unhashable)
        try:
            status = messagePatterns[pattern]
        except KeyError:
            label = "Unusual message format"
            raise BBAnalyticalError(label)
            #something odd happening here
    return status

#Modelling:
default_model_name = "Blank Blackbird Model"
default_unit_name = "Blank Unit"
default_periods_back = 36
default_periods_fwd = 36
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
t0 = date(2015,6,16)
fix_ref_date = True
#whether models always start on the same date; keep True for testing
days_in_month = 30
days_in_year = 365




