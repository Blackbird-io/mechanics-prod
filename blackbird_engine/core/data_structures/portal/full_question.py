#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: data_structures.portal.full_question
"""

Module defines FullQuestion class. FullQuestion objects provide all details
necessary for Portal to display the question properly to a user. FullQuestion
objects also provide identification and charactertization attributes that allow
Engine to learn pattenrs from manual question selection.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
q_types               list of input_types that Portal recognizes
q_entry               list of keys for each type entry in FullQuestion._types

FUNCTIONS:
n/a

CLASSES:
FullQuestion          Object that defines question for both Engine and Portal
====================  ==========================================================
"""





#imports
import copy
import decimal

import BBExceptions
import BBGlobalVariables as Globals

from .input_elements.binary import BinaryInput
from .input_elements.bool import BoolInput
from .input_elements.choice import ChoiceInput
from .input_elements.date import DateInput
from .input_elements.date_range import DateRangeInput
from .input_elements.number import NumberInput
from .input_elements.number_range import NumberRangeInput
from .input_elements.text import TextInput
from .input_elements.time import TimeInput
from .input_elements.time_range import TimeRangeInput

from ..system.bbid import ID
from ..system.tags import Tags




#globals
decimal.getcontext().prec = 6

q_types = ["binary",
           "bool",
           "choice",
           "date",
           "date-range",
           "number",
           "number-range",
           "time",
           "time-range",
           "text"]

q_entry = ["klass",
           "sub_types"]

#classes
class FullQuestion:
    """

    Class defines object that stores all details relevant to both Engine in
    Portal environments for asking user a question. 

    The QuestionManager creates a FullQuestion for every module in the
    QuestionWarehouse and stores that FullQuestion in its catalog.

    Generally, a warehouse module will set some question attributes permanently
    (such as the prompt, where careful, simple wording matters a lot) and leave
    others for customization at run-time (context, individual array elements).

    See the Engine-Wrapper API for more details on how the Portal responds to
    various FullQuestion attributes. 
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    _max_elements         int; max length  ofinput_array, fixed per API
    _progress             Decimal; instance-level state for progress 
    _types                dict; CLASS, maps strings Portal knows to classes
    array_caption         string that appears above arrays of input_elements
    basic_prompt          default prompt for question
    comment               explanation string that appears below the prompt
    context               dictionary of customization data for custom_prompt
    custom_prompt         prompt keyed to format with context data
    id                    obj; instance of Platform.ID
    input_array           list of InputElement objects
    input_type            string, controls widgets displayed in browser
    input_sub_type        string, provides additional context for Portal
    prompt                main question
    progress              float; completion indicator for interview, 0< p <=1
    short                 string; 2-3 question summary for tracker panel
    source                relative path of conent module that described obj
    tags                  obj; instance of Platform.Tags, for naming & feedback
    topic_name            string; appears in user-facing browser outline
    transcribe            bool; whether portal should show question to lenders
    
    FUNCTIONS:
    copy()                returns new obj with deep id, tags, array, and context
    ProgressDescriptor()  manages class and instance progress attributes
    set_prompt()          sets prompt to formatted custom if possible, or basic
    set_type()            sets question type, populates input_array
    set_sub_type()        sets question sub_type, if fits input_type
    update()              updates instance attributes from MiniQuestion
    ====================  ======================================================
    """
    #class attributes
    _types = {k:dict.fromkeys(q_entry) for k in q_types}
    _types["binary"]["klass"] = BinaryInput
    _types["bool"]["klass"] = BoolInput
    _types["choice"]["klass"] = ChoiceInput
    _types["date"]["klass"] = DateInput
    _types["date-range"]["klass"] = DateRangeInput
    _types["number"]["klass"] = NumberInput
    _types["number-range"]["klass"] = NumberRangeInput
    _types["time"]["klass"] = TimeInput
    _types["time-range"]["klass"]= TimeRangeInput
    _types["text"]["klass"] = TextInput
    _types["number"]["sub_types"] = {"percent",
                                     "currency",
                                     "days",
                                     "weeks",
                                     "months",
                                     "years"}
    _types["number-range"]["sub_types"] = _types["number"]["sub_types"]
    _types["text"]["sub_types"] = {"email"}
    #
    _max_elements = 5
    
    def __init__(self):
        self.id = ID()
        self.tags = Tags()
        #
        self.array_caption = None
        self.comment = None
        self.input_array = []
        self.input_type = None
        self.input_sub_type = None
        self.prompt = None
        self._progress = 0
        self.short = None
        self.source = None
        self.topic_name = None
        self.transcribe = False
        #
        self.basic_prompt = None
        self.context = dict()
        self.custom_prompt = None

    class ProgressDescriptor:
        """

        Descriptor for ``progress`` attribute. Limits value to [0,100] range,
        stores it as integer on instance._progress.
        
        """
        def __get__(self,instance,owner):
            return instance._progress

        def __set__(self,instance,value):
            if  0 <= value <= 100:
                instance._progress = int(value)
            else:
                c = "Attribute requires value between 0 and 100, inclusive."
                raise BBExceptions.ManagedAttributeError(c)

    progress = ProgressDescriptor()

    def copy(self):
        """


        FullQuestion.copy() -> FullQuestion


        Method returns a new instance of FullQuestion with equivalent attribute
        values.

        Method first creates a shallow copy and then creates deep copies of
        values for ``context``, ``id`` and ``input_array``. Method also sets
        result.tags to a class-specific, rules-off copy of the instance tags
        object.
        """
        result = copy.copy(self)
        result.context = copy.deepcopy(self.context)
        result.id = copy.deepcopy(self.id)
        result.input_array = copy.deepcopy(self.input_array)
        result.tags = self.tags.copy(enforce_rules = False)
        return result

    def set_prompt(self):
        """


        FullQuestion.set_prompt() -> None


        Method sets instance prompt to a Portal- / browser-ready string.

        If instance specifies a custom_prompt, method attempts to format the
        custom_prompt with the context. Uses basic_prompt if context doesn't fit
        (raises KeyError) or if custom_prompt is blank.
        """
        if self.custom_prompt:
            try:
                self.prompt = self.custom_prompt.format(**self.context)
            except KeyError:
                self.prompt = self.basic_prompt
        else:
            self.prompt = self.basic_prompt

    def set_sub_type(self, sub_type):
        """


        FullQuestion.set_sub_type(sub_type) -> None


        Method sets instance.input_sub_type to argument. ``sub_type`` is
        usually a string. Instances must have type before they can have
        sub_type, so method raises error if instance.input_type != True.

        Method also raises error if the sub_type doesn't fit the instance type
        per the API (ie, sub_type is not in
        FullQuestion._types[instance type]["sub_types"]).
        """
        if not self.input_type:
            c = "Must specify type before sub_type."
            raise BBExceptions.QuestionFormatError(c)
        if sub_type in self._types[self.input_type]["sub_types"]:
            self.input_sub_type = sub_type
            for e in self.input_array:
                object.__setattr__(e, "input_sub_type", sub_type)
                #input_sub_type always restricted, must set manually
        else:
            c = "" 
            c += "Portal does not recognize %s as valid input_sub_type for\n"
            c += "%s."
            c = c % (sub_type,self.input_type)
            raise BBExceptions.QuestionFormatError(c)
        #
        #<-------------- should change this to work on a single element? or a pool of elements?
        #or should just do this on the element?
        #element.set_sub_type()
        #
        #
        
    def set_condition(self, show_if_rule):
        #<---------------------------------------------------------------------------------
        self.condition = True
        rule_element = BinaryInput()
        rule_element.update(show_if_rule)
        self.input_array.insert(0, rule_element)
        
    def set_type(self,input_type):
        """


        FullQuestion.set_type(input_type) -> None


        Method sets instance type to argument. ``input_type`` is usually a
        string. Method raises error if the type is not recognized by the Portal
        per Engine-Wrapper API (argument is not in FullQuestion._types). 
        """
        if input_type not in self._types.keys():
            c = "Portal does not recognize %s as valid input_type."
            c = c % input_type
            raise BBExceptions.QuestionFormatError(c)
        else:
            self.input_type = input_type
            self.input_array = []
            for i in range(self._max_elements):
                new_element = self._types[input_type]["klass"]()
                self.input_array.append(new_element)

        #if this is ``mixed``, should create a blank array
        #content modules should only specify "mixed" in advanced config
        #should still start with a base type.
        #then, if mixed, QM can pick out elements based type from the FQ._types thing
        #

    def to_engine(self, portal_question):
        """
        -> FullQuestion
        take an API PortalQuestion schema and create an instance that fits
        """
        if mixed:
            #delegate to specialized function
        else:
            
            
        

    def update(self,mini_q):
        """


        FullQuestion.update(mini_q) -> None


        Method walks through mini_q.__dict__ and for True values, sets matching
        attributes on instance to the mini_q value. Method skips skip_attrs.

        NOTE: skip_attrs == ["id","tags"]
        If implementing runtime-to-catalog tag inheritance, adjust skip_attrs. 
        """
        skip_attrs = ["id","tags"]
        for (attr_name, attr_val) in mini_q.__dict__.items():
            if attr_name in skip_attrs:
                continue
            else:
                if attr_val:
                    setattr(self, attr_name, attr_val)
    
        

