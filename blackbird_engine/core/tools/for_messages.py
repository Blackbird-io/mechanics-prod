#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: tools.for_messages

"""
Module provides toolkit for processing Engine messages. 
"""



# Imports
import bb_exceptions




# Constants
END_INTERVIEW = "END_interview"
USER_STOP = "STOP INTERVIEW"

# Message Status Tools:
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
    
    if mqrMessage[2] == END_INTERVIEW or mqrMessage[2] == USER_STOP:
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
            raise bb_exceptions.BBAnalyticalError(label)
            #something odd happening here
    return status
