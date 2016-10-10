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
import chef_settings
from .cell_styles import CellStyles
from .garnish_chef import GarnishChef
from .line_chef import LineChef
from .sheet_style import SheetStyle
from .tab_names import TabNames
from .transcript_chef import TranscriptChef
from .unit_chef import UnitChef
from .summary_chef import SummaryChef




# Constants
IMAGE_PATH = os.path.join(
    os.path.dirname(__file__), 'static', 'blackbird_engine_2X_410x120.png'
)

# Module Globals
line_chef = LineChef()
transcript_chef = TranscriptChef()
unit_chef = UnitChef()

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
        now = model.time_line.current_period
        company = now.content

        unit_chef.chop_multi(book=book, unit=company)

        if bb_settings.MAKE_ANNUAL_SUMMARIES:
            summary_chef = SummaryChef()
            summary_chef.add_annual_summary(book, model)

        unit_chef.chop_multi_valuation(book=book, unit=company, index=2,
                                       recur=False)

        temp_sheet = book.get_sheet_by_name(TabNames.SCENARIOS)
        spacer_idx = book.get_index(temp_sheet) + 1
        spacer_sheet = book.create_sheet("Details >>", spacer_idx)
        spacer_sheet.sheet_properties.tabColor = chef_settings.COVER_TAB_COLOR
        SheetStyle.style_sheet(spacer_sheet)

        transcript_chef.make_transcript_excel(model, book, idx=3)

        CellStyles.format_line_borders(book)

        return book
