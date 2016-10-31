# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL

# Blackbird Environment
# Module: serializers.chef.model_chef
"""

Class for creating dynamic Excel representations of Blackbird Engine models.

Chef modules write formulas to cells explicitly, using the set_explicit_value()
method, to make sure Excel interprets the strings correctly.
====================  =========================================================
Attribute             Description
====================  =========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
ModelChef             chop Blackbird Engine model into a dynamic Excel workbook
====================  =========================================================
"""




# Imports
import os
import openpyxl as xlio

import bb_settings
from .cell_styles import CellStyles
from .garnish_chef import GarnishChef
from .line_chef import LineChef
from .report_chef import ReportChef
from .sheet_style import SheetStyle
from .summary_chef import SummaryChef
from .transcript_chef import TranscriptChef
from .unit_chef import UnitChef
from .unit_structure import StructureChef




# Constants
IMAGE_PATH = os.path.join(
    os.path.dirname(__file__), 'static', 'blackbird_engine_2X_410x120.png'
)

# Module Globals
line_chef = LineChef()
transcript_chef = TranscriptChef()

get_column_letter = xlio.utils.get_column_letter
bounding_box = xlio.drawing.image.bounding_box

# Classes
class ModelChef:
    """

    Class packages an Engine model into an Excel workbook with dynamic links.
    ====================  =====================================================
    Attribute             Description
    ====================  =====================================================

    DATA:
    n/a

    FUNCTIONS:
    chop_model()          returns BB_Workbook containing an Excel workbook with
                          dynamic links
    ====================  =====================================================
    """

    def chop_model(self, model):
        """


        ModelChef.chop_model -> BB_Workbook

        --``model`` is an instance of Blackbird Engine model

        Method delegates to UnitChef to chop BusinessUnits and returns an
        instance of BB_Workbook.  BB_Workbook contains an Excel workbook with
        dynamic links.
        """

        book = GarnishChef.add_garnishes(model)

        # add a tab with unit structure map
        structure_chef = StructureChef(model)
        structure_chef.chop(book)

        unit_chef = UnitChef(model)
        unit_chef.chop_multi(book)

        if bb_settings.MAKE_ANNUAL_SUMMARIES:
            summary_chef = SummaryChef(model)
            summary_chef.add_annual_summary(book)

        unit_chef.chop_multi_valuation(model, book, index=2, recur=False)

        transcript_chef.make_transcript_excel(model, book, idx=3)

        CellStyles.format_line_borders(book)

        return book

    def build_report(self, model, dates=None):
        # gGet timelines to report from
        proj = model.get_timeline()
        actl = model.get_timeline(resolution='monthly', type='actual')

        # Make workbook and add Cover tab
        book = GarnishChef.add_garnishes(model, report=True)

        # Add "Forecast" tab filled with projections and "Actual" tab filled
        # with reported values.
        unit_chef = UnitChef(model)
        unit_chef.chop_multi(timeline=proj)
        unit_chef.chop_multi(timeline=actl, actuals=True)
        """
        UnitChef notes:
         - Using chop_multi() to start with. -> need to add timeline and actuals keywords
         - Later, if we want to only chop the company, can add a chop_single()
           routine (or just hide the extra tabs, if any)
         - chop_multi(actuals=True) means no drivers, life, etc at the top of
         the sheet since all values are hardcoded
        """

        # Build reports
        report_chef = ReportChef(model, dates)
        report_chef.build_reports(book, proj, actl)

        # Add "Reports >>" tab with table of contents.  Need to do this last
        # since we can't count on dates corresponding exactly with period start
        # and end dates.
        structure_chef = StructureChef(model)
        structure_chef.chop_report(book, dates)

        for sheet in book.worksheets:
            SheetStyle.style_sheet(sheet)