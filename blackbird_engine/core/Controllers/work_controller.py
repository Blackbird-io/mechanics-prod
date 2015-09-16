#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2014
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: Controllers.work_controller

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
interviewer = Interviewer()
summary_t_name = "basic model summary, annualized current with capex"
yenta = Yenta()

#classes    
class WorkController:
    """

    Class of objects that combine all functions necessary to go from one message
    to another.
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    max_cycles            int; max number of attempts before return
    upReady               bool; is current message ready for return 
    upStatus              specific status of message (static)

    FUNCTIONS:
    set_status()          store message status on instance
    choose_direction()    point message to more analysis or portal
    wrap_interview()       clean up / storage to run prior to end
    ====================  ======================================================
    """
    
    def __init__(self):
        self.max_cycles = 20
        self.needs_work = True
        self.status = None

##    def reset(self):
##        """
##
##        aLM.reset() -> None
##
##        Method clears instance message-dependent state and prepares the instance
##        to process a new message
##        """
##        self.ready_for_portal = False
##        self.status = None
##        self.clearMessageOut()  
##        self.clearMessageIn()

    def set_status(self,new_status):
        """


        WorkController.set_status(new_status) -> None


        Method sets instance.status to the new status.
        """
        self.status = new_status

    def choose_direction(self, message):
        """


        WorkController.choose_direction(message) -> message
        

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
        check = Globals.checkMessageStatus
        ready_for_portal = {Globals.status_pendingQuestion,
                            Globals.status_endSession}
        #
        status = check(message)
        #place follow-up status checks in if blocks because they only need them
        #if someone may have changed the message.
        if status == Globals.status_topicNeeded:
            message = interviewer.process(message)
            #interviewer may have decided that the model is good enough and that
            #we should end the interview. refresh status. 
            status = check(message)
        #
        #pass end-session messages to conclude() to go through required wrap-up
        #work. may also check direction here if conclude() needs to ask more
        #questions, so check status after too. 
        if status == Globals.status_endSession:
            message = self.wrap_interview(message)
            #future versions of wrap_interview() may identify gaps in knowledge.
            #if that happens, wrap_interview() may either switch direction back
            #into full interview mode (perhaps by increasing the attention
            #budget) or move the process into a fill-gaps functionality, where
            #the Engine asks questions about critical holes, in MQEND format. 
            #
            #refresh status in case conclude() changed model or message.
            status = check(message)
        if status in ready_for_portal:
            self.needs_work = False
        else:
            self.needs_work = True
        #
        self.set_status(status)
        return message

    def process(self, message):
        """


        WorkController.process(message) -> message


        Method works to improve the model until it's either (i) good enough to
        stop work altogether or (ii) a question for the user comes up and the
        Engine needs to pause work.
        """
        n = 0
        message = self.choose_direction(message)
        #use choose_direction() to for substantive work. method also weeds
        #out messages that are ready for portal delivery right away.
        while self.needs_work:
            model = message[0]
            #
            if self.status == Globals.status_pendingResponse:
                topic_bbid = model.interview.transcript[-1][0]["topic_bbid"]
                topic = yenta.TM.local_catalog.issue(topic_bbid)
                message = topic.process(message)
            #
            elif self.status == Globals.status_topicNeeded:
                topic = yenta.select_topic(model)
                if topic:
                    message = topic.process(message)
                else:
                    pass
                    #Yenta.select_topic() returned None for Topic, which means
                    #it couldn't find any matches in the Topic Catalog. In such
                    #an event, Yenta notes dry run on focal point and IC shifts
                    #to the next focal point
            message = self.choose_direction(message)
            #the engine has done more work on the model. use choose_direction()
            #to see if it can stop or needs to continue.
            #
            n = n + 1
            if n > self.max_cycles:
                break
            #circuit-breaker logic
        #
        return message

    def wrap_interview(self, message):
        """
        

        WorkController.wrap_interview(message) -> message


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
        model = message_in[0]
        message_out = message_in
        #
        if not model.valuation.guide.complete:
            model.path = model.valuation.path
            #set interviewer.default_protocol to 0 <--------------------? should be ok if always running on disposable instances?
            message_out = (model, None, None)
            #send back for more work on valuation
        #
        if not model.summary.guide.complete:
            model.path = model.summary.path
            #set interview.default_protocol to 0
            message_out = (model, None, None)
            #send back for more work on summary
        #
        return message_out
    
##        #or can be something like:
##        message = self.run_valuation(message)
##        message = self.run_summary(message)
##        return message

    def check_valuation(self, message):
        #check that message is m_End
        #only do work then; otherwise dont touch <---------------------
        message_in = message
        message_out = message_in
        #
        model = message_in[0]
        if not model.valuation.complete:
            model.work_path = model.valuation.path
            message_out = (model, None, None)
        #
        return message_out

    def check_summary(self, message):
        pass
        #similar idea to above
        
##the process_summary() and process_valuation() functions should be at SessionController!
##they dont need to be at manager. so force_valuation() could set pointer to some valuation
##object and go from there.
    #basically, that function wants to be able to run process on the valuation only! nothing
    #else. for a particular period. so should be able to set model.valuation to that period,
    #then pass down for regular old processing here? but then would need to set path to
    #model.valuation.path. which is kind of ok i think? or if i dont want to touch path
    #that high up, can have a process_valuation method here, which is just:

#def process_valuation(self, message):
    #message_in = message
    #message_out = message_in
    #model = message_in[0]
    #model.path = model.valuation.path
    ##already pointing to a particular date
    #message_out = self.process(message_in)
    #return message out

    def process_summary(self, message):
        #should be obsolete if i integrate summarization into path
        #or alternatively can have a separate path called ``summarization``
        #kind of like the new market_value interface
        if brute_force:
            summary_topic_id = yenta.TM.local_catalog.by_name[summary_t_name]
            summary_topic = yenta.TM.local_catalog.issue(summary_topic_id)
            message = summary_topic.process(message)
            #
            return message
        else:
            pass
            #set path to model.summary.path; return (m, None, None)


    def process_valuation(self, message):
        #
        #substantively, this should say: keep running process() until valuation
        #object is all done. more specifically, until model.analytics.guide.complete
        #is done.
        #
        #can either change the path...? or do something weird.
        #
        #set interview.path to company.valuation.path
        #pass the whole thing to interviewer.process(message, protocol_key = 0)
        model = message[0]
        if not model.valuation.complete:
            model.path = model.valuation.path
            return message
        if not 
        #
        return message




    
