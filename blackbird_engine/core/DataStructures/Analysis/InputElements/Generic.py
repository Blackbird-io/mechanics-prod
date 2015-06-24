#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: Analysis.Inputs.GenericInput
"""

Module defines the GenericInput class. GenericInput objects serve as ancestors
for more specialized input-definition objects. GenericInput objects restrict
attribute addition and modification via a whitelist (``_var_attrs``). 

====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
GenericInput          Describes on-screen field where user can input a response 
====================  ==========================================================
"""




#imports
import copy

import BBExceptions

from ..ReadyForPortal import ReadyForPortal



#globals
#n/a

#classes
class GenericInput(ReadyForPortal):
    """

    The GenericInput class allows financial analysts to specify how a person
    answering Questions through the Portal should enter their response. 

    The WrapperManager transforms GenericInput objects and their descendants
    into API-spec InputElement objects prior to delivering them to the Wrapper. 

    Since the Portal can interpret only a finite set of attributes (defined
    here), GenericInput objects restrict how Engine users may create or modify
    attributes. Standard assignment (``x.y = z``) syntax thus only works for
    those attributes listed in the ``_var_attrs`` whitelist.

    For GenericInput objects, the whitelist includes most class-specific
    attributes. Other, specialized descendants restrict the parameters further.     
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    _var_attrs            tuple; names of attributes that accept new values
    _active               bool; whether Portal should display this input element
    allow_other           bool; can user provide free-form entry for choice type
    entries               list; response choices
    input_type            string; None for this class 
    input_sub_type        string or None; contextual hint for Web Portal
    line_value            decimal; value of line user should verify
    main_caption          string; browser displays main_caption above the input
    multi                 bool; can user select multiple options
    r_max                 decimal; upper bound on user input
    r_min                 decimal; lower bound on user input
    response              obj; placeholder, reponse appears on PortalResponse
    shadow                obj; light value displayed in field before response
    shadow_2              obj; for range-type elements, shadow for second box
    size                  string; controls size of text box
    show_if               None or binary InputElement; shows main if truthy
    toggle_caption_false  text that appears when toggle is set to False
    toggle_caption_true   text that appears when toggle is set to True
    user_can_add          whether user can add more input fields (like rows)

    FUNCTIONS:
    __setattr__()         whitelisted attrs set through superclass, else error
    __str__()             prints each attribute in whitelist on own line
    check_response()      check whether response fits pattern and min-max range
    copy()                returns a shallow copy, w deep copy of other_element
    format_response()     take string, return object formatted per type and API
    set_response()        take string, format, set as target response
    update()              update instance attributes to spec values
    ====================  ======================================================
    """
    def __init__(self, var_attrs = None):
        if var_attrs == None:
            var_attrs = ("_active",
                         "allow_other",
                         "entries",
                         "line_value",
                         "main_caption",
                         "multi",
                         "r_max",
                         "r_min",
                         "response",
                         "shadow",
                         "shadow_2",
                         "show_if",
                         "size",
                         "toggle_caption_false",
                         "toggle_caption_true",
                         "user_can_add")
            #tuple for immutability
        else:
            var_attrs = set(var_attrs) | {"_active", "response"}
            var_attrs = tuple(sorted(var_attrs))
        #
        ReadyForPortal.__init__(self, var_attrs)
        #       
        self.__dict__["_active"] = False
        self.__dict__["allow_other"] = False
        self.__dict__["entries"] = None
        self.__dict__["input_type"] = None
        self.__dict__["input_sub_type"] = None
        self.__dict__["line_value"] = None
        self.__dict__["main_caption"] = None
        self.__dict__["multi"]= False
        self.__dict__["r_max"] = None
        self.__dict__["r_min"] = None
        self.__dict__["response"] = None
        self.__dict__["shadow"] = None
        self.__dict__["shadow_2"] = None
        self.__dict__["show_if"] = None
        self.__dict__["size"] = None
        self.__dict__["toggle_caption_false"] = None
        self.__dict__["toggle_caption_true"] = None
        self.__dict__["user_can_add"] = False
        #set default values manually through dict to make sure they do not
        #bounce when a subclass passes in a smaller attribute whitelist

    def __str__(self, tab = None):
        result = ""
        name_field_width = 25
        dots = 8
        attrs_to_print = (["input_type", "input_sub_type"] +
                          list(self._var_attrs))
        for attr_name in attrs_to_print:
            attr_val = getattr(self,attr_name)
            line = "\t" + str(attr_name) + ":"
            line += ((name_field_width - len(attr_name)) + dots) * "."
            line += str(attr_val) + "\n"
            result = result + line
        return result                       

    def check_response(self, proposed_response):
        """


        GenericInput.check_response(proposed_response) -> bool


        Method return True if proposed_response satisfies type-specific format
        conditions, False otherwise.

        Basic default routine checks if proposed_response is an instance of
        list with a length of at least 1.        
        """
        result = None
        if (isinstance(proposed_response,list) and len(proposed_response) > 0):
            result = True
        else:
            result = False
        return result
    
    def copy(self):
        """


        GenericInput.copy() -> obj


        Method returns a new instance of the original's class, with the same
        attributes and values. Result.other_element is a deep copy of original;
        other attribute values are shallow copies. 
        """
        result = self.__class__()
        result.__dict__["other_element"] = copy.deepcopy(self.other_element)
        return result

    def format_response(self, raw_response):
        """


        GenericInput.format_response(raw_response) -> list


        Method turns raw_response into an object that satisfies the Engine API
        specifications for a ResponseElement of the instance's input type and
        sub_type.

        The default, most-basic version of a ResponseElement-compatible object
        is a len-1 list of the raw_response. 

        Descendant classes may customize the first step of the routine to
        include more complex processing. For example, a range class would split
        the string along a comma into two component strings. 
        """
        adj_response = [raw_response]
        return adj_response
            
    def set_response(self, proposed_response, target):
        """


        GenericInput.set_response(proposed_response, target) -> None


        Method sets target.response to a clean, formatted version of proposed
        response. Raises ResponseFormatError if proposed response does not fit
        element parameters (e.g., exceeds maximum) or if any other errors arise
        during routine.

        Target should be a dictionary-type object that supports keywords.
        
        INACTIVE: Target can be any object that supports the ``response``
        attribute. If ``target`` left blank, method sets response on instance.

        SimplePortal will feed in individual ResponseElements as ``target``
        during command line operation.

        Method also sets target input_type and input_sub_type to match instance.
        
        INACTIVE: Method uses object.__setattr__() to modify target in case the
        object blocks normal attribute setting. 
        """
        #
        #blocks covering ResponseElement objects (vs plain dictionaries)
        #commented out
        #
##        if not target:
##            target = self
        #
        try:
            adj_response = self.format_response(proposed_response)
            if self.check_response(adj_response):
                #
                clean_response = adj_response
                #
                target["response"] = clean_response
                target["input_type"] = self.input_type
                target["input_sub_type"] = self.input_sub_type
                #                
##                object.__setattr__(target,
##                                   "response",
##                                   clean_response)
##                object.__setattr__(target,
##                                   "input_type",
##                                   self.input_type)
##                object.__setattr__(target,
##                                   "input_sub_type",
##                                   self.input_sub_type)
                #
            else:
                c = "Response does not satisfy element parameters."
                raise BBExceptions.ResponseFormatError(c)
        except Exception as E:
            c = "user response does not fit input element."
            raise BBExceptions.ResponseFormatError(c, E)

    def update(self, spec):
        """


        GenericInput.update(spec) -> None


        Method updates instance attributes to values in spec. Method expects
        ``spec`` to be a dictionary with attribute name keys. 
        """
        for attr_name in spec:
            spec_val = spec[attr_name]
            setattr(self, attr_name, spec_val)
            
                
            
