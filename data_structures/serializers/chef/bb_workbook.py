# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL

# Blackbird Environment
# Module: data_structures.serializers.chef.bb_workbook
"""

Module defines workbook with custom native-Python data storage on each sheet.
====================  =========================================================
Attribute             Description
====================  =========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
BB_Workbook           workbook where each sheet has a SheetData record set
====================  =========================================================
"""




# Imports
import openpyxl as xlio

from ._chef_tools import add_links_to_selectors, collapse_groups, test_book
from .data_management import SheetData




# Constants
# n/a

# Module Globals
# n/a

# Classes
class BB_Workbook(xlio.Workbook):
    """

    Class modifies standard workbook to include a SheetData record set on each
    sheet. As a result, we can do data lookups and reference builds faster and
    more explicitly.     
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    scenario_names        None or list; holds names of scenarios in workbook

    FUNCTIONS:
    create_sheet()        returns sheet with a SheetData instance at sheet.bb
    save()                saves workbook to file and runs test on contents
    test()                test workbook against model
    ====================  ======================================================
    """ 
    def __init__(self, *pargs, **kwargs):
        xlio.Workbook.__init__(self, *pargs, **kwargs)
        self.scenario_names = None

    def create_sheet(self, name, index=None):
        """


        BB_WorkBook.create_sheet(name) -> Worksheet

        --``name`` must be string name for new worksheet
        --``index`` is the desired index at which to place the new worksheet
            within the workbook

        Return worksheet with a SheetData record set at instance.bb.

        """
        sheet = xlio.Workbook.create_sheet(self, name, index=index)
        sheet.bb = SheetData()

        return sheet

    def save(self, filename):
        """


        BB_WorkBook.save(filename) -> None

        --``filename`` must be string path at which to save workbook

        Method saves workbook to specified file and uses VBScript to prettily
        collapse row and column groups.
        """
        # save workbook
        xlio.Workbook.save(self, filename)

        collapse_groups(filename)

        sources_dict = self._get_sources_dict()
        add_links_to_selectors(filename, sources_dict)

    @staticmethod
    def test(model, filename):
        """


        BB_WorkBook.test(filename) -> None

        --``model`` must be a Chef-chopped Blackbird engine model
        --``filename`` must be string path at which the workbook for the
            chopped model has been saved.

        Method initiates test of file contents against the model in memory.
        """
        # test the workbook against engine values
        test_book(model, filename)

    #*************************************************************************#
    #                          NON-PUBLIC METHODS                             #
    #*************************************************************************#

    def _get_sources_dict(self):
        """


        BB_Workbook._get_sources_dict(self) -> dict

        Method compiles dictionary of worksheet names and cell addresses where
        scenario selector cells live.
        """
        sources_dict = dict()
        for sheet in self.worksheets:
            if getattr(sheet, 'bb', None):
                if sheet.bb.scenario_selector:
                    idx = int(self.get_index(sheet))+1
                    sheet_num = "Sheet%s" % idx
                    sources_dict[sheet_num] = (sheet.title,
                                               sheet.bb.scenario_selector)

        return sources_dict
