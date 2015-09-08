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
class analyzerLM(Messenger):
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
    upController()        check if message ready for return
    wrapInterview()       clean up / storage to run prior to end
    ====================  ======================================================
    """
    
    def __init__(self):
        Messenger.__init__(self)
        self.maxCycles = 20
        self.upMessage = None
        self.upReady = False
        self.upStatus = None
        
    def downStream(self,message,trace=False):
        """

        aLM.downStream(message[,trace=False]) -> message

        Method evaluates a message and generates the next one. downStream()
        first passes a message to upController to determine if additional
        review is necessary. upController notes its conclusion on the instance's
        ``upReady`` attribute and returns the message (potentially w some
        changes). If the message is upReady at that point, method returns it as
        is. Otherwise, downStream() attempts to process the message further
        using lower-level resources: topics and the Yenta module.

        Method stops processing on the first upworthy message (as determined by
        upController) or the conclusion of the maxCycles number of analytical
        attempts. 
        
        """
        n = 0
        print("in Analyzer.downStream")
        message = self.upController(message)
        #upController checks message status and calls InterviewController. IC
        #updates M.guide.focalPoint if necessary, or changes the message (if it
        #decides to terminate interview). upController then checks status again
        #in case message changed and notes the status on the instance. 
        while n < self.maxCycles and not self.upReady:
            print("starting analysis loop #",n)
            M = message[0]
            Q = message[1]
            R = message[2]
            if self.upStatus == Globals.status_pendingResponse:
                topic_bbid = M.interview.transcript[-1][0]["topic_bbid"]
                T = TopicManager.local_catalog.issue(topic_bbid)
                message = T.process(message)
                #
            elif self.upStatus == Globals.status_topicNeeded:
                T = yenta.select_topic(M)
                if T:
                    message = T.process(message)
                else:
                    pass
                    #Yenta.select_topic() returned None for Topic, which means
                    #it couldn't find any matches in the Topic Catalog. In such
                    #an event, Yenta notes dry run on focal point and IC shifts
                    #to the next focal point
            message = self.upController(message)
            #if upController determines messageOut is suitable for delivery, it
            #will toggle self.upReady and the loop will not run again
            n = n + 1
        print("finished analysis loop")
        print("n is: ",n)
        return message
        
    def receive(self,message):
        """

        aLM.receive(message) -> None

        Method runs Platform.Messenger.receive() on message
        """
        Messenger.receive(self,message)
        #Messenger.receive records the incoming message in self.messageIn

    def reset(self):
        """

        aLM.reset() -> None

        Method clears instance message-dependent state and prepares the instance
        to process a new message
        """
        self.upReady = False
        self.upStatus = None
        self.clearMessageOut()  
        self.clearMessageIn()

    def setStatus(self,newStatus):
        """

        aLM.setStatus(newStatus) -> None

        Method sets instance.status to the new status.
        """
        self.upStatus = newStatus

    def upController(self,message):
        """

        aLM.upController(message) -> message

        Method checks whether the message is of a type that can be returned to
        higher-level modules. Only two types of messages are suitable for upward
        return:
           1) those with an open question for the user
           2) those signaling that the interview is complete

        aLM.upC() uses Globals.checkMessageStatus() to identify the format of a
        given message. If the message needs a topic, .upC() then passes it to 
        InterviewController for further processing. IC returns message with
        the focal point for further analysis ``highlighted`` on M.guide. IC may
        determine that the model needs no further analysis and return an
        endSession message.

        Accordingly, upon receiving IC's digested version of
        the message, upController() checks its status again to check if it
        should continue or terminate the interview. It notes accordingly on
        instance.upReady and upStatus and returns the latest version of the
        message.

        In the event upController encounters a message in the endSession format,
        it will run self.wrapInterview() on the message before returning it.
        """
        checkStatus = Globals.checkMessageStatus
        upWorthy = {Globals.status_pendingQuestion, Globals.status_endSession}
        mStatus = checkStatus(message)
        if mStatus == Globals.status_topicNeeded:
            message = interviewer.process(message)
            mStatus = checkStatus(message)
            #only run one message transformation per call (via IC.process(msg))
        if mStatus == Globals.status_endSession:
            message = self.wrapInterview(message)
            mStatus = checkStatus(message)
        if mStatus in upWorthy:
            self.upReady = True
        self.setStatus(mStatus)
        return message        

    def wrapInterview(self,message):
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
    

aLM1 = analyzerLM()

def process(smMessageIn):
    """

    Analyzer.process(smMessageIn) -> message

    This function provides the main interface with the Analyzer module for other
    objects in the Blackbird environment. On a process(message) call, Analyzer
    checks if additional user input is necessary to build out the model (M in
    MQR). If user input is necessary, Analyzer generates a message suitable for
    such input. If the model is complete, Analyzer generates a message carrying
    the completed model and the END_INTERVIEW sentinel in R position.

    Logic works by delegation. 
    """
    aLM1.reset()
    aLM1.receive(smMessageIn)
    messageOut = aLM1.downStream(smMessageIn)
    #downStream will keep running until it formulates an upWorthy msg
    return messageOut

#NOTE: at some point, Analyzer should store the tag catalog?
#SessionManager should do it if it gets an EndSession message

aLM2 = analyzerLM()
aLM2.controller = AnalyticsController()

def atx_up(self,msg):
    msg = self.controller.process(msg)
    mStatus = Globals.checkMessageStatus(msg)
    self.setStatus(mStatus)
    M = msg[0]
    self.upReady = M.analytics.guide.complete
    return msg

aLM2.upController = atx_up.__get__(aLM2)

def process_analytics(msgIn, trace = False):
    #half-baked
    M = msgIn[0]
    M.currentPeriod.content.fillOut()
    M.analytics = M.currentPeriod.content.valuation
    #super simple way of selecting which period to run analytics for
    #can have a function that does that
    aLM2.reset()
    aLM2.receive(msgIn)
    msgOut = aLM2.downStream(msgIn)
    return msgOut
    
def process_summary(message, trace = False):
    """


    process_summary(message, trace = False) -> message


    Function takes an MQR message, runs analytics, runs a pre-designated
    summary topic, and returns the result. 
    """
    summary_topic_id = yenta.TM.local_catalog.by_name[summary_t_name]
    summary_topic = yenta.TM.local_catalog.issue(summary_topic_id)
    message = summary_topic.process(message)
    return message





    
