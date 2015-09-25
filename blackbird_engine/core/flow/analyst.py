#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2014
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: flow.analyst

"""

[This module gets a message and processes it until it gets a new message suitable
for return to upper level components. Only two types of messages are suitable
for upward return:
    1) MQ_: those with an open question for the user
    2) xxEND: those signaling that the interview is complete

The process() function provides the primary interface for module use.

On a process(message) call, Analyzer checks if additional user input is
necessary to build out the model (M in MQR). If user input is necessary,
Analyzer generates a message suitable for such input. If the model is complete,
Analyzer generates a message carrying the completed model and the END_INTERVIEW
sentinel in R position.

SessionManager provides Analyzer with its connector for resource access. The
connector primarily comes into play when Analyzer locates a new topic and
prepares it for use. ]
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:


FUNCTIONS:

====================  ==========================================================
"""




#imports
import BBGlobalVariables as Globals

from .interviewer import Interviewer
from .yenta import Yenta




#globals
check = Globals.checkMessageStatus
interviewer_a = Interviewer()
interviewer_b = Interviewer()
summary_t_name = "basic model summary, annualized current with capex"
yenta = Yenta()
#
topic_needed = Globals.status_topicNeeded
pending_question = Globals.status_pendingQuestion
pending_response = Globals.status_pendingResponse
end_session = Globals.status_endSession

#classes    
class Analyst:
    """

    Class of objects that manage combine all functions necessary to go from one message
    to another.
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
        self.max_cycles = 20
        self.needs_work = True
        self.status = None

    def check_stage(self, message, stage):
        """


        Analyst.check_stage(message, stage) -> message
    

        For ***end_session messages only**, method checks if ``stage`` is
        complete. If it is, returns message as-is. Otherwise, sets model.stage
        to the argument, gets an interviewer to pick out a focal point on that
        stgage, and then returns the resulting message so that other routines
        can continue work.

        This method contemplates that interviewer will send back a (M,_,_)
        message on the new stage, but **does not** require it to do so. So the
        interviewer can decide that the stage is complete and return an
        end_session message after all.
        """
        #
        status = check(message)
        if status == end_session:
            if stage.guide.complete:
                pass
            else:
                model = message[0]
                model.stage = stage
                message = (model, None, None)
                message = interviewer_b.process(message)
                #make sure message comes out with a focal point
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
##        status = check(message)
##        #
##        if status in [topic_needed, end_session]:
##            for i in range(2):
##                if i > 0:
##                    status = check(message)
##                    #save cycles
##                if status == topic_needed:
##                    message = interviewer_a.process(message)
##                    status = check(message)
##                    if status == topic_needed:
##                        break
##                #
##                if status == end_session:
##                    message = self.wrap_interview(message, *pargs, **kargs)
##                    status = check(message)
##                    if status == end_session:
##                        break
##                #
##        self.status = status
##        if status in [pending_question, end_session]:
##            self.needs_work = False
##        else:
##            self.needs_work = True
##        #
##        return message
##        #loop runs at most twice per call. interviewer and wrap_interview both
##        #can transform the message. we only want to deliver end_session messages
##        #if wrap_interview() has ``signed off`` on them.
##        #
##        #on the other hand, if interviewer says ``end_session``, we want to pass
##        #the message to wrap_interview() to confirm the action. similarly, if
##        #wrap() thinks that a message needs more work, we need to pass it to
##        #interviewer() to pick a focal point for that work.
##        #
##        #hence the loop structure: each subroutine can deliver a message we
##        #trust, in which case we break. or it can deliver something the other
##        #routine needs to see, in which case we pass it on.
##        #
##        #the loop runs twice, so we always pick a direction (even, for example,
##        #if interviewer insists that a m,_,_ message it got from wrap() should
##        #turn to end session). if we don't put a fixed decision limit on the
##        #flow, we risk creating an infinite loop where the routines disagree
##        #with each other. the same problem prevents a recursive implementation.
##        #
##
##    def choose_no_loop(self, message, *pargs, **kargs):
        status = check(message)
        if status == topic_needed:
            message = interviewer_a.process(message)
            status = check(message)
        #
        if status == end_session:
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
        #use choose_direction() to for substantive work. method also weeds
        #out messages that are ready for portal delivery right away.       
        while self.status in [topic_needed, pending_response]:
            #
            model = message[0]
            #
            if self.status == pending_response:
                topic_bbid = model.transcript[-1][0]["topic_bbid"]
                topic = yenta.TM.local_catalog.issue(topic_bbid)
                message = topic.process(message)
            #
            elif self.status == topic_needed:
                topic = yenta.select_topic(model)
                if topic:
                    message = topic.process(message)
                else:
                    pass
                    #Yenta.select_topic() returned None for Topic, which means
                    #it couldn't find any matches in the Topic Catalog. In such
                    #an event, Yenta notes dry run on focal point and IC shifts
                    #to the next focal point
            message = self.choose_direction(message, *pargs, **kargs)
            #the engine has done more work on the model. use choose_direction()
            #to see if it can stop or needs to continue.
            #
            n = n + 1
            if n > self.max_cycles:
                break
            #circuit-breaker logic
        #
        return message           

    def wrap_interview(self, message, run_valuation = True, run_summary = True):
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
        #basically, check for completion in various ways, if it's not complete
        #point where necessary, and set message into m,_,_
        #
        model = message[0]
        #
        if run_valuation is True:
            message = self.check_stage(message, model.valuation)
        if run_summary is True:
            message = self.check_stage(message, model.summary)
        #
        return message

        

        




    
