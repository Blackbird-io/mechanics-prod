#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2014
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Diagnostics
#Module: tester
"""

Module provides testing tools for Blackbird Engine.
====================  ==========================================================
Object                Description
====================  ==========================================================

DATA:
FOLDER_NAME           name of storage folder for diagnostics logs

FUNCTIONS:
generate_standard()   run tests, save output as standard in test folder
print_result()        pretty print for standard result dictionary
run_battery()         returns dict w results for each test
run_test()            returns bool, run task then grader for a single test
run_test_do()         returns dict, use build to perform one test's task
run_test_check()      returns True if build output passes test, else False
make_test()           generates a new test from a script
====================  ==========================================================
"""




# imports:
import compileall
import copy
import dill as pickle
import imp
import inspect
import os
import shutil
import string
import sys
import time

from datetime import datetime
from fnmatch import fnmatch




# Constants
FOLDER_NAME = r"diagnostics_log"  # Address for log folder with respect to cwd.

# Constants for make_test
LOG_FILE_NAME = r"\log.txt"
MAIN_TEMPLATE_DIR = r".\tests\templates"
SCRIPT_DIR = r".\scripts"
TEMPLATE_DIR = MAIN_TEMPLATE_DIR + r"\_rev_test_template"
TEST_PATH = r".\tests"
_GRADER_FILE = r"\grader.py"
_INIT_FILE = r"\__init__.py"
_P = r"."
_TASK_FILE = r"\task.py"

# Template test file lines to replace
_IMPORT_SCRIPT_BM = "from scripts import template_module as seed  " \
                    "# REPLACE WITH ACTUAL TO USE\n"
_MODULE_INIT_LOCATION_BM = "#Module: Tests.Basic.interview_test_template." \
                           "__init__\n"
_MODULE_TASK_LOCATION_BM = "#Module: Tests.Basic.interview_template.Task\n"
_NAME_VAR_BM = 'name = "interview_test_template"\n'
_SCRIPT_TEMPLATE_BM = "SCRIPT: TEMPLATE\n"


# Functions
def generate_standard(build_path, *tests, overwrite=False):
    """


    generate_standard() -> None


    For each test in tests, function stores the result as the standard in
    the test's directory. The result object contains the test's output and
    other identifying information. 
    """
    for test in tests:
        #Work in five steps.
        #
        #1. figure out where test lives, relative to cwd
        path_for_test = inspect.getfile(test)
        path_for_test_folder = os.path.dirname(path_for_test)
        file_name = "standard.pkl"
        path_for_file = path_for_test_folder + "\\" + file_name
        #normalize file path
        path_for_file = os.path.normpath(path_for_file)
        #
        #2. check if file exists
        exists = os.path.exists(path_for_file)
        if exists and not overwrite:
            c = "File named ``%s`` already in place in \n%s\n\n."
            c = c % (file_name, path_for_test_folder)
            raise Exception(c)
        #
        #3. run the test
        result = run_test_do(build_path, test)
        #
        #4. pull out the output and save it to
        completed = result["completed"]
        if not completed:
            c = "Test ``%s`` failed to complete. Function only makes standards "
            c += "\nfrom working tests."
            c = c % test.name
            raise Exception(c)
            #use generic exceptions here to avoid unnecessary dependancies.
        standard = result
        file = open(path_for_file, "wb")
        pickle.dump(standard, file)
        #
        #5. close file
        file.close()
    #the end


def print_result(result, truncate=True):
    """


    print_result() -> None

    
    Pretty print function for standard ``result`` dictionary.
    """
    k_order = ["name",
               "testName",
               "output",
               "errors",
               "completed",
               "passed",
               "rubric"]
    trunc_length = 20
    for key in k_order:
        space = 15 - len(key)
        line = "\t%s:"+space*" "+"%s \n"
        try:
            val = result[key]
            val_length = len(str(val))
            if truncate and val_length > trunc_length:
                val = "... (truncated)"
            print(line % (key,val))
        except KeyError:
            continue
    print("")


def run_battery(build_path, *battery, force_finish=False):
    """


    run_test() -> dict()

    -- ``build_path`` must be a string path for an existing directory;
    -- ``battery`` should be one or more test modules.

    Function calls run_test() for each test in battery. Function collates
    pass status for each test into a dictionary by test name. Function always
    logs and times each test.

    Function stops working after first fail, unless ``force_finish`` is True. 
    """    
    #if finished = True, always finish,
                      #always log
    tracker = dict()
    for test in battery:
        name = test.name
        status = run_test(build_path, test, log = True, timer = True)
        tracker[test.name] = status
        if any([status, force_finish]):
            continue
        else:
            break
    return tracker


def run_test(build_path, test, log=False, timer=False):
    """


    run_test() -> bool


    Function gets build output for Task through run_test_do, then grades it
    with run_test_check. Returns True if build passes test, False otherwise.

    -- ``build_path`` must be a string path for an existing directory.
    -- ``test`` must be the test **module**
    -- ``log``, when True, saves trace to build's DiagnosticsLog folder
    -- ``timer``, when True, times Grader analysis
    """
    r = run_test_do(build_path, test, log = log, timer = timer)
    s = run_test_check(build_path, test, r, log = log, timer = timer)
    #
    return s


def run_test_do(build_path, test, log=False, timer=False, retain_state=False,):
    """


    run_test_do() -> dict


    Function runs the task portion of the specified test module for the build in
    bLocation.
  
    Function returns a dictionary in the standard test reporting format. See
    test module doc string for details on the response contents.
    
    -- ``build_path`` must be a string path for an existing directory;
    -- ``test`` must be the test **module**;
    -- ``log``, when True, saves trace to build's DiagnosticsLog folder;
    -- ``timer``, when True, times Grader analysis;
    -- ``retain_state``: if True, test attempts to preserve state on exceptions.

    NOTE: Function switches CWD to build_path for the duration of the test
    
    Function returns to the original working directory after the test completes
    operation. 
    """
    #
    bLocation = os.path.normpath(build_path)
    #make bLocation system-neutral
    #
    if not os.path.exists(bLocation):
        status = "build location does not exist"
        return status
    #
    #append bLocation to PYTHON_PATH so build modules can run imports as they
    #expect
    sys.path.append(bLocation)
    #
    #changing working directory so testing files can locate and store inputs
    #relative to the testing modules' location within root dir
    starting_wd = os.getcwd()
    ##    os.chdir(bLocation)
    #
    if log:
        dFolderPath = bLocation+"\\"+FOLDER_NAME
        dFolderPath = os.path.normpath(dFolderPath)
        #create a system-neutral path
        #
        #place a diagnostic log folder in the build directory
        if not os.path.exists(dFolderPath):
            os.makedirs(dFolderPath)
        ft = time.localtime()
        sFolderName = str(ft.tm_mon)+str(ft.tm_mday)+str(ft.tm_year)
        sFolderPath = dFolderPath + "\\" + sFolderName
        sFolderPath = os.path.normpath(sFolderPath)
        #create a system-neutral path
        #
        if not os.path.exists(sFolderPath):
            os.makedirs(sFolderPath)
        #
        #support old and new style names
        test_name = getattr(test, "name", None)
        if not test_name:
            test_name = test.testName
            #support old and new test module formats
        test_name = test_name[:20]
        #trunkate long test names for storage
        #
        logFilePath = sFolderPath + "\\" + test_name + "_do"+".txt"
        logFilePath = os.path.normpath(logFilePath)
        #create a system-neutral path
        #
        logFile = open(logFilePath,"w")
        sys.stdout = logFile
    tStart = time.time()
    result = test.do(retain_state)
    tEnd = time.time()
    tRun = tEnd - tStart
    if timer:
        print("start time: ",tStart)
        print("end time:   ", tEnd)
        print("run time:   ",tRun)
    if log:
        h1 = "\nRESULT:"
        print("*"*40)
        print(h1)
        print_result(result)
        logFile.close()
    #
    #revert back to original stdout and working dir
    os.chdir(starting_wd)
    sys.stdout = sys.__stdout__
    #
    return result


def run_test_check(build_path, test, result, log=False, timer=False):
    """


    run_test_check() -> bool
                   

    Function returns True if Grader is satisfied with result, False otherwise.

    -- ``build_path`` must be a string path for an existing directory;
    -- ``test`` must be the test **module**;
    -- ``result`` should be the build's Task result;
    -- ``log``, when True, saves trace to build's DiagnosticsLog folder;
    -- ``timer``, when True, times Grader analysis.
    """
    #
    bLocation = os.path.normpath(build_path)
    #make bLocation system-neutral
    #
    #change working directory so testing files can locate and store inputs
    #relative to the testing modules' location within root dir
    starting_wd = os.getcwd()
##    os.chdir(bLocation)
    #
    if log:
        dFolderPath = bLocation+"\\"+FOLDER_NAME
        dFolderPath = os.path.normpath(dFolderPath)
        #create a system-neutral path
        #
        #place a diagnostic log folder in the build directory
        if not os.path.exists(dFolderPath):
            os.makedirs(dFolderPath)
        ft = time.localtime()
        sFolderName = str(ft.tm_mon)+str(ft.tm_mday)+str(ft.tm_year)
        sFolderPath = dFolderPath + "\\" + sFolderName
        sFolderPath = os.path.normpath(sFolderPath)
        #create a system-neutral path
        #
        if not os.path.exists(sFolderPath):
            os.makedirs(sFolderPath)
        #
        #support old and new style test names
        test_name = getattr(test, "name", None)
        if not test_name:
            test_name = test.testName
        test_name = test_name[:20]
        #trunkate long test names for storage
        #
        logFilePath = sFolderPath + "\\" + test_name + "_check"+".txt"
        logFilePath = os.path.normpath(logFilePath)
        #create a system-neutral path
        #
        logFile = open(logFilePath,"w")
        sys.stdout = logFile
    tStart = time.time()
    passed = test.check(result)
    tEnd = time.time()
    tRun = tEnd-tStart
    if timer:
        print("start time: ",tStart)
        print("end time:   ", tEnd)
        print("run time:   ",tRun)
    print("*"*40)
    print("PASSED: ",passed)
    print("*"*40)
    if log:
        logFile.close()
    #
    #revert back to original stdout and working dir
    os.chdir(starting_wd)
    sys.stdout = sys.__stdout__
    #
    return passed


def make_test(script, desc, directory, battery):
    """


    make_test() -> None


    Function creates a test from script using _rev_test_template files,
    generates standard for new test, and confirms correct build by running test.

    -- ``script`` must be a string name for an existing script (without .py)
        that is stored in the core\scripts folder;
    -- ``desc`` must be a string describing the script/test;
    -- ``directory`` must be a string name for the test directory in which to
        store the test, can be existing or new
    -- ``battery`` must be the string name of the battery to which the test
        belongs; can be a new or existing battery
    """

    # check if script module exists
    script_path = (SCRIPT_DIR + r"\%s.py" % script)
    if not os.path.isfile(script_path):
        msg = "!ERROR: This script ("+script+") does not exist in the " \
                                         "scripts folder!"
        print(msg)
        exit()
    else:
        base_path = TEST_PATH + r"\%s" % directory

        # first, check if directory where test will live exists
        if not os.path.isdir(base_path):
            # directory doesn't exist, have to make it
            os.mkdir(base_path)

            # also need to add __init__.py file
            template_file = MAIN_TEMPLATE_DIR + _INIT_FILE
            newtest_file = base_path + _INIT_FILE
            shutil.copy(template_file, newtest_file)

            # within tests\__init__.py look for #imports to add new module
            _add_module_to_tests(TEST_PATH, directory)

        # use first two "words" in script filename to try to divine what
        # the test folder name should be
        temp = script.split('_')
        dir_name = temp[0]+"_"+temp[1]

        # check if the proposed test name already exists in this directory
        path_check = base_path + r"\%s" % dir_name
        while os.path.isdir(path_check):
            # directory exists, see if it contains a test for this script
            txt = open(path_check+_TASK_FILE)
            check_text = "from scripts import * as seed*"

            # find line designating script
            while True:
                txt_temp = txt.readline()
                if fnmatch(txt_temp, check_text):
                    txt.close()
                    break

            temp = txt_temp.split(' ')
            if temp[3] == script:
                # file contains the script
                # -> print error and tell user this test has been made
                #    already
                msg = "!ERROR: The test associated with this script ("+\
                      script+".py) has already been made!\n"
                print(msg)
                exit()
            else:
                # file does NOT contain this script, ask user to supply
                # a valid test name
                msg = "!ERROR: A test named "+dir_name+" has already "\
                      "been created.  Please supply a valid test name:  "
                dir_name = input(msg)
                dir_name = dir_name.strip()
                dir_name = dir_name.replace(" ", "_")

                path_check = base_path + r"\%s" % dir_name

        # make the directory using non-conflicting name determined above
        os.mkdir(path_check)

        # create new log file and open for writing
        logfile = open(path_check + LOG_FILE_NAME,"x")
        logfile.write(str(datetime.today())+"\n")
        logfile.write("Creating test "+dir_name+" from script: " +
                      script+".py\n")

        # copy template grader.py file form _rev_test_template normally
        shutil.copy(TEMPLATE_DIR+_GRADER_FILE, path_check+_GRADER_FILE)
        logfile.write("Copied grader.py template.\n")

        # make dictionary of lines to replace and their new values
        rep_dict = dict()
        rep_dict[_MODULE_INIT_LOCATION_BM]\
            = "#Module: Tests."+directory+"."+dir_name+".__init__\n"
        rep_dict[_NAME_VAR_BM] = 'name = "'+desc+'"\n'
        rep_dict[_MODULE_TASK_LOCATION_BM]\
            = "#Module: Tests."+directory+"."+dir_name+".Task\n"
        rep_dict[_SCRIPT_TEMPLATE_BM] = "SCRIPT: "+script+"\n"
        rep_dict[_IMPORT_SCRIPT_BM] = "from scripts import "+script + \
                                      " as seed\n"

        # update __init__.py with description of script/test
        _file_copy_by_line_w_replace(TEMPLATE_DIR+_INIT_FILE,
                                     path_check+_INIT_FILE,
                                     rep_dict)
        logfile.write("Finished line-by-line custom copy of __init__.py "
                      "template.\n")

        # update task.py with module name to import
        _file_copy_by_line_w_replace(TEMPLATE_DIR+_TASK_FILE,
                                     path_check+_TASK_FILE,
                                     rep_dict)

        logfile.write("Finished line-by-line custom copy of task.py "
                      "template.\n")

        # Add test to appropriate battery in test_directory.__init__
        _add_basic_test_module(base_path, dir_name, battery)
        logfile.write("Added new test to "+directory+" module.\n")
        logfile.write("Added new test to "+battery+" battery.\n")

        # need to compile and import here, otherwise new module will
        # not be included, will also reload later
        compileall.compile_dir(TEST_PATH, maxlevels=20)
        import tests

        # generate_standard using this framework
        module = getattr(tests, directory)
        imp.reload(module)  # gotta re-load it so we can use it

        t = getattr(module, dir_name)
        generate_standard(_P, t, overwrite=False)
        logfile.write("Standard generated for new test.\n")

        # run_test and confirm build passes
        res = run_test(_P, t, log=True)
        logfile.write("Test run and passed: "+str(res)+"\n")
        logfile.write("See detailed results in diagnostics_log folder.\n")
        logfile.close()

        print("New test created for script ("+script+") and stored in "
              "tests (" + path_check + ").")
        print("See log file in test folder for details. Test passed: "
              + str(res))


def _add_import_to_lines(file_lines, insert_marker, insert_text):
    """


    _add_import_to_lines() -> list


    Function adds new import to import section of __init__ file

    -- ``file_lines`` must be a list of file lines
    -- ``insert_marker`` must be a string indicating where new imports
        are to be added
    -- ``insert_text`` must be the string containing the new import text
    """

    for i, line in enumerate(file_lines):
        # check to see if it's time to import the new test
        if insert_marker in line:
            file_lines.insert(i+1, insert_text)
            break

    return file_lines


def _add_module_to_tests(TEST_PATH, new_module):
    """


    _add_module_to_tests() -> None


    Function copies contents of main test directory __init__ file and adds
    new modules to the imports

    -- ``TEST_PATH`` must be a string path to the main test directory
    -- ``new_module`` must be the name of the newly created directory
    """
    fpath = TEST_PATH + r"\__init__.py"
    insert_marker = '#imports'
    insert_text = "from . import "+new_module+"\n"

    # Read in basic.__init__.py file as-is, line by line
    file = open(fpath,"r")
    init_lines = file.readlines()
    file.close()

    # Add import
    init_lines = _add_import_to_lines(init_lines, insert_marker,
                                      insert_text)

    # Now open basic.__init__.py to write modifications
    init = open(fpath, "w")

    for line in init_lines:
        init.write(line)

    init.close()


def _file_copy_by_line_w_replace(old_file, new_file, rep_dict):
    """


    _file_copy_by_line_w_replace() -> None


    Function copies old_file content to new_file replacing lines as indicated
    in rep_dict

    -- ``old_file`` must be a string path to the file to read
    -- ``new_file`` must be string path to new file to write
    -- ``rep_dict`` must be a dictionary containing lines and their replacement
    """
    file = open(old_file,"r")
    file_lines = file.readlines()
    file.close()

    new_text = open(new_file, "x")

    for line in file_lines:
        if line in rep_dict.keys():
            new_text.write(rep_dict[line])
        elif line == "":
            break
        else:
            new_text.write(line)

    new_text.close()


def _add_basic_test_module(test_directory, test, battery):
    """


    add_basic_test_module() -> None


    Function adds new test to the specified battery to be available for testers

    -- ``test`` must be the string name of the new test module
    -- ``battery`` must be the string name of the battery to which the test
        belongs; can be a new or existing battery
    """

    fpath = test_directory + _INIT_FILE
    check_text = 'batteries["'+battery+'"]'
    end_text = "]"
    insert_marker = '# placeholder for new imports'
    insert_text = "from . import "+test+"\n"

    # Read in test_directory.__init__.py file as-is, line by line
    file = open(fpath,"r")
    init_lines = file.readlines()
    file.close()

    # Add new import to lines
    init_lines = _add_import_to_lines(init_lines, insert_marker,
                                      insert_text)

    # Now open test_directory.__init__.py to write modifications
    init = open(fpath,"w")

    batt_found = False  # has the appropriate battery been found
    line_added = False  # has the new test been added to the battery
    for line in init_lines:
        # check if it's time to add the test to a battery
        if check_text in line:
            batt_found = True

            # check to see if this battery has only one entry,
            #  append here if so
            temp = line.split('=')
            check_this = temp[1]
            if end_text in check_this:
                # guestimate the num of blanks from last line for good format
                blanks = ' '*(len(last_line) - len(test))

                new_line = temp[0]+"="+temp[1][:-3]+'",\n'
                init.write(new_line)
                init.write(blanks+test+']\n')
                line_added = True
            else:
                init.write(line)
        elif batt_found and not line_added:
            # check here for last entry in battery
            if end_text in line:
                # get correct number of blanks from last line for good format
                blanks = ' '*(len(line) - len(line.strip(' ')))

                idx = line.index(end_text)
                new_end = line[idx:]

                new_line = line[:idx]+',\n'
                init.write(new_line)

                new_line = blanks+test+new_end
                init.write(new_line)
                line_added = True
            else:
                init.write(line)
        else:
            # otherwise just a normal line, regurgitate it
            init.write(line)

        # save this line for use in formatting if needed
        last_line = line

    if not batt_found:
        # We need to add a new battery
        line = '\nbatteries["'+battery+'"] = ['+test+']\n'
        init.write(line)

    init.close()
