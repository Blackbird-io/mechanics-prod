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
add_links_to_selectors function adds VB macros to link cells in sheets
add_scenario_selector function adds a scenario selector cell to the sheet
calculate_formulas    function opens-saves-closes Excel book do calculations
check_alignment       function checks that line is correctly aligned
check_filename_ext    function checks that file has correct extension
close_excel_by_force  function closes Excel application by force
collapse_groups       function opens an Excel file and collapses all groups
group_lines           function adds row to outline group for pretty collapsing
is_close              function for fuzzy equals between numeric values
test_book             function tests values calculated in Excel against those
                      calculated within the Blackbird Engine

CLASSES:
n/a
====================  ==========================================================
"""




# Imports
import os
import openpyxl as xlio
import xlrd

from chef_settings import SCENARIO_SELECTORS

if SCENARIO_SELECTORS:
    import win32api
    import win32com.client as win32
    import win32con
    import win32gui
    import win32process


from openpyxl.worksheet.datavalidation import DataValidation

from .cell_styles import CellStyles
from .field_names import FieldNames




# Constants
_COLLAPSE_GROUPS_VBS_FILE = "excel_collapse_pretty_rows.vbs"
_OPEN_SAVE_CLOSE_VBS_FILE = "open_save_close_excel.vbs"
_VBS_FILENAME_BOOKMARK = "FILENAME_PLACEHOLDER"
_VBS_PATH = os.path.dirname(os.path.realpath(__file__))

# Module Globals
cell_styles = CellStyles()
field_names = FieldNames()

# Classes
# n/a


def add_links_to_selectors(filename, sources_dict):
    """


    add_links_to_selectors() -> None

    --``filename`` is the xlsx file (Chef chopped) to work on
    --``sources_dict`` is a dictionary containing the Excel sheet names and
       selector cell coordinates to link

    Method adds VB code to a completed Chef workbook to link scenario
    selection cells together to allow universal scenario change from any
    sheet in the workbook.
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

    xl.DisplayAlerts = False

    newfile = check_filename_ext(filename, "xlsm")
    ss.SaveAs(newfile, FileFormat=52)

    ss.Close()

    xl.Quit()
    close_excel_by_force(xl)

    # delete original file
    os.remove(filename)

    return newfile


def add_scenario_selector(sheet, column, row, selections):
    """


    add_scenario_selector() -> None

    --``filename`` is the xlsx file (Chef chopped) to work on
    --``sources_dict`` is a dictionary containing the Excel sheet names and
       selector cell coordinates to link

    Method adds VB code to a completed Chef workbook to link scenario
    selection cells together to allow universal scenario change from any
    sheet in the workbook.
    """

    select_column = column + 2

    options = ','.join(selections)
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
    cell_styles.format_hardcoded(selector_cell)
    dv.add(selector_cell)
    sheet.bb.scenario_selector = selector_cell.coordinate

    # Make label cells and drop-down selector
    cell_styles.format_scenario_selector_cells(sheet,
                                               column,
                                               select_column,
                                               row)


def calculate_formulas(filename):
    """


    update_formulas -> None

    --``filename`` must be the string path for the file to check, real path

    This function opens an Excel file, saves, and closes the file.
    """
    _write_run_temp_vbs_file(filename, _OPEN_SAVE_CLOSE_VBS_FILE)


def check_alignment(line):
    """


    check_alignment() -> bool

    --``line`` must be a BB LineItem object

    Function checks that ``line`` is aligned with itself from prior periods.
    Function prints misalignments to screen and returns False when detected.
    """
    cell = line.xl.cell
    sheet = cell.parent

    try:
        check_data = sheet.bb.line_directory[line.id.bbid]
    except KeyError:
        # sheet.bb.line_directory[line.id.bbid] = line.xl
        # check_data = sheet.bb.line_directory[line.id.bbid]
        check_data = None

    result = True
    if check_data:
        if check_data.cell.row != cell.row:
            print(line)
            print(cell)
            print("Correct row: %s" % check_data.cell.row)
            print("Current row: %s" % cell.row)

            c = 'Misalignment!  This line should not be written to ' \
                'the current row.'
            print(c)
            result = False

    return result


def check_filename_ext(filename, ext):
    """


    check_filename_ext() -> str

    --``filename`` proposed filename for workbook
    --``ext`` correct file extension for workbook

    Function ensures filename complies with specified extension and corrects
    if not.  Function returns correct file path.
    """
    temp = filename.strip().split('.')
    check_ext = temp[-1]

    if check_ext == ext:
        result = filename
    else:
        base = filename[0:-len(check_ext)]
        result = base + ext

    return result


def close_excel_by_force(excel):
    """


    close_excel_by_force() -> None

    --``excel`` must be an Excel Application instance

    Method closes all Excel instances by brute force. No other way to close
    out all lingering threads.
    Source: http://stackoverflow.com/questions/10221150/cant-close-excel-completely-using-win32com-on-python
    """

    # Get the window's process id's
    hwnd = excel.Hwnd
    t, p = win32process.GetWindowThreadProcessId(hwnd)

    # Ask window nicely to close
    win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)

    # If the application didn't close, force close
    try:
        handle = win32api.OpenProcess(win32con.PROCESS_TERMINATE, 0, p)
        if handle:
            win32api.TerminateProcess(handle, 0)
            win32api.CloseHandle(handle)
    except:
        pass


def collapse_groups(filename):
    """


    collapse_groups -> None

    --``filename`` must be the string path for the file to check

    This function opens an Excel file, collapses all columns and rows, saves,
    and closes the file.
    """
    _write_run_temp_vbs_file(filename, _COLLAPSE_GROUPS_VBS_FILE)


def group_lines(sheet, row=None):
    """


    group_lines() -> None


    --``sheet`` must be an instance of openpyxl Worksheet

    Group lines in sheet to outline level specified by sheet data
    """
    if not row:
        row = sheet.bb.current_row

    sheet.row_dimensions[row].outline_level = sheet.bb.outline_level


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


def test_book(model, filename, log_filename=None):
    """


    test_book -> bool & writes a log file

    --``model`` must be a Chef-chopped Blackbird engine model
    --``filename`` must be string path at which the workbook for the
        chopped model has been saved.
    --``log_filename`` is the optional path at which to write the test's log

    Function relies on the user having open-saved-closed the Excel spreadsheet,
    manually or programmatically, to make the formulas calculate.

    This is the driver function for checking Excel output.  Function delegates
    to _check_bu to do most of the work.

    Function checks formulas and values written to Excel against values
    calculated and stored in the Blackbird Engine. Function uses fuzzy equals
    (to the 0.001) to compare numeric values.

    Function returns "True" if the test passes (there are no discrepancies
    between the model and excel workbook), "False" otherwise.

    Note:
    A None in the Engine is declared equivalent to an Excel Zero for the
    purpose of this test.
    """

    # start with passed = True, will set False if any inconsistencies are found
    passed = True

    # now open workbook and retrieve relevant cells to compare to dict
    wb = xlrd.open_workbook(filename=filename)

    # open log file
    if not log_filename:
        loc_dot = filename.rfind(".")
        log_fnam = filename[0:loc_dot] + "_log.xlsx"
    else:
        log_fnam = log_filename

    log_wb = xlio.Workbook()
    log_ws = log_wb.active

    # # Lists to hold log values
    qa_list = ["Sheet", "Cell", "BB_Value", "Excel_Value", "Formula_Name"]
    log_ws.append(qa_list)

    # get model and walk through time periods, bu's, statements, lines
    for t in model.time_line.values():
        if t is model.time_line.current_period:
            # only check valuation for the company-level unit in the current
            # period
            check_val = True
        else:
            check_val = False

        if t.content:
            passed = _check_bu(t.content, wb, log_ws, passed,
                               check_val=check_val)

    # now check annual summaries
    annual_summaries = model.time_line.summary_builder.summaries['annual']
    for t in annual_summaries.values():
        if t.content:
            passed = _check_bu(t.content, wb, log_ws, passed, check_val=False)

    log_wb.save(log_fnam)

    return passed

    #*************************************************************************#
    #                          NON-PUBLIC METHODS                             #
    #*************************************************************************#


def _check_bu(business_unit, workbook_in, log_ws, passed, check_val=False):
    """

    _check_bu -> bool & writes to log file

    --``business_unit`` must be an instance of BusinessUnit
    --``workbook_in`` must be the Excel workbook (xlrd.Workbook type) to check
    --``log_ws`` must be the Excel sheet for test log entries (openpyxl.Sheet
        type)
    --``passed`` must ba a bool, whether or not the test has passed thus far
    --``check_val`` whether or not to check Valuation for the business unit

    Function walks through BusinessUnits and Statements and delegates to _check
    _statement to do the bulk of the work.  Function returns "True" if the
    test has passed thus far, "False" otherwise.
    """

    # recursively walk through all business units
    comps = business_unit.components.get_ordered()
    for c in comps:
        # do not check valuation, only check for company-level unit in current
        # period
        passed = _check_bu(c, workbook_in, log_ws, passed, check_val=False)

    # walk through statements
    for statement in business_unit.financials.full_ordered:
        if statement:
            is_val = statement is business_unit.financials.valuation
            if is_val and not check_val:
                continue
            passed = _check_statement(statement, workbook_in, log_ws, passed)

    return passed


def _check_statement(statement, workbook_in, log_ws, passed):
    """

    _check_statement -> bool & writes to log file

    --``business_unit`` must be an instance of BusinessUnit
    --``workbook_in`` must be the Excel workbook (xlrd.Workbook type) to check
    --``log_ws`` must be the Excel sheet for test log entries (openpyxl.Sheet
        type)
    --``passed`` must ba a bool, whether or not the test has passed thus far

    Function recursively checks Excel output for all business units and writes
    inconsistencies to log_ws.  Function uses fuzzy equals (to the 0.001) to
    compare numeric values.

    Function returns "True" if the test has passed thus far, "False" otherwise.

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
            passed = False
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
                formula = line.tags.name

            qa_list = [line.xl.cell.parent.title, line.xl.cell.coordinate,
                       line.value, cell.value, formula]
            log_ws.append(qa_list)
            passed = False

    return passed


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
    i = 0
    while True:
        temp_fnam = vbs_file[:-4]+"_temp_%s.vbs" % i
        temp_path = os.path.join(_VBS_PATH, temp_fnam)
        if os.path.isfile(temp_path):
            i += 1
        else:
            break

    temp_file = open(temp_path, mode='w')

    for line in orig_lines:
        if _VBS_FILENAME_BOOKMARK in line:
            line = line.replace(_VBS_FILENAME_BOOKMARK, filename)

        temp_file.write(line)

    temp_file.close()

    # run the VBS file
    run_path = '"'+temp_path+'"'
    os.system(run_path)

    # delete the temporary VBS file
    os.remove(temp_path)
