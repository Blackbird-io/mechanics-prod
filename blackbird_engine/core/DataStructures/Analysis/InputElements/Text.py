#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: DataStructures.Analysis.Inputs.TextInput
"""

Module defines the TextInput class. 

====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
TextInput             Describes a text input field.
====================  ==========================================================
"""




#imports
from .Generic import GenericInput




#globals
#n/a

#classes
class TextInput(GenericInput):
    """

    The TextInput object defines a text box. 

    **A TextInput response is a list of 1 string**

    The TextInput object descends from GenericInput and tightens the
    ``_var_attrs`` whitelist to the following attributes:
    
     -- main_caption
     -- shadow
     -- show_if
     -- size
     -- user_can_add

    ``size`` can either be None or "long". If ``size`` is None (default), Portal
    will display a small text box, suitable for approximately 50 characters. For
    ``long`` instances, Portal will display a box that can fit 2-3 sentences
    without scrolling.
    
    Class restricts modification of all other attributes.
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    _size                 instance-level state for 
    input_type            "text"
    size                  class, dynamic; managed through SizeDescriptor

    FUNCTIONS:
    class SizeDescriptor  accepts "long", None as values; otherwise error
    ====================  ======================================================
    """
    def __init__(self):
        var_attrs = ("main_caption",
                     "shadow",
                     "size",
                     "show_if",
                     "user_can_add")
        GenericInput.__init__(self,var_attrs)
        self.__dict__["_size"] = None
        self.__dict__["input_type"] = "text"

    class SizeDescriptor:
        """

        Descriptor for ``size`` class attribute.
        """
        def __get__(self,instance,owner):
            return instance._size

        def __set__(self,instance,value):
            ok_values = ["long",None]
            if value in ok_values:
                instance.__dict__["_size"] = value
            else:
                raise BBExceptions.ManagedAttributeError
                
    size = SizeDescriptor()
