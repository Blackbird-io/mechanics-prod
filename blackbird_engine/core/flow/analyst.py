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
check = Globals.checkMessageStatus
interviewer = Interviewer()
summary_t_name = "basic model summary, annualized current with capex"
yenta = Yenta()

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

    def set_status(self,new_status):
        """


        Analyst.set_status(new_status) -> None


        Method sets instance.status to the new status.
        """
        self.status = new_status

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
        
        end_session = Globals.status_endSession
        topic_needed = Globals.status_topicNeeded
        pending_question = Globals.status_pendingQuestion
        #
        status = check(message)
        if status == topic_needed:
            message = interviewer.process(message)
            status = check(message)

        if status == end_session:
            message = self.wrap_interview(message)
            status = check(message)
            if status == topic_needed:
                #dedicated second pass by interviewer, in case of ?
                message = interviewer.process(message)
                #what if this guy generates an end_
                
        
        
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
            message = self.wrap_interview(message, *pargs, **kargs)
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
        #
        return message

    
        #if wrap_ returns end, all good
        #otherwise, repeat through interviewer
        #

        #so:
        #run loop until wrap() returns end
        #in loop:
            #message = interviewer(message)
            #if message == end_session:
                #message = wrap(message)
            #if message == topic_needed:
                #continue
            #else:
                #break

        #if status == topic_needed:
            #message = interviewer(message)
            #status = check(message)
        #
        #if sttaus == end_message:
            #message = wrap(message)
            #status = check(message)
            #if status == topic_needed:
                #message = interviewer(message)
                #status = check(message)

        #or i can package the second logic chunk in wrap()

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
        while self.needs_work:
            #
            model = message[0]
            #
            if self.status == Globals.status_pendingResponse:
                topic_bbid = model.transcript[-1][0]["topic_bbid"]
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
        #alternate pattern:
        #use model.guide.complete instead of the analyzer.needs_work indicator; #<--------------------------------------------------- should probably implement
        #can make Analyzer completely stateless, but at the expense of knowing
        #how to look inside the model a bit.
        #
        #
        #model = message[0]
        #while model.guide.needs_work:
            #status = check(message)
            #if status == pending_response:
                #topic_bbid = model.transcript[-1]
                #topic
                #message = topic.process(message)
            #elif status == topic_needed:
                #topic = yenta.select_topic(model)
                #if topic:
                    #message = topic.process(message)
                #else:
                    #pass
            #message = self.choose_direction(message, *pargs, **kargs)
            #del model
            #model = message[0]
            ##update model pointer in case the object changed
            ##circuit breaker
        #
        #return message
        

    #status = check(status)
    #loop = False
    #if status in [topic_needed, end_session, pending_response]:
        #loop = 
    #while loop:
        #if status == open_question:
            #break
        #if status
    #
    #the problem: if interviewer delivers end_session, it's not good enough. you
    #need wrapper to deliver the same to consider it done.

    #so basically choose_direction() should deliver end_ only if wrap() does

    #while status in [pending_response, topic_needed]:
        #if status == topic_needed:
            #self.choose_direction(message)
            ##here, run interviewer. if interviewer returns end, run wrap
            ##then do nothing?
            ##but problem is i expect to choose a topic here
            ##
        #elif status == pending_response:
            #self.process_response(message)
            ##returns M,_,_
        #status = check(message)
        ##if mq_, end, pop out

    #so what if i basically make choose:
    #def choose()
        #status(message)
        #if status = topic_needed:
            #interviewer.process(message)
            #topic = yenta.process(model)
            #message = topic.process(message)
    
        #if topic_needed
        #interviewer.process(message)
        #if status 
    

    def choose():
        status = check(message)
        if status = topic_needed:
            message = interviewer.process(message)
            status = check(message)
        while status == end_session:
            message = self.wrap(message)
            status = check(message)
            if status == topic_needed:
                message = interviewer.process(message)
                status = check(message)

    #allow delivery of end_sesson only if wrap_interview() produces it
    #while status = end_session:
            #message = wrap_interview(message)
                ##wrap_interview should run choose_direction() on topic_needed?
                ##
            #status = check(message)
    
            


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

    def check_stage(self, message, stage):
        """


        Analyst.check_stage(message, stage) -> message
    

        For ***end_session messages only**, method checks if ``stage`` is
        complete. If it is, returns message as-is. Otherwise, sets model.stage
        to the argument and returns an (M,_,_) message so other routines can
        continue work. 
        """
        message_in = message
        message_out = message_in
        #
        status = check(message_in)
        if status == Globals.status_endSession:
            model = message_in[0]
            if stage.guide.complete:
                pass
            else:
                model.stage = stage
                message_out = (model, None, None)
        #
        return message_out

        




    
