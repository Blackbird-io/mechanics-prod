# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL
# Blackbird Environment
# Module: Analysis.PortalModel
"""

Module defines class that follows the Engine-Wrapper API PortalModel schema
and converts rich objects into schema-compliant dictionaries.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
PortalModel        object that follows Engine-Wrapper API schema
====================  ==========================================================
"""




# imports
import pickle

from .ready_for_portal import ReadyForPortal




# globals
# n/a

# classes
class PortalModel(ReadyForPortal):
    """

    Class defines an object that translates a question the Engine wishes to ask
    the user into the Engine API's PortalQuestion schema.

    Use to_portal() to generate clean dictionaries suitable for external
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
    topic_name            string; appears in user-facing browser outline
    transcribe            bool; whether portal should show question to lenders

    FUNCTIONS:
    to_portal()           returns attr : attr_val dictionary
    ====================  ======================================================
    """
    def __init__(self):
        pm_attrs = ["e_model",
                    "industry",
                    "summary",
                    "business_name",
                    "business_id",
                    "user_context",
                    "tags",
                    "update_count",
                    "monitoring",
                    "timelines",
                    ]
        #
        ReadyForPortal.__init__(self, pm_attrs)
        #
        self.e_model = None
        self.industry = None
        self.summary = None
        self.business_name = None
        self.business_id = 99999999
        self.user_context = None
        self.tags = None
        self.update_count = 0
        self.monitoring = False

    def to_portal(self, seed=None):
        """


        PortalModel.to_portal(seed) -> dict()


        Method returns a dictionary object, keyed by attribute name for a
        standard, fresh instance of cls and carrying values from matching
        seed attributes.

        Method delegates work to ReadyForPortal.to_portal, then modifies the
        output by manually extracting the industry.
        """
        prelim = ReadyForPortal.to_portal(self)
        # prelim is a dictionary;
        result = prelim.copy()
        if seed:
            if seed.portal_data:
                result.update(seed.portal_data)
            #
            seed.portal_data.clear()
            result["industry"] = seed.interview.work_space.get("industry")
            # dict keys serialized by Model itself
            result.update(seed.to_portal())

            if seed.summary:
                summary = seed.summary.to_portal()
            else:
                summary = {"credit capacity": "dummy placeholder"}
            result["summary"] = summary

            del seed.timelines
            for bu in seed.bu_directory.values():
                del bu.financials

            if seed.summary_maker:
                sum_dict = {'_fiscal_year_end': seed.summary_maker._fiscal_year_end,
                            'timeline_name': seed.summary_maker.timeline_name,
                            }
                seed.summary_maker = sum_dict

            flattened = pickle.dumps(seed)
            result["e_model"] = flattened

        del result["_var_attrs"]

        return result
