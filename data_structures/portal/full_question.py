# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL
# Blackbird Environment
# Module: data_structures.portal.full_question
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

import bb_exceptions

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

    FullQuestion objects with a single (vs mixed) type automatically carry the
    maximum permitted number of elements in their input array. By default, the
    first element is turned on (element._active == True) and the others are
    turned off. For such regular-way questions, our topics never have to add
    elements manually; they can just toggle the ``_active`` setting.

    See the Engine-Wrapper API for more details on how the Portal responds to
    various FullQuestion attributes. 
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
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
    build_basic_array()   build an array for single-type elements
    build_custom_array()  build an array of elements from spec; can be mixed
    check()               check if elements match instance type and length
    copy()                returns new obj with deep id, tags, array, and context
    set_condition()       sets instance gating element to valid binary spec
    set_prompt()          sets prompt to formatted custom if possible, or basic
    update()              updates instance attributes from MiniQuestion
    ====================  ======================================================
    """
    #class attributes
    _MAX_ELEMENTS = 5

    _klasses = dict()
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
        self.show_if = None
        self.source = None
        self.topic_name = None
        self.transcribe = False
        #
        self.basic_prompt = None
        self.context = dict()
        self.custom_prompt = None

    class _ProgressDescriptor:
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
                raise bb_exceptions.ManagedAttributeError(c)

    progress = _ProgressDescriptor()
        
    def _check_length(self):
        """


        FullQuestion._check_length() -> bool

        
        Return True if the number of elements in instance's input_array is less
        than or equal to the maximum permitted, False otherwise. 
        """
        result = False
        if len(self.input_array) <= self._MAX_ELEMENTS:
            result = True
        #
        if not result:
            c = "\nError in question ``%s``:\n"
            c += "(source: %s)\n\n"
            c += "Array length exceeds maximum.\n"
            c = c % (self.tags.name, self.source)
            raise bb_exceptions.QuestionFormatError(c)
        #
        return result            

    def _check_type(self):
        """


        FullQuestion._check_types() -> bool


        Return True if the instance type and sub_type matches the profile of
        each of the elements in instance's input_array, False otherwise.

        NOTE: Method will return False if elements are homogenous but instance
        type is set to ``mixed``. We do this to encourage disciplined question
        crafting. Otherwise, we may start to always label questions ``mixed``. 
        """
        result = False
        #
        types_in_array = set()
        sub_types_in_array = set()
        for element in self.input_array:
            types_in_array.add(element.input_type)
            sub_types_in_array.add(element.input_sub_type)
##        #
##        if self.conditional:
##            if self.input_type != "binary":
##                types_in_array.remove("binary")
##        # Skip this step now that we store gating specs at instance.show_if
        #
        types_in_array = sorted(types_in_array)
        sub_types_in_array = sorted(sub_types_in_array)
        #
        if len(types_in_array) > 1:
            if self.input_type == "mixed":
                result = True
                #enforce discipline; only use "mixed" if actually mixing types,
                #don't use it as a catch-all
        else:
            if self.input_type == types_in_array[0]:
                if self.input_sub_type == sub_types_in_array[0]:
                    result = True

        if self.input_type == "table":
            result = True

        if not result:
            c = "\nError in question ``%s``:\n"
            c += "(source: %s)\n\n"
            c += "Element types don't match question type.\n"
            c = c % (self.tags.name, self.source)
            c += "\tquestion type: \t\n%s\n"
            c = c % self.input_type
            c += "\telement type(s): \t\n%s\n"
            c = c % sorted(types_in_array)
            raise bb_exceptions.QuestionFormatError(c)

        return result
    
    def _set_type(self, input_type, input_sub_type=None):
        """


        FullQuestion._set_type(input_type[, input_sub_type=None])-> None


        Set instance attributes to arguments, raise QuestionFormatError if they
        don't fit.
        """
        if input_type == "mixed":
            if input_sub_type:
                c = "``mixed`` questions do not support subtypes."
                raise bb_exceptions.QuestionFormatError(c)
            self.input_type = input_type
        elif input_type == "table":
            self.input_type = input_type
        else:
            if input_type in self._klasses:
                self.input_type = input_type
                permitted_subs = self._klasses[input_type]._sub_types
                if input_sub_type in permitted_subs:
                    self.input_sub_type = input_sub_type
                else:
                    c = "``%s`` is not a valid %s subtype."
                    c = c % (input_sub_type, input_type)
                    raise bb_exceptions.QuestionFormatError(c)
                
    def build_basic_array(self, input_type, input_sub_type=None,
                          active_count=1):
        """


        FullQuestion.build_basic_array() -> None


        Clear existing contents, then add the maximum permitted number of
        type-specific elements and set the instance type accordingly. 
        
        Method sets _active == True for the first ``active_count`` elements. 
        """
        self.input_array.clear()
        base_klass = self._klasses[input_type]
        for i in range(self._MAX_ELEMENTS):
            element = base_klass()
            if i < active_count:
                element._active = True
            if input_sub_type:
                element.set_sub_type(input_sub_type)
            self.input_array.append(element)
        #
        self._set_type(input_type, input_sub_type)

    def build_custom_array(self, array_spec, input_type, input_sub_type=None,
                           ignore_fixed=False):
        """


        FullQuestion.build_custom_array() -> None

                                       
        Clear existing contents, then add elements as specified in spec.

        Spec may be partial or complete. Method uses question-level type and
        sub_type to try and build out the array for partial specs. 

        Method expects spec to follow API InputElement schema. Method sets
        all elements to _active == True by default. Spec can override that
        setting.

        Method passes ``ignore_fixed`` value to element.update(): if True,
        update will only update attributes in element._var_attrs. 
        """
        self.input_array.clear()
        array_spec = copy.deepcopy(array_spec)
        #make a deep copy so can modify array itself or element dictionaries
        #
        for i in range(len(array_spec)):
            e_spec = array_spec[i]
            try:
                e_type = e_spec.pop("input_type")
            except KeyError:
                e_type = input_type            
            element = self._klasses[e_type]()
            #
            try:
                e_sub_type = e_spec.pop("input_sub_type")
                #details may not 
            except KeyError:
                e_sub_type = input_sub_type
            element.set_sub_type(e_sub_type)
            #sub_types are write-protected; use dedicated setting interface
            #
            element._active = True
            #assume that all elements are active by default; spec can
            #override if necessary
            element.update(e_spec, ignore_fixed)
            self.input_array.append(element)
        #
        self._set_type(input_type, input_sub_type)
                
    def check(self):
        """


        FullQuestion.check() -> bool


        Return True if both check_types() and check_length() are True, False
        otherwise. 
        """
        result = all([self._check_type(), self._check_length()])
        return result
    
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
        result.tags = self.tags.copy()
        return result

    def set_condition(self, binary_spec):
        """


        FullQuestion.set_condition() -> None


        Create a binary gating element that matches the spec, assign to
        instance.show_if.
        """
        gating_element = self._klasses["binary"]()
        gating_element._active = True
        gating_element.update(binary_spec)
##        self.input_array.insert(0, gating_element)
##        self.conditional = True
        self.show_if = gating_element

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
    
    def update(self, mini_q):
        """


        FullQuestion.update() -> None


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

