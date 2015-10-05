#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: data_structures.system.messenger
"""

Module defines Messenger class.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
Messenger

====================  ==========================================================
"""




#imports:
#n/a




#globals
#n/a

#classes
class Messenger:
    """

    This class provides a uniform interface for Blackbird environment messaging.
    
    ==========================  ================================================
    Attribute                   Description
    ==========================  ================================================

    DATA:
    activeModel                 storage for M in MQR message
    activeQuestion              storage for Q in MQR message
    activeReceiver              object designated to receive messages from
                                instance
    activeResponse              storage for R in MQR message
    liveQ                       filtered Q storage (question pending for user)
    messageIn                   message received by instance
    messageOut                  message instance prepares for sending out
    receivedMessages            record of received messages, with timestamps
    sentMessages                record of sent messages, with timestamps

    FUNCTIONS:
    clearMessageIn()            sets messageIn to None
    clearMessageOut()           sets messageOut to None
    clearMQR()                  sets activeModel,activeQuestion,activeResponse,
                                and liveQ to None
    generateMessage()           combines M,Q, and R elements into messageOut
    receive()                   stores specified message as messageIn
    send()                      runs receiver.receive on messageOut
    setReceiver()               sets receiver to specified object
    unpackMessage()             splits, stores M,Q, and R elements of message   
    
    ==========================  ================================================
    """
    def __init__(self):
        self.activeModel = None
        self.activeQuestion = None
        self.activeReceiver = None
        self.activeResponse = None
        self.liveQ = None
        self.messageIn = None
        self.messageOut = None
        self.receivedMessages = []
        self.sentMessages = []

    def clear(self):
        self.clearMessageIn()
        self.clearMessageOut()
        self.clearMQR()

    def clearMessageIn(self):
        """

        MR.clearMessageIn() -> None

        Sets instance's ``messageIn`` attribute to ``None``.
        """
        self.messageIn = None

    def clearMessageOut(self):
        """

        MR.clearMessageOut() -> None

        Sets instance's ``messageOut`` attribute to ``None``.
        """
        self.messageOut = None

    def clearMQR(self):
        """

        MR.clearMQR() -> None

        Method sets each of ``activeModel``, ``activeQuestion``,
        ``activeResponse``, and ``liveQ`` for instance to ``None``.
        """
        self.activeModel = None
        self.activeQuestion = None
        self.activeResponse = None
        self.liveQ = None

    def generateMessage(self, M = None, Q = None, R = None):
        """

        MR.generateMessage([M],[Q],[R]) -> None

        Method sets instance.messageOut to a 3-tuple of M,Q,R.
        """
        newMessage = (M,Q,R)
        self.messageOut = newMessage
        
    def receive(self, message):
        """

        MR.receive(message) -> None

        Method stores message in instance's ``messageIn``.
        """
        self.messageIn = message

    def prep(self, message):
        self.clear()
        self.receive(message)
        self.unpack()

##    def send(self, message = None):
##        """
##
##        MR.sent([message]) -> None
##
##        Method delivers message to instance's activeReceiver via
##        activeReceiver's ``receive`` method. MR.send() then appends a tuple
##        of the message and the current UMT time to the instance's
##        ``sentMessages``. Finally, method runs clearMessageOut() on instance.
##
##        Method uses self.messageOut if ``message`` as default message.        
##        """
##        if not message:
##            message = self.messageOut
##        self.activeReceiver.receive(message)
##        self.sentMessages.append((message,time.time))
##        self.clearMessageOut()
##
##    def setReceiver(self,rec):
##        """
##
##        MR.setReceiver(rec) -> None
##
##        Method checks whether rec has a ``receive`` attribute; if so, sets
##        instance's ``activeReceiver`` to rec. Raises AttributeError otherwise.
##        """
##        if getattr(rec,"receive",False):
##            self.activeReceiver = rec
##        else:
##            raise AttributeError("Receiver object missing receive() method")

    def unpack(self):
        """


        MR.unpack() -> None

        
        Method sets instance's activeModel, activeQuestion, and activeResponse
        attributes to the first, second, and third element in msg, respectively.        
        """
        msg = self.messageIn
        self.activeModel = msg[0]
        self.activeQuestion = msg[1]
        self.activeResponse = msg[2]
        if self.activeQuestion:
            self.liveQ = self.activeQuestion   
