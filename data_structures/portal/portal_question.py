# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL
# Blackbird Environment
# Module: data_structures.portal.portal_question
"""

Module defines class that follows the Engine-Wrapper API PortalQuestion schema
and converts rich objects into schema-compliant dictionaries.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
PortalQuestion        object that follows Engine-Wrapper API schema
====================  ==========================================================
"""




#imports
import copy

from .ready_for_portal import ReadyForPortal




#globals
#n/a

#classes
class PortalQuestion(ReadyForPortal):
    """

    Class defines an object that translates a question the Engine wishes to ask
    the user into the Engine API's PortalQuestion schema.

    Use to_database() to generate clean dictionaries suitable for external
    delivery.

    PortalQuestion objects do not rely on any QuestionManager functionality. 
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    array_caption         string that appears above arrays of input_elements
    comment               explanation string that appears below the prompt
    input_array           list of InputElement objects
    input_type            string, controls widgets displayed in browser
    input_sub_type        string, provides additional context for Portal
    prompt                main question
    progress              float; completion indicator for interview, 0< p <=1
    short                 string; 2-3 question summary for tracker panel
    show_if               binary gating element or None;
    topic_name            string; appears in user-facing browser outline
    transcribe            bool; whether portal should show question to lenders

    FUNCTIONS:
    to_database()           returns attr : attr_val dictionary
    ====================  ======================================================
    """
    def __init__(self):
        pq_attrs = ["array_caption",
                    "comment",
                    "input_array",
                    "input_type",
                    "input_sub_type",
                    "prompt",
                    "progress",
                    "short",
                    "show_if",
                    "topic_name",
                    "transcribe",
                    "name",
                    "target",
                    "extra_rows",
                    "delayed",
                    ]
        #
        ReadyForPortal.__init__(self, pq_attrs)
        #
        self.array_caption = None
        self.comment = None
        self.input_array = []
        self.input_type = "text"
        self.input_sub_type = None
        self.name = None
        self.prompt = None
        self.progress = 0
        self.short = None
        self.show_if = None
        self.topic_name = None
        self.transcribe = False
        self.target = None
        self.extra_rows = True
        self.delayed = False

    def to_database(self, seed, web=False):
        """


        PortalQuestion.to_database() -> dict()

        
        Method returns a dictionary object, keyed by attribute name for a
        standard, fresh instance of cls and carrying values from matching
        seed attributes.

        For attribtues like input_array, method condenses seed values into
        objects composed of built-in types only (as opposed to user-defined
        classes). 

        Method delegates work to ReadyForPortal.to_database, then modifies the
        output by stripping out inactive elements from input array.

        If ``web`` is True, method condenses active elements into dictionary
        representations that track Engine-Wrapper InputElement spec. Method also
        replaces progress with an integer.

        Finally, method adds optional supplementary keys to result.
        
          -- ``name`` : allows SimplePortal to match question to script answer
          -- [intentionally blank]
          
        These keys support command-line testing functionality. The Web Portal
        ignores them altogether. Method pulls data for values directly from
        **seed** (as opposed to prelim). 
        """
        prelim = ReadyForPortal.to_database(self, seed)
        # Prelim is a dictionary with keys that track attributes
        
        result = prelim.copy()

        # Drop inactive elements, flatten to JSON if necessary
        result["input_array"] = []
        for input_element in prelim["input_array"]:
            if input_element._active:
                clean_element = input_element
                #weed out inactive elements
                if web:
                    clean_element = input_element.to_database()
                    #flatten input_element to a dictionary for web output
                #
                result["input_array"].append(clean_element)

        # Manually adjust a couple attribute values
        result["progress"] = int(prelim["progress"])
        if web:
            if prelim["show_if"] is not None:
                result["show_if"] = prelim["show_if"].to_database()
                # Flatten binary gating element to JSON spec
            
        # additional portal-oriented data
        result["name"] = copy.copy(seed.tags.name)
        result["question_id"] = str(seed.id.bbid)
        result["target"] = seed.context.get("target", None)
        result["extra_rows"] = seed.extra_rows
        result["delayed"] = seed.delayed

        del result["_var_attrs"]
        
        return result
        

    
    
