# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL
# Blackbird Environment
# Module: tools.for_messages

"""
Module provides toolkit for processing Engine messages.
"""



# Imports
import bb_exceptions




# Constants
END_INTERVIEW = "END_interview"
USER_STOP = "STOP INTERVIEW"

TOPIC_NEEDED = "topic needed"
PENDING_QUESTION = "pending question"
PENDING_RESPONSE = "pending response"
END_SESSION = "end session"

# Message Status Tools:
p_topic_needed = (1, 0, 0)
p_pending_question = (1, 1, 0)
p_pending_response = (1, 1, 1)
p_end_session = (1, 0, 1)
p_blank = (0, 0, 0)

message_patterns = {}
message_patterns[p_topic_needed] = TOPIC_NEEDED
message_patterns[p_pending_question] = PENDING_QUESTION
message_patterns[p_pending_response] = PENDING_RESPONSE
message_patterns[p_end_session] = END_SESSION
message_patterns[p_blank] = END_SESSION


def engine_message_status(engine_message):
    """

    engine_message_status() -> str

    Function compares the message to known patterns stored in message_patterns
    dictionary and returns fit. If message contains the END_INTERVIEW
    sentinel in last position (ie, message is in xxEND formaT), function
    returns endSession status without running further logic.
    """

    if engine_message[2] == END_INTERVIEW or engine_message[2] == USER_STOP:
        status = message_patterns[p_end_session]
    else:
        pattern = (int(bool(x)) for x in engine_message)
        # tuple for use as dict key
        pattern = tuple(pattern)
        try:
            status = message_patterns[pattern]
        except KeyError:
            label = "Unusual message format"
            raise bb_exceptions.BBAnalyticalError(label)
            # something odd happening here
    return status


def portal_message_status(portal_message):
    """

    portal_message_status() -> str

    Function checks the status of a portal format message. To that end it
    creates a tuple from a dict and runs it through engine_message_status.
    """
    mock_engine_msg = (portal_message[k] for k in ('M', 'Q', 'R'))

    return engine_message_status(tuple(mock_engine_msg))
