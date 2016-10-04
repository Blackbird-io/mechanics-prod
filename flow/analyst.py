# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL

# Blackbird Engine
# Module: flow.analyst
"""

Module defines Analyt class. Analysts receive messages and work on a response
until they come up with something that's suitable for delivery to Portal
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
Analyst               worker object, can run independently
====================  ==========================================================
"""




# Imports
import logging

import bb_settings

from .interviewer import Interviewer
from .yenta import Yenta

from tools.for_messages import \
    TOPIC_NEEDED, PENDING_RESPONSE, END_SESSION, \
    check_engine_message as check




# Constants
summary_t_name = "basic model summary, annualized current with capex"

# Globals
charlie_rose = Interviewer()
larry_king = Interviewer()

yenta = Yenta()

logger = logging.getLogger(bb_settings.LOGNAME_MAIN)


# Classes
class Analyst:
    """

    An Analyst uses other objects (topics and flow modules) to improve a model
    until it is either complete or requires external input.
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    max_cycles            int; max number of attempts before return
    needs_work            bool; does engine need to work more or can send out?
    status                state for message status so methods can communicate

    FUNCTIONS:
    check_stage()         see if a particular stage is complete
    choose_direction()    point message to more analysis or portal
    process()             main interace, perform engine work until ready
    wrap_interview()      clean up / storage to run prior to end
    ====================  ======================================================
    """

    def __init__(self):
        self.max_cycles = 200
        self.needs_work = True
        self.status = None

    def check_stage(self, message, stage):
        """


        Analyst.check_stage(message, stage) -> message


        For **end_session messages only**, method checks if ``stage`` is
        complete. If it is, returns message as-is. Otherwise, sets
        model.target.stage to the argument, gets an interviewer to pick out a
        focal point on that stage, and then returns the resulting message so
        that other routines can continue work.

        This method contemplates that interviewer will send back a (M,_,_)
        message on the new stage, but **does not** require it to do so. So the
        interviewer can decide that the stage is complete and return an
        end_session message after all.
        """
        #
        status = check(message)
        if status == END_SESSION:
            if stage.guide.complete:
                pass
            else:
                model = message[0]
                model.target.stage = stage
                message = (model, None, None)
                message = larry_king.process(message)
                # make sure message comes out with a focal point
        #
        return message

    def choose_direction(self, message, *pargs, **kargs):
        """


        Analyst.choose_direction(message) -> message


        Method reads the message and selects the direction that best suits its
        content. If the message is ready for delivery to portal, method notes
        accordingly on the instance.

        Method focuses on m,_,_ and m,_,end messages. These represent an
        inflection point in the interview: the Engine can either move on to a
        new area of analysis or conclude work altogether.

        Method only performs shallow, format-based analysis on its own. Method
        delegates deeper, substantive analysis to objects that specialize in
        that kind of reasoning.

        Method first checks the message format to determine whether the model
        needs a fresh topic of analysis. If it does, method passes the message
        to interviewer. Interviewer examines the model's path for completion,
        marks the next focal point for substantive analysis on the model's
        ``interview`` attribute, and returns the message.

        Sometimes, interviewer will determine that the model is good enough and
        that the Engine should stop asking the user questions. At other times,
        some other object or routine may reach the same conclusion on its own.

        In both situations, this method will need to make sure that the Engine
        completes all required steps prior to signing off on a particular
        model. Method will do so by passing the message down to the
        wrap_interview() routine.

        Once wrap_interview() returns the message, this method will perform
        a final status check and note whether the message is ready for
        delivery to the portal.
        """
        status = check(message)
        if status == TOPIC_NEEDED:
            message = charlie_rose.process(message)
            status = check(message)
        #
        if status == END_SESSION:
            message = self.wrap_interview(message)
            status = check(message)
        #
        self.status = status
        #
        return message

    def process(self, message, *pargs, **kargs):
        """


        Analyst.process(message) -> message


        Method works to improve the model until it's either (i) good enough to
        stop work altogether or (ii) a question for the user comes up and the
        Engine needs to pause work.
        """
        n = 0
        message = self.choose_direction(message, *pargs, **kargs)
        # use choose_direction() to for substantive work. method also weeds
        # out messages that are ready for portal delivery right away.
        yenta.diary.clear()
        while self.status in [TOPIC_NEEDED, PENDING_RESPONSE]:
            #
            model = message[0]
            #
            if self.status == PENDING_RESPONSE:
                topic_bbid = model.transcript[-1][0]["topic_bbid"]
                topic = yenta.TM.local_catalog.issue(topic_bbid)
                logger.info('{} {}'.format(self.status, topic.source))
                message = topic.process(message)
            #
            elif self.status == TOPIC_NEEDED:
                topic = yenta.select_topic(model)
                if topic:
                    logger.info('{} {}'.format(self.status, topic.source))
                    message = topic.process(message)
                else:
                    pass
                    # Yenta.select_topic() returned None for Topic, which means
                    # it couldn't find any matches in the Topic Catalog. In such
                    # an event, Yenta notes dry run on focal point and IC shifts
                    # to the next focal point
            message = self.choose_direction(message, *pargs, **kargs)
            # the engine has done more work on the model. use choose_direction()
            # to see if it can stop or needs to continue.
            #
            n = n + 1
            if n > self.max_cycles:
                break
            # circuit-breaker logic
        #
        return message

    def wrap_interview(self, message, run_valuation=True, run_summary=True):
        """


        Analyst.wrap_interview(message) -> message


        Method prepares a final message for portal. The final message should
        contain a completed Engine model, as well as any API-format summary
        and analytics data the portal expects. Accordingly,


        Method runs process_summary to summarize the model.

        More generally, wrapInterview() performs clean up, storage, and/or
        transformation logic on messages signaling the end of an interview
        before they go out to higher level modules and the user.

        For example, wrapInterview() can insert final questions or flag certain
        items for follow-up or review.
        """
        # basically, check for completion in various ways, if it's not complete
        # point where necessary, and set message into m,_,_
        #
        model = message[0]
        #
        if run_valuation:
            message = self.check_stage(message, model.valuation)
        if run_summary:
            message = self.check_stage(message, model.summary)
        #
        return message
