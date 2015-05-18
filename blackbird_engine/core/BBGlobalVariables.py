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

FUNCTIONS:
checkStatus()         compare message to known patterns, returns fit
====================  ==========================================================
"""


#Calendar:
t0 = 1427688000.0
#March 30, 2015, 00:00:00 am
fix_ref_date = True
#whether models always start on the same date; keep True for testing

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
screen_width = 80
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
cc_haircut = 0.20

#Object Life Cycle
conception_date_min = "1850-01-01"
conception_date_max = "2100-01-01"
gestation_years_max = 15
gestation_years_def = 1
life_span_years_max = 300
life_span_years_def = 10
ref_date_min = "1900-01-01"
ref_date_max = "2100-01-01"

