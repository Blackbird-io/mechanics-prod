#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2014
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: flow.starter

"""
Module defines a starter class for commencing Engine analysis.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
Starter               class for starting Engine analysis
====================  ==========================================================
"""




#imports
import datetime

import bb_settings

from data_structures.modelling.business_unit import BusinessUnit
from data_structures.modelling.line_item import LineItem
from data_structures.modelling.model import Model
from data_structures.system.messenger import Messenger




#globals
intro_line = LineItem("build or upload")
# intro_line.tags.add("start", "configuration")
# intro_line.guide.quality.set_standard(2)

#classes
class Starter:
    """

    Object prepares a (M, None, None) message at the beginning of an interview
    so that other parts of the Engine can commence work.
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    MR                    instance of Messenger

    FUNCTIONS:
    process()             main interface, put together (M, None, None) message
    ====================  ======================================================
    """

    def __init__(self):
        self.MR = Messenger()

    def process(self, message):
        """


        Starter.process(message) -> message


        Method always returns an (M,None,None) message. Method picks up any
        useful background information that the Portal sends along (e.g.,
        location, type of company associated with access code, etc.).

        If the inbound message is completely empty (_,_,_), method creates a
        new model. Method then starts the model and builds out a time line
        around either the current or globally fixed reference date.
        """

        ref_date = datetime.date.today()

        self.MR.prep(message)

        model = message[0]
        if model:
            model_name = model.portal_data["business_name"]
            if not model_name:
                model_name = bb_settings.DEFAULT_MODEL_NAME
            model.set_name(model_name)
            #starter can also do configuration from other parts of
            #user_context
        else:
            model = Model(bb_settings.DEFAULT_MODEL_NAME)

        model.start()
        model._ref_date = ref_date

        # officially ``start`` the model so that it never comes back here;
        # otherwise, starter.process() will destroy all existing model data.
        if not model.time_line.current_period:
            model.time_line.build(ref_date)

        if not model.get_company():
            company = BusinessUnit(model.tags.name)
            model.set_company(company)
            model.target = company
            # TODO: remove

        if not model.target.stage.path:
            model.target.stage.set_path()

        if not model.target.stage.focal_point:
            model.target.stage.path.append(intro_line.copy())
            model.target.stage.focal_point = intro_line.copy()

        message = (model, None, None)

        return message

        #SessionController will pass this message to an analyst, which will use Yenta
        #to select the best intro topic. As is, all models start with the same intro
        #topic, but in the future, the introduction can be customized by geography
        #or business type (based on sign-up code, for example).
