# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL

# Blackbird Environment
# Module: data_structures.serializers.chef._chef_tools
"""

Module defines functions that are tools for Chef module.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
collapse_groups       function opens an Excel file and collapses all groups
is_close              function for fuzzy equals between numeric values
test_book             function tests values calculated in Excel against those
                      calculated within the Blackbird Engine

CLASSES:
n/a
====================  ==========================================================
"""




# Imports
import openpyxl as xlio
import os
import xlrd
import win32com.client as win32
import win32process
import win32gui
import win32api
import win32con
import time

import Shell

from openpyxl.worksheet.datavalidation import DataValidation
from .cell_styles import CellStyles




# Constants
_ORIG_VBS_FILE = "open_save_close_excel_model.vbs"
_COLLAPSE_GROUPS_VBS_FILE = "excel_collapse_pretty_rows.vbs"
_VBS_FILENAME_BOOKMARK = "FILENAME_PLACEHOLDER"
_VBS_PATH = os.path.dirname(os.path.realpath(__file__))

SELECTION_OPTIONS = list()
cell_styles = CellStyles()

# Module Globals
# n/a

# Classes
# n/a




def add_links_to_selectors(filename, sources_dict):

    """
    take a dict of sheet_name:cell_coord (sources_dict)

    whole_set = set(sources_dict.keys())

    for sheet in whole_set:
        write macro to sheet
        link cell to cells in all other_sheets
        other_sheets = whole_set - set(sheet)

        get cell address in other_sheets using sources_dict
    """

    xl = win32.gencache.EnsureDispatch('Excel.Application')
    xl.Visible = False

    ss = xl.Workbooks.Open(filename)

    all_sheets = set(sources_dict.keys())
    for sheet in all_sheets:
        macro_code = []
        cos = sources_dict[sheet][1]
        col = cos[0]
        row = cos[1]
        line = '    If Target.Address = "$%s$%s" Then' % (col, row)
        macro_code.append(line)

        line = '        Application.EnableEvents = False'
        macro_code.append(line)

        other_sheets = all_sheets - set(sheet)
        for o in other_sheets:
            name = sources_dict[o][0]
            cos = sources_dict[o][1]
            col = cos[0]
            row = cos[1]
            line = '        ThisWorkbook.Sheets("%s").Range("$%s$%s").Value = Target.Value' % (name, col, row)
            macro_code.append(line)

        line = '        Application.EnableEvents = True'
        macro_code.append(line)

        line = '    End If'
        macro_code.append(line)

        comp = ss.VBProject.VBComponents(sheet)
        module = comp.CodeModule
        line_num = module.CreateEventProc("Change", "Worksheet")

        for i, line in enumerate(macro_code):
            module.InsertLines(line_num+i+1, line)

    newfile = filename[0:-4] + "xlsm"
    ss.SaveAs(newfile, FileFormat=52)

    ss.Close()
    del ss

    xl.Quit()
    close_excel_by_force(xl)
    del xl

    # delete original file
    os.remove(filename)


def close_excel_by_force(excel):
    # Get the window's process id's
    hwnd = excel.Hwnd
    t, p = win32process.GetWindowThreadProcessId(hwnd)
    # Ask window nicely to close
    win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
    # Allow some time for app to close
    time.sleep(10)
    # If the application didn't close, force close
    try:
        handle = win32api.OpenProcess(win32con.PROCESS_TERMINATE, 0, p)
        if handle:
            win32api.TerminateProcess(handle, 0)
            win32api.CloseHandle(handle)
    except:
        pass


def add_scenario_selector(sheet, column, row, model=None):
    select_column = column + 2

    if model:
        SELECTION_OPTIONS.append("Custom")
        for o in model.scenarios.get_keys():
            SELECTION_OPTIONS.append(o.title())

    options = ','.join(SELECTION_OPTIONS)
    dv = DataValidation(type="list",
                        formula1='"%s"' % options,
                        allow_blank=False)

    # Optionally set a custom error message
    dv.error ='Your entry is not in the list'
    dv.errorTitle = 'Invalid Entry'

    # Optionally set a custom prompt message
    dv.prompt = 'Please select from the list'
    dv.promptTitle = 'List Selection'

    sheet.add_data_validation(dv)

    selector_cell = sheet.cell(column=select_column, row=row)
    selector_cell.value = "Base"
    dv.add(selector_cell)
    sheet.bb.scenario_selector = selector_cell.coordinate

    # Make label cells and drop-down selector
    cell_styles.format_scenario_selector_cells(sheet,
                                               column,
                                               select_column,
                                               row)

def collapse_groups(filename):
    """


    collapse_groups -> None

    --``filename`` must be the string path for the file to check

    This function opens an Excel file, collapses all columns and rows, saves,
    and closes the file.
    """
    _write_run_temp_vbs_file(filename, _COLLAPSE_GROUPS_VBS_FILE)


def is_close(a, b, rel_tol=1e-09, abs_tol=0.0):
    """


    is_close -> bool

    --``a``, ``b`` are numeric values to compare
    --``rel_tol`` is the relative allowable tolerance, taken as fraction of the
        larger of a and b
    --``abs_tol`` is the absolute allowable tolerance

    This method provides a means for comparing two numbers by "fuzzy equals".
    If the absolute difference between ``a`` and ``b`` is less than or equal to
    the maximum of the specified relative tolerance and absolute tolerance,
    method returns True.  This method was copied from documentation for
    math.isclose() method in Python 3.5.

    """
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


def test_book(model, filename):
    """


    test_book -> None (writes a log file)

    --``model`` must be a Chef-chopped Blackbird engine model
    --``filename`` must be string path at which the workbook for the
        chopped model has been saved.

    This is the driver function for checking Excel output.  Function delegates
    to _write_run_temp_vbs_file and _check_bu to do most of the work.

    Function checks formulas and values written to Excel against values
    calculated and stored in the Blackbird Engine. Function uses fuzzy equals
    (to the 0.001) to compare numeric values.

    Note:
    A None in the Engine is declared equivalent to an Excel Zero for the
    purpose of this test.
    """
    # _write_run_temp_vbs_file(filename, _ORIG_VBS_FILE)

    # now open workbook and retrieve relevant cells to compare to dict
    wb = xlrd.open_workbook(filename=filename)

    # open log file
    loc_dot = filename.rfind(".")
    log_fnam = filename[0:loc_dot] + "_log.xlsx"

    log_wb = xlio.Workbook()
    log_ws = log_wb.active

    # # Lists to hold log values
    qa_list = ["Sheet", "Cell", "BB_Value", "Excel_Value", "Formula_Name"]
    log_ws.append(qa_list)

    # get model and walk through time periods, bu's, statements, lines
    for t in model.time_line.values():
        if t.content:
            _check_bu(t.content, wb, log_ws)

    log_wb.save(log_fnam)

    #*************************************************************************#
    #                          NON-PUBLIC METHODS                             #
    #*************************************************************************#


def _check_bu(business_unit, workbook_in, log_ws):
    """

    _check_bu -> None (writes to log file)

    --``business_unit`` must be an instance of BusinessUnit
    --``workbook_in`` must be the Excel workbook (xlrd.Workbook type) to check
    --``log_ws`` must be the Excel sheet for test log entries (openpyxl.Sheet
        type)

    Function walks through BusinessUnits and Statements and delegates to _check
    _statement to do the bulk of the work.
    """

    # recursively walk through all business units
    comps = business_unit.components.get_ordered()
    for c in comps:
        _check_bu(c, workbook_in, log_ws)

    # walk through statements
    for statement in business_unit.financials.ordered:
        if statement:
            _check_statement(statement, workbook_in, log_ws)


def _check_statement(statement, workbook_in, log_ws):
    """

    _check_statement -> None (writes to log file)

    --``business_unit`` must be an instance of BusinessUnit
    --``workbook_in`` must be the Excel workbook (xlrd.Workbook type) to check
    --``log_ws`` must be the Excel sheet for test log entries (openpyxl.Sheet
        type)

    Function recursively checks Excel output for all business units and writes
    inconsistencies to log_ws.  Function uses fuzzy equals (to the 0.001) to
    compare numeric values.

    Note:
    A None in the Engine is declared equivalent to an Excel Zero and Excel
    empty string for the purpose of this test.
    """

    lines = statement.get_full_ordered()

    # walk through lineitems
    for line in lines:
        # get cell value
        sheet = workbook_in.sheet_by_name(line.xl.cell.parent.title)

        try:
            col = line.xl.cell.col_idx - 1
            row = line.xl.cell.row - 1
            cell = sheet.cell(row, col)
        except IndexError:
            m1 = "Row %s, Col %s" % (row, col)
            m2 = "NROWS %s, NCOLS %s" % (sheet.nrows, sheet.ncols)
            m = m1 + "\n" + m2
            raise IndexError(m)

        same = False
        if line.value is None or cell.value is None:
            if line.value is None and cell.value is "":
                same = True
            elif line.value is None and cell.value == 0:
                # None LineItems are written as zeros
                same = True
            else:
                same = False
        elif isinstance(cell.value, float) or isinstance(cell.value, int):
            if is_close(cell.value, line.value, abs_tol=0.001):
                same = True
            else:
                same = False
        elif isinstance(cell.value, str):
            if cell.value is line.value:
                same = True
            else:
                same = False
        else:
            print("ERROR: unrecognized type")

        if same is True:
            pass
        else:
            if line.xl.derived.calculations:
                calcs = line.xl.derived.calculations
                formula_names = [c.name for c in calcs]
                formula = ','.join(formula_names)
            else:
                formula = line.name

            qa_list = [line.xl.cell.parent.title, line.xl.cell.coordinate,
                       line.value, cell.value, formula]
            log_ws.append(qa_list)


def _write_run_temp_vbs_file(filename, vbs_file):
    """


    _write_run_temp_vbs_file -> None

    --``filename`` must be the string path for the file being checked

    Function updates template VBScript with file being checked, opens file,
    saves file, and closes file so that Excel will calculate formula values.
    """

    # open and read original VBS file
    orig_path = os.path.join(_VBS_PATH, vbs_file)
    orig_file = open(orig_path, mode='r')
    orig_lines = orig_file.readlines()
    orig_file.close()

    # write temporary VBS file with correct filepath
    temp_fnam = vbs_file[:-4]+"_temp.vbs"
    temp_path = os.path.join(_VBS_PATH, temp_fnam)
    temp_file = open(temp_path, mode='w')

    for line in orig_lines:
        if _VBS_FILENAME_BOOKMARK in line:
            line = line.replace(_VBS_FILENAME_BOOKMARK, filename)

        temp_file.write(line)

    temp_file.close()

    # run the VBS file
    os.system(temp_path)

    # delete the temporary VBS file
    os.remove(temp_path)
