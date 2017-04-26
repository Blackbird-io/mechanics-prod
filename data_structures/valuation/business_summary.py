# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL
# Blackbird Environment
# Module: data_structures.valuation.business_summary

"""

Module defines BusinessSummary class. The BusinessSummary provides a storage
container that describes the business as a whole at a particular point and time.
The class also includes an output method (to_portal()) that provides a portable
version of the information in a JSON-compatible, primitive form.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
BusinessSummary       dictionary with pre-populated fields
====================  ==========================================================
"""




#imports
from ..guidance.outline import Outline
from ..guidance.step import Step
from ..modelling.book_mark import BookMark




#globals
mandatory_summary_fields = ["credit_capacity"]

#classes
class BusinessSummary(Outline):
    """

    Container for business summary information. 
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    data                  dictionary
    
    FUNCTIONS:
    __str__               mildly pretty print
    set_path()            put together a standard summary path
    to_portal()           return a primitive dict of instance data
    ====================  ======================================================
    """
    def __init__(self):
        Outline.__init__(self, "business summary")
        self.data = dict.fromkeys(mandatory_summary_fields)
        self.set_path()

    def to_portal(self):
        result = dict()
        result['outline'] = Outline.to_portal(self)
        result['data'] = self.data

        return result

    @classmethod
    def from_portal(cls, data):
        outline = Outline.from_portal(data['outline'], list())

        result = cls()
        result.__dict__.update(outline.__dict__)
        result.data = data['data']

        return result

    def set_path(self):
        """


        BusinessSummary.set_path() -> None


        Method creates a standard summary roadmap.
        """
        Outline.set_path(self)
        steps = [BookMark("start Summary", "Summary"),
                 Step("annual financials"),
                 Step("credit capacity"),
                 BookMark("end Summary", "Summary", "endStatement")]
        self.path.extend(steps)
