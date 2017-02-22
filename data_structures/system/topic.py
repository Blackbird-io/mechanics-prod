# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL

# Blackbird Environment
# Module: data_structures.system.topic
"""

Module defines Topic class, the basic unit of person-like analysis that the
Engine performs
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
Topic                 an object that asks questions and processes responses
====================  ==========================================================
"""




# Imports
import time
import uuid

import bb_exceptions
import bb_settings

import color_manager as ColorManager

from tools import for_messages as message_tools

from .bbid import ID
from .messenger import Messenger
from .tags import Tags




# Globals
ColorManager.populate()
user_stop = message_tools.USER_STOP


# Classes
class Topic:
    """

    Topic objects analyze and modify models.

    Topics receive MQR-format messages and process their contents into new
    messages. Topics focus on one particular insight into a given business and
    work by applying scenarios. Conceptually:

    scenario(msg_1) -> msg2

    Topics store and select scenarios based on the bbid of a question that they
    handle. A topic will call the scenario keyed to question A when the topic
    receives a message whose question.id.bbid == A.id.bbid. Scenarios thus
    correspond to the question whose response they digest.

    If a scenario is keyed to None, the Topic will call it to start analysis
    on a M,_,_ message. Each topic must also provide a special "end" scenario
    keyed to user_stop. Topics run end_scenarios when they receive a message
    where a user asked to stop the interview in the middle of a question. When
    a topic receives a user_stop message ((M,Q,End) or (M,_,End)), it should
    run its analysis entirely on assumptions.

    Scenarios can include nearly arbitrary logic but **must** always conclude
    by calling a ``wrap_x`` method on the topic at hand. The wrap methods
    serve distinct purposes:
     -- ``wrap_scenario()`` concludes scenarios that ask the user a question
     -- ``wrap_topic()`` concludes scenarios that finalize their work without
        further user input; this method exits the current topic
     -- ``wrap_to_stop()`` concludes end scenarios and generates the M,_,End
        message. Higher-level modules can then pass the M,_,End message to
        other topics to run follow-up assumption-based logic.

    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    formulas              dictionary of formulas used by the topic, by name
    id                    instance of ID class
    MR                    instance of Messenger class
    questions             dictionary of MiniQuestions used by topic, by name
    record_containers     list of objects that record_work() goes through
    record_strings        list of string attribute paths w respect to M
    record_on_exit        bool, whether record work should run on sign off
    scenarios             dictionary of scenarios used by topic, by q bbid
    source                relative path of content module that described obj
    tags                  instance of Tags class
    work_plan             dict; keys are line names, values are improvements in
                          quality

    FUNCTIONS:
    add_work_item()       register lineName:contribtion (k,v) pair in work_plan
    choose_scenario()     selects scenario by question id
    get_first_answer()    pulls out item from activeResponse[0]["response"][0]
    get_second_answer()   pulls out item from activeResponse[0]["response"][1]
    get_table_responses() pulls table output into a more useable format
    process()             unpacks message, apply scenario, return new message
    record_work()         increment quality for lineItems in work_plan
    reset_work_plan()     sets work_plan to a blank dictionary
    set_record_containers() generates a list of record objects from recStrings
    transcribe()          record a summary of the msg1-> scene -> msg2 change
    wrap_scenario()       generate a MQ_ message
    wrap_to_end()         generate a M_End message
    wrap_topic()          generate a M,_,_ message
    ====================  ======================================================
    """

    trace = True

    def __init__(self):
        self.CM = ColorManager
        self.id = ID()
        self.MR = Messenger()
        self.tags = Tags()
        self.formulas = None
        self.questions = None
        self.record_on_exit = True
        self.scenarios = None
        self.source = None
        self.work_plan = {}

    def add_work_item(self, line_name, contribution):
        """


        T.add_work_item(line_name,contribution)-> None


        Method records arguments in self.work_plan, with line_name as key and
        contribution as value. Method tags self with the line_name unless the
        tag already exists.
        """
        self.work_plan[line_name] = contribution
        if line_name not in self.tags.all:
            self.tags.add(line_name)

    def choose_scenario(self):
        """


        Topic.choose_scenario() -> obj


        Method returns a scenario from instance's ``scenarios`` dictionary.

        If Topic messenger carries an active question, method selects the
        scenario that matches that question's bbid.

        Default key for messages without an active question is None, which
        signifies that a Topic should begin its analysis from scratch in either
        a normal context (R == None) or following a user stop order
        (R == user_stop). In the latter case, method uses the active response
        as the key.
        """
        #
        # add response sensing logic here
        scenario_key = None
        active_scenario = None
        if self.MR.activeQuestion:
            q_bbid_string = self.MR.activeQuestion["question_id"]
            q_bbid = uuid.UUID(q_bbid_string)
            scenario_key = q_bbid
        else:
            if self.MR.activeResponse == user_stop:
                scenario_key = self.MR.activeResponse
        if scenario_key in self.scenarios.keys():
            active_scenario = self.scenarios[scenario_key]
        else:
            raise bb_exceptions.TopicDefinitionError()
        return active_scenario

    def get_first_answer(self):
        """

        Topic.get_first_answer() -> obj

        Method returns the first item of the first array element in the active
        response (activeResponse[0]["response"][0]).

        For example, suppose instance.activeResponse looks like this:

          activeResponse = [response_elem0, response_elem1, response_elem2]
          response_elem0["response"] = ["ford","gm","chrysler"]
          response_elem1["response"] = ["coke","pepsi"]
          response_elem2["response"] = ["door","window","ceiling"]

        Method will return "ford".
        """
        first_element = self.MR.activeResponse[0]
        answer = first_element["response"][0]
        return answer

    def get_second_answer(self):
        """

        Topic.get_second_answer() -> obj

        Method returns the second item of the first array element in the active
        response (activeResponse[0]["response"][1]).

        For example, suppose instance.activeResponse looks like this:

          activeResponse = [response_elem0, response_elem1, response_elem2]
          response_elem0["response"] = ["ford","gm","chrysler"]
          response_elem1["response"] = ["coke","pepsi"]
          response_elem2["response"] = ["door","window","ceiling"]

        Method will return "gm".
        """
        first_element = self.MR.activeResponse[0]
        answer = first_element["response"][1]
        return answer

    def get_table_responses(self):
        """

        Topic.get_table_responses() -> list

        Method returns a list of dictionaries containing key (main_caption):
        value (response) pairings for all rows in table.

        Example output:
            [{'commodity name': 'beef', 'cost per ticket': 2.0},
             {'commodity name': 'lettuce', 'cost per ticket': 0.5},
             {'commodity name': 'pickles', 'cost per ticket': 0.15}]
        """
        full_response_array = self.MR.activeResponse

        answer = list()
        for array in full_response_array:
            temp_dict = dict()
            for elem in array:
                temp_dict[elem['main_caption']] = elem['response'][0]

            answer.append(temp_dict)

        return answer

    def process(self, message_1):
        """


        Topic.process(message_1) -> message_2


        Method processes message with the instance and returns a new message.
        Works for both live interview and stop interview messages.

        Algorithm:
         -- clear instance messenger,
         -- receive message_1 through instance messenger,
         -- unpacks the message through messenger
         -- set record containers for instance
         -- select an active_scenario by running choose_scenario()
         -- run the active_scneario
         -- confirm the active_scenario wrapped correctly and posted a message
         -- transcribe the step
         -- return the message
        """
        self.MR.clearMQR()
        self.MR.receive(message_1)
        # sets MR.messageIn to message
        self.MR.unpack()

        active_scenario = self.choose_scenario()
        active_scenario(self)
        #
        # scenarios are unbound functions, so have to manually feed in topic
        # instance on call. scenario can then access any topic attributes
        # directly.
        #
        message_2 = self.MR.messageOut
        #
        # scenarios responsible for generating outbound message and posting it
        # to self.MR.messageOut. scenarios do so by calling wrap_scenario or
        # wrap_topic.
        #
        if not message_2:
            c = "No message at message out. Scenario did not wrap properly."
            raise bb_exceptions.TopicDefinitionError(c)
        self.transcribe(message_1, message_2, active_scenario)
        self.MR.clear()

        return message_2

    def record_work(self):
        """


        T.record_work() -> None


        Increments the guide.quality counter of any line item in Model's path
        or current top-level financials. Uses instance.work_plan for quality
        increments. Checks containers for both cased and casefolded versions of
        the line name.

        Method expects each record container to support build_tables().
        """
        model = self.MR.activeModel
        model.interview.record_work(self)

    def reset_work_plan(self):
        """


        T.reset_work_plan() -> None


        Method sets instance.work_plan to a blank dictionary.
        """
        self.work_plan = {}

    def transcribe(self, msg1, msg2, applied_scenario):
        """


        Topic.transcribe(msg1, msg2, applied_scenario) -> None


        Method records a mark in active model's transcript. The transcript
        allows human and machine readers to review and continue analysis.

        Each mark is a dictionary with the following keys:
        -- ``scenario_name``: name of scenario instance appplied to msg1
        -- ``q_in`` : question object from inbound message
        -- ``q_out``: question object from outgoing message
        -- ``r_in`` : response object from inbound message
        -- ``r_out`` : response object from outgoing message
        -- ``topic_bbid`` : bbid of instance
        -- ``timestamp`` : time of call

        When the Engine receives an MQR message, higher level modules use the
        topic_bbid in the last transcript entry to locate the topic that asked
        the question.
        """
        mark = {}
        mark["q_in"] = msg1[1]
        mark["q_out"] = msg2[1]
        mark["r_in"] = msg1[2]
        mark["r_out"] = msg1[2]
        mark["topic_bbid"] = self.id.bbid
        scene_name = getattr(applied_scenario, "name", None)
        if not scene_name:
            scene_name = applied_scenario.__name__
        mark["scenario_name"] = scene_name
        mark["timestamp"] = time.time()
        model = self.MR.activeModel
        mark["target_bu"] = model.target.tags.name
        model.transcribe(mark)
        model.target.used.add(self.id.bbid)

    def wrap_scenario(self, Q):
        """


        Topic.wrap_scenario() -> None


        Method pauses internal analysis to ask the user a question by generating
        a M,Q,_ message. M is the active model, Q is the argument.

        Method sets question progress to Model.interview.progress.
        """
        if not Q:
            c = "Topic.wrap_scenario() requires a valid question object to run."
            raise bb_exceptions.TopicOperationError(c)
        self.MR.liveQ = Q
        M = self.MR.activeModel
        R = None
        #
        # set progress status on Q; always increment progress by 1 for every new
        # question the user sees to show that they are moving along
        #
        new_progress = \
            M.interview.progress + \
            bb_settings.MINIMUM_PROGRESS_PER_QUESTION
        M.interview.set_progress(new_progress)
        Q.progress = new_progress
        #
        self.MR.generateMessage(M, Q, R)

    def wrap_to_stop(self):
        """


        Topic.wrap_to_stop() -> None


        Method runs instance.wrap_topic(), then changes outbound message to
        (M,_,user_stop).
        """
        self.wrap_topic()
        M = self.MR.messageOut[0]
        Q = None
        R = user_stop
        self.MR.generateMessage(M, Q, R)

    def wrap_topic(self):
        """


        Topic.wrap_topic() -> None


        Method increments line items in model path according to work_plan and
        exits topic by generating a M,_,_ message. Message uses activeModel from
        instance messenger.

        A topic can signal that it has completed its analysis by returning a
        (M,None,None) message. The Analyzer module does not send M _ _ messages
        back out to the portal. Instead, Analyzer internally selects a different
        topic and passes the message on to it.
        """
        print(self.tags.name)

        if self.record_on_exit:
            self.record_work()
        M = self.MR.activeModel
        Q = None
        R = None
        self.MR.generateMessage(M, Q, R)
