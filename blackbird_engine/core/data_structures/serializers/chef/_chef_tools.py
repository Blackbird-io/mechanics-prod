#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2016
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL

#Blackbird Environment
#Module: data_structures.serializers.chef._chef_tools
"""

Module defines workbook with custom native-Python data storage on each sheet.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
test_book             function tests values calculated in Excel to those
                      calculated within the Blackbird Engine
write_run_temp_vbs_file  function updates template VBScript to open, save, and
                         close Excel file to calculate formulas
isclose               function for fuzzy equals between numeric values

CLASSES:
n/a
====================  ==========================================================
"""




# Imports
import openpyxl as xlio
import os
import subprocess
import xlrd

from .line_chef import CHEF_TESTING_DICT




# Constants
_VBS_PATH = r"C:\Blackbird\Engine\mechanics\chef_updates\blackbird_engine" + \
           r"\core\data_structures\serializers\chef"
_ORIG_VBS_FILE = r"\open_save_close_excel_model.vbs"
_TEMP_VBS_FILE = r"\open_save_close_excel_model_TEMP.vbs"
_VBS_FILENAME_BOOKMARK = "FILENAME_PLACEHOLDER"

# Module Globals
# n/a

# Classes
# n/a


def test_book(filename):
    """

    test_book -> None (writes a log file)

    --``filename`` must be the string path for the file to check

    Function checks formulas written to Excel against values calculated in the
    Blackbird Engine. Function uses fuzzy equals (to the 0.001) to compare
    numeric values.

    Note:
    A None in the Engine is declared equivalent to an Excel Zero for the
    purpose of this test.
    """
    write_run_temp_vbs_file(filename)

    # now open workbook and retrieve relevant cells to compare to dict
    wb = xlrd.open_workbook(filename=filename)

    cells = CHEF_TESTING_DICT.keys()

    # open log file
    loc_dot = filename.rfind(".")
    log_fnam = filename[0:loc_dot] + "_log.xlsx"

    log_wb = xlio.Workbook()
    log_ws = log_wb.active

    # # Lists to hold log values
    qa_list = ["Sheet", "Cell", "BB_Value", "Excel_Value", "Formula_Name"]
    log_ws.append(qa_list)

    for c in cells:
        # get cell value
        sheet = wb.sheet_by_name(c.parent.title)

        try:
            col = c.col_idx - 1
            cell = sheet.cell(c.row, col)
        except IndexError:
            m1 = "Row %s, Col %s" % (c.row, col)
            m2 = "NROWS %s, NCOLS %s" % (sheet.nrows, sheet.ncols)
            m = m1 + "\n" + m2
            raise IndexError(m)
        cell_value = cell.value

        same = False
        if CHEF_TESTING_DICT[c] is None or cell_value is None:
            if CHEF_TESTING_DICT[c] is None and cell_value is None:
                same = True
            elif CHEF_TESTING_DICT[c] is None and cell_value == 0:
                # None LineItems are written as zeros
                same = True
            else:
                same = False
        elif isinstance(cell_value, float) or isinstance(cell_value, int):
            if isclose(cell_value, CHEF_TESTING_DICT[c], abs_tol=0.001):
                same = True
            else:
                same = False
        elif isinstance(cell_value, str):
            if cell_value is CHEF_TESTING_DICT[c]:
                same = True
            else:
                same = False
        else:
            print("ERROR: unrecognized type")

        if same is True:
            pass
        else:
            temp = c.comment.text.split("\n")
            temp = temp[0].split(":")
            formula = temp[1].strip()

            qa_list = [c.parent.title, c.coordinate, CHEF_TESTING_DICT[c],
                       cell_value, formula]
            log_ws.append(qa_list)

    log_wb.save(log_fnam)


def write_run_temp_vbs_file(filename):
    """

    write_run_temp_vbs_file -> None

    --``filename`` must be the string path for the file being checked

    Function updates template VBScript with file being checked, opens file,
    saves file, and closes file so that Excel will calculate formula values.
    """

    # open and read original VBS file
    orig_path = _VBS_PATH + _ORIG_VBS_FILE
    orig_file = open(orig_path, mode='r')
    orig_lines = orig_file.readlines()
    orig_file.close()

    # write temporary VBS file with correct filepath
    temp_path = _VBS_PATH + _TEMP_VBS_FILE
    temp_file = open(temp_path, mode='w')

    for line in orig_lines:
        if _VBS_FILENAME_BOOKMARK in line:
            line = line.replace(_VBS_FILENAME_BOOKMARK, filename)

        temp_file.write(line)

    temp_file.close()

    # run the VBS file
    p = subprocess.Popen(temp_path, shell=True)
    stdout, stderr = p.communicate()

    # delete the temporary VBS file
    os.remove(temp_path)


def isclose(a, b, rel_tol = 1e-09, abs_tol=0.0):
    """

    isclose -> bool

    --``a``, ``b`` are values to compare
    --``rel_tol`` is the relative allowable tolerance, taken as fraction of the
        larger of a and b
    --``abs_tol`` is the absolute allowable tolerance

    This method provides a means for comparing two numbers by "fuzzy equals",
    copied from documentation for math.isclose method in Py35
    """
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)
