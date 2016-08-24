# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL

# Blackbird Environment
# Module: serializers.chef.transcript_chef
"""

Class for creating the transcript tab in Blackbird workbooks.
====================  =========================================================
Attribute             Description
====================  =========================================================

DATA:
N/A

FUNCTIONS:
n/a

CLASSES:
TranscriptChef         add transcript tab to Blackbird model Excel workbook
====================  =========================================================
"""




# Imports
import chef_settings
import datetime
import os
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.styles.colors import WHITE, BLACK
import string

from .cell_styles import CellStyles
from .sheet_style import SheetStyle
from .tab_names import TabNames




# Constants
NOTE_CAP = 'Note'

# Module Globals
cell_styles = CellStyles()
sheet_style = SheetStyle()
tab_names = TabNames()


# Classes
class TranscriptChef:
    """

    Class packages an Engine model into an Excel workbook with dynamic links.
    ====================  =====================================================
    Attribute             Description
    ====================  =====================================================

    DATA:
    n/a

    FUNCTIONS:
    make_transcript_tab() adds transcript tab to Blackbird model workbook
    ====================  =====================================================
    """

    def make_transcript_excel(self, model, book, idx=1):
        """


       TranscriptChef.make_transcript_tab() -> None

        --``model`` Blackbird model object
        --``book`` working Excel book where tab should be added
        --``idx`` is the index where tab should be added

        Function generates and excel transcript of the questiosn/responses from the
        analysis' interview.
        """

        # get length of interview
        transcript = list()
        for i in model.transcript:
            q = i[0]['q_in']
            if q:
                q['response_array'] = i[0]['r_in']
                transcript.append(q)

        analysis_name = model.name.title()

        column_dict = dict()
        column_dict['Question'] = 'C'
        column_dict['Element Caption'] = 'D'
        column_dict['Target Unit'] = 'E'
        column_dict['Response'] = 'F'
        column_dict['Question Identifier'] = 'G'

        sheet = self._prep_output_excel(book, analysis_name, column_dict, idx)

        mc = "main_caption"
        rs = "response"
        it = 'input_type'

        current_row = 8
        for q in transcript:
            try:
                target = q['target']
            except KeyError:
                target = None
                prompt = q['prompt']
                name = None
            else:
                name = q['name']
                prompt = q['prompt']

            response_array = q['response_array']

            if q['input_type'] == 'end':
                continue

            if not response_array:
                continue

            for i in range(len(response_array)):
                answer = column_dict.copy()

                main_cap = response_array[i][mc]
                response = response_array[i][rs][0]
                input_type = response_array[i][it]

                if response is None and input_type == 'bool':
                    response = False

                if isinstance(response, datetime.date):
                    response = response.strftime('%Y-%m-%d')

                if isinstance(response, list):
                    response = 'Min: %s; Max: %s' % tuple(response)

                answer['Question'] = prompt or ''
                answer['Element Caption'] = main_cap or ''
                answer['Target Unit'] = target or ''
                answer['Response'] = response or ''
                answer['Question Identifier'] = name or ''

                self._add_record_to_excel(sheet, column_dict, answer, current_row)
                current_row += 1

            try:
                notes = q['notes']
            except KeyError:
                pass
            else:
                for note in notes:
                    answer['Question'] = prompt or ''
                    answer['Element Caption'] = NOTE_CAP
                    answer['Target Unit'] = target or ''
                    answer['Response'] = note or ''
                    answer['Question Identifier'] = name or ''
                    self._add_record_to_excel(sheet, column_dict, answer, current_row)
                    current_row += 1

        for col in column_dict.values():
            num_col = string.ascii_uppercase.find(col.upper()) + 1
            cell_styles.format_border_group(sheet=sheet,
                                            st_col=num_col,
                                            ed_col=num_col,
                                            st_row=8,
                                            ed_row=current_row - 1,
                                            border_style='dashed')

        self._add_note_to_excel(sheet, current_row + 1)

        sheet_style.style_sheet(sheet, label_areas=False)
        sheet.sheet_properties.tabColor = chef_settings.TRANSCRIPT_TAB_COLOR

    @staticmethod
    def _add_note_to_excel(sheet, row):
        # set label cell
        cell = sheet['A' + str(row)]
        cell.value = 'Note:'
        cell.font = Font(bold=True)

        # set note
        cell = sheet['C' + str(row)]
        cell.value = 'To ensure compatibility with website script functionality, adjust only values in "Response" ' \
                     'column. Within "Response" column, maintain given formatting for ranges, dates, etc.'

    @staticmethod
    def _add_record_to_excel(sheet, master_dict, answer_dict, row):
        for key, column in master_dict.items():
            cell = sheet[column + str(row)]
            cell.value = answer_dict[key]
            cell.alignment = Alignment(horizontal='left')

    @staticmethod
    def _prep_output_excel(wb, name, column_dict, index):
        title_txt = 'INTERVIEW TRANSCRIPT'

        column_widths = dict()
        column_widths['A'] = 9  # Labels
        column_widths['B'] = 4
        column_widths['C'] = 74  # Question prompt column
        column_widths['D'] = 44  # Target BU name
        column_widths['E'] = 44  # Main Caption/Element Caption column
        column_widths['F'] = 44  # Response column
        column_widths['G'] = 40  # Question name/identifier, HIDE THIS COLUMN

        date = datetime.date.today()
        date_str = '%s-%s-%s' % (date.month, date.day, date.year)
        title = name + ' ' + date_str

        sheet = wb.create_sheet(name=tab_names.TRANSCRIPT, index=index)

        for col, wid in column_widths.items():
            sheet.column_dimensions[col].width = wid

        # set sheet title cell
        cell = sheet['D2']
        cell.value = title_txt
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal='center')

        # set company name cell and label
        cell = sheet['A4']
        cell.value = 'Company:'
        cell.font = Font(bold=True)

        cell = sheet['C4']
        cell.value = name

        # set date cell and label
        cell = sheet['A5']
        cell.value = 'Date:'
        cell.font = Font(bold=True)

        cell = sheet['C5']
        cell.value = date_str

        for title, col in column_dict.items():
            cos = col + '7'
            cell = sheet[cos]
            cell.value = title
            cell.font = Font(color=WHITE, bold=True)
            cell.fill = PatternFill(start_color=BLACK,
                                    end_color=BLACK,
                                    fill_type='solid')
            cell.alignment = Alignment(horizontal='left')

        sheet.freeze_panes = 'C8'

        sheet.column_dimensions['G'].hidden = True

        return sheet
