#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: data_structures.system.messenger
"""

Module defines Messenger class, for basic handling and storage.
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

    Class provides basic message handling and storage functionality. Expects
    all messages to conform to (MQR) format. Class doesn't do any real,
    substantive introspection.
    ==========================  ================================================
    Attribute                   Description
    ==========================  ================================================

    DATA:
    activeModel                 storage for M in MQR message
    activeQuestion              storage for Q in MQR message
    activeResponse              storage for R in MQR message
    liveQ                       filtered Q storage (question pending for user)
    messageIn                   message received by instance
    messageOut                  message instance prepares for sending out

    FUNCTIONS: 
    clear()                     clear all state
    clearMessageIn()            sets messageIn to None
    clearMessageOut()           sets messageOut to None
    clearMQR()                  sets model, question, response to None
    generateMessage()           combines M,Q, and R elements into messageOut
    prep()                      clear, receive, unpack
    receive()                   stores specified message as messageIn
    send()                      runs receiver.receive on messageOut
    unpack()                    splits, stores M,Q, and R elements of message       
    ==========================  ================================================
    """
    def __init__(self):
        self.activeModel = None
        self.activeQuestion = None
        self.activeResponse = None
        self.liveQ = None
        self.messageIn = None
        self.messageOut = None

    def clear(self):
        """


        Messenger.clear() -> None


        Method clears message in, message out, and detail records.
        """
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
        """


        Messenger.prep(message) -> None


        Method clears instance, receives the message, and unpacks it. 
        """
        self.clear()
        self.receive(message)
        self.unpack()

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
