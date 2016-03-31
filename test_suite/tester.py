#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2016
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL

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
====================  ==========================================================
"""




# imports:
import dill as pickle
import inspect
import os
import sys
import time




# Constants
FOLDER_NAME = r"diagnostics_log"  # Address for log folder with respect to cwd.


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
