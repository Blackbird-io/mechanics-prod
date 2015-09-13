#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2014
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: Analyzer

"""

This module gets a message and processes it until it gets a new message suitable
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
prepares it for use. 

====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
aCR                   instance of PlatformComponents.Connector class
aLM1                  instance of analyzerLM class

FUNCTIONS:
class analyzerLM()    class w message introspection and transformation methods
connectAll()          connects aCR to a connector object
prepareTopic()        connects topic's connecto to aCR
process()             evaluates message, returns next one

====================  ==========================================================
"""




#imports
import BBGlobalVariables as Globals
import DataStructures.Platform as Platform

from Managers import TopicManager

from .yenta import Yenta

from .analytics_controller import AnalyticsController
from .interviewer import Interviewer




#globals
yenta = Yenta()
interviewer = Interviewer()
Messenger = Platform.Messenger.Messenger

TopicManager.populate()
#TM.populate() should be a no-op here because Yenta will have already done so
#and TM.local_catalog.populated will be True accordingly.
summary_t_name = "basic model summary, annualized current with capex"

#classes    
class FlowController(Messenger):
    """

    Class of objects that combine all functions necessary to go from one message
    to another.
    
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    maxCycles             int; max number of attempts before return
    upReady               bool; is current message ready for return 
    upStatus              specific status of message (static)

    FUNCTIONS:
    downStream()          evaluate message, generate the next one
    receive()             unpack and store a message
    reset()               clear state to default
    setStatus()           store message status on instance
    choose_direction()    point message to more analysis or portal
    wrapInterview()       clean up / storage to run prior to end
    ====================  ======================================================
    """
    
    def __init__(self):
        Messenger.__init__(self)
        self.max_cycles = 20
        self.needs_work = True
        self.status = None

    def reset(self):
        """

        aLM.reset() -> None

        Method clears instance message-dependent state and prepares the instance
        to process a new message
        """
        self.ready_for_portal = False
        self.status = None
        self.clearMessageOut()  
        self.clearMessageIn()

    def setStatus(self,newStatus):
        """

        aLM.setStatus(newStatus) -> None

        Method sets instance.status to the new status.
        """
        self.status = newStatus

    def choose_direction(self,message):
        """


        FlowController.choose_direction(message) -> message
        

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
        self.setStatus(status)
        return message

    def work_on_model(self, message):
        """
        #work_on_model()


        FlowController.work_on_model(message) -> message


        Method works to improve the model until it's either good enough to
        consider done, or a question for the user comes up. 
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
                topic = TopicManager.local_catalog.issue(topic_bbid)
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
        print("finished analysis loop after %s passes" % n)
        return message

    def wrap_interview(self,message):
        """
        
        aLM.wrapInterview(message) -> message

        Method runs process_summary to summarize the model.

        More generally, wrapInterview() performs clean up, storage, and/or
        transformation logic on messages signaling the end of an interview
        before they go out to higher level modules and the user.

        For example, wrapInterview() can insert final questions or flag certain
        items for follow-up or review. 
        """
        M = message[0]
        Q = message[1]
        R = message[2]
        #
        #use M,_,_ here to avoid errors from incorrect wrap calls by Topic
        #scenarios (ie to make sure that if scenario wraps w wrap_topic, the
        #actual message this method returns still contains the original Q and
        #R)
        #
        #NOTE: Assumes that neither analytics nor summarization topics can
        #ask any questions.
        #
        alt_msg = (M, None, None)
        alt_msg = process_analytics(alt_msg)
        M = alt_msg[0]
        l_sum = M.analytics.credit.combined.get_summary()
        print(l_sum)
        #
        alt_msg = process_summary(alt_msg)
        #
        message = (M,Q,R)
        #        
        return message
    




    
