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
Engine to learn patterns from manual question selection.
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

    #FullQuestion objects automatically carry their maximum number of typed
    #input elements, so that Topic authors never have to add any manually. By
    default, the first element is turned on (element._active == True) and the
    others are turned off. Topics can modify these settings when they wish.

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
    _klasses["binary"] = BinaryInput
    _klasses["bool"] = BoolInput
    _klasses["choice"] = ChoiceInput
    _klasses["date"] = DateInput
    _klasses["date-range"] = DateRangeInput
    _klasses["number"] = NumberInput
    _klasses["number-range"] = NumberRangeInput
    _klasses["time"] = TimeInput
    _klasses["time-range"]= TimeRangeInput
    _klasses["text"] = TextInput

    #
    _klasses["number"]["sub_types"] = 
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
        
    def build_basic_array(self, input_type,
                          input_sub_type = None, active_elements = 1):
        """
        -> None
        clears existing array, then adds the maximum number of elements of requested
        type and sub_type.
        """
        self.input_array.clear()
        base_klass = new_question._klasses[input_type]
        for i in range(new_question._max_elements):
            element = base_klass()
            if i < active_elements:
                element._active = True
            if input_sub_type:
                element.input_sub_type = input_sub_type
            self.input_array.append(element)

    def build_custom_array(self, array_spec, active_elements = 1):
        """

        clears instance input_array and rebuilds from spec
        raises error if multiple types of questions or type doesnt match

        method sets ``active_count`` elements to _active == True, though
        spec can override that. 
        """
        self.input_array.clear()
        array_spec = array_spec.copy()
        #make a copy so we can remove data
        #
        for i in range(len(array_spec)):
            e_spec = array_spec[i]
            e_type = e_spec.pop("input_type")
            element = self._klasses[e_type]()
            if i < active_elements:
                element._active = True
            #set default active status first; e_spec can override
            element.update(e_spec)           
            self.input_array.append(element)

    def check(self):
        """


        FullQuestion.check() -> bool


        Return True if both check_types() and check_length() are True, False
        otherwise. 
        """
        result = all(self.check_types(), self.check_length())
        return result

    def check_length(self):
        """


        FullQuestion.check_length() -> bool

        
        Return True if the number of elements in instance's input_array is less
        than or equal to the maximum permitted, False otherwise. 
        """
        result = False
        if len(self.input_array) <= self._max_elements:
            result = True
        #
        return result            

    def check_types(self):
        """


        FullQuestion.check_types() -> bool


        Return True if the instance type matches the profile of each of the
        elements in instance's input_array, False otherwise.

        NOTE: Method will return False if elements are homogenous but instance
        type is set to ``mixed``. We do this to encourage disciplined question
        crafting. Otherwise, we may start to always label questions ``mixed``. 
        """
        result = False
        #
        types_in_array = set()
        for element in self.input_array:
            e_type = element["input_type"]
            types_in_array.add(e_type)
        #
        if self.conditional:
            if self.input_array["input_type"] == "binary":
                types_in_array.remove("binary")
        #
        types_in_array = sorted(types_in_array)
        if len(types_in_array) > 1:
            if self.input_type == "mixed":
                result = True
                #enfore discipline; only use "mixed" if actually mixing types,
                #don't use it as a catch-all
        else:
            if self.input_type == types_in_array[0]:
                result = True
        #
        return result
    
    def set_condition(self, binary_spec):
        """


        FullQuestion.set_condition(binary_spec) -> None


        Create a binary gating element that matches the spec, insert at the
        beginning of the instance input array.
        """
        gating_element = self._klasses["binary"]()
        gating_element.update(binary_spec)
        self.input_array.insert(0, gating_element)
        self.conditional = True

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

