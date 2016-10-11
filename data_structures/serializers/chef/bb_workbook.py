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

from chef_settings import COLLAPSE_ROWS, DEFAULT_SCENARIOS, SCENARIO_SELECTORS

from ._chef_tools import check_filename_ext
from .data_management import SheetData
from .field_names import FieldNames

if COLLAPSE_ROWS or SCENARIO_SELECTORS:
    import pythoncom

    from ._chef_tools import add_links_to_selectors, collapse_groups




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
    set_scenario_names()  sets scenario_names attribute
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

        --``filename`` must be string path at which to save workbook (".xlsx")

        Method saves workbook to specified file and uses VBScript to prettily
        collapse row and column groups.
        """

        if COLLAPSE_ROWS or SCENARIO_SELECTORS:
            pythoncom.CoInitialize()

        # save workbook
        filename = check_filename_ext(filename, 'xlsx')
        xlio.Workbook.save(self, filename)

        if COLLAPSE_ROWS:
            collapse_groups(filename)

        if SCENARIO_SELECTORS:
            sources_dict = self._get_sources_dict()
            filename = add_links_to_selectors(filename, sources_dict)

        if COLLAPSE_ROWS or SCENARIO_SELECTORS:
            pythoncom.CoUninitialize()

        return filename

    def set_scenario_names(self, model):
        """


        BB_Workbook.set_scenario_names() -> None

        --``model`` must be a Blackbird Engine model

        Sets instance.scenario_names list.
        """
        self.scenario_names = [FieldNames.CUSTOM, FieldNames.BASE]
        self.scenario_names.extend(DEFAULT_SCENARIOS)

        for k in sorted(model.scenarios.keys()):
            if k not in self.scenario_names:
                self.scenario_names.append(k.title())

    # *************************************************************************#
    #                           NON-PUBLIC METHODS                             #
    # *************************************************************************#

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
                    idx = int(self.get_index(sheet)) + 1
                    sheet_num = "Sheet%s" % idx
                    sources_dict[sheet_num] = (sheet.title,
                                               sheet.bb.scenario_selector)

        return sources_dict
