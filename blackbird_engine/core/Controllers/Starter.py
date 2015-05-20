#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2014
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: Controllers.Starter

"""
This module responds to the (_,_,_) message that kicks off every session.

The module always returns a MQ_ message.

The module contains an interface that's symmetric to Analyzer.

Module actions in detail: 
        gets a _,_,_ message
            Creates a model
            Names it something
            Creates a timeline in it
            configures default financials
            configures default bookmarks
            Adds a business unit to its current period
            Does some tagging stuff
            May be does some basic lifeCycle stuff?
            picks the first topic and question
        returns a M,Q,_ message

"""




#imports
import copy
import time
import BBGlobalVariables as Globals
import Managers.TopicManager as TopicManager

from DataStructures.Valuation.Analytics import Analytics
from DataStructures.Modelling.Model import Model
from DataStructures.Modelling.BusinessUnit import BusinessUnit
from DataStructures.Platform.Messenger import Messenger





#globals
#Intro Topic
intro_topic_name = "simple introduction for generic model."
startLM = Messenger()

#functions
def process(msg):
    if Globals.fix_ref_date == True:
        refDate = Globals.t0
    else:
        refDate = time.time()
    startLM.clearMessageOut()
    startLM.clearMessageIn()
    startLM.receive(msg)
    #
    M = msg[0]
    if M:
        model_name = M.portal_data["business_name"]
        if not model_name:
            model_name = Globals.default_model_name
        M.setName(model_name)
        #starter can also do configuration from other parts of
        #user_context
    else:
        M = Model(Globals.default_model_name)
    M.start()
    #make sure to officially ``start`` the model so that it never comes
    #back here; otherwise, all data will be lost
    #
    M.timeLine.build(refDate,
                     Globals.default_periods_fwd,
                     Globals.default_periods_back)
    topBU = BusinessUnit(Globals.default_unit_name)
    topBU.life.set_ref_date(refDate)
    atx = Analytics()
    topBU.setAnalytics(atx)
    M.currentPeriod.setContent(topBU)
    i_overview = topBU.financials.indexByName("overview")
    line_overview = topBU.financials[i_overview]
    line_overview.tag("Start")
    line_overview.tag("Configuration")
    M.interview.setFocalPoint(line_overview)
    def fFIXED(L):
        result = False
        if L.guide.quality.current >= L.guide.quality.minStandard:
            result = True
        return result
    M.interview.setPointStandard(fFIXED)
    #
    message = (M, None, None)
    #
    #run intro topic
    intro_topic_bbid = TopicManager.local_catalog.by_name[intro_topic_name]
    intro_topic = TopicManager.local_catalog.issue(intro_topic_bbid)
    message = intro_topic.process(message)
    #
    return message

