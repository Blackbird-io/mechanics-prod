#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2014
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Diagnostics
#Module: Tester
"""

Module provides testing tools for Blackbird Engine.
====================  ==========================================================
Object                Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
generate_standard()   run test, save output as standard in test folder
print_result()        pretty print for standard result dictionary
run_battery()         --------------------->TO DO, run a bunch of tests, fail on any,
        
run_test()            --------------------->TO DO, run do then check
run_test_do()         returns dict, use build to perform one test's task
run_test_check()      returns True if build output passes test, else False
====================  ==========================================================
"""




#imports:
import copy
import dill as pickle
import inspect
import os
import sys
import time




#globals
def generate_standard(test, overwrite = False):
    """


    generate_standard(test[, overwrite = False]) -> None


    Function runs the specified test and stores the result as the standard in
    the test's directory. The result object contains the test's output and
    other identifying information. 
    """
    cwd = os.getcwd()
    
    #Work in five steps.    
    #1. figure out where test lives, relative to cwd
    path_for_test = inspect.getfile(test)
    path_for_test_folder = os.path.dirname(path_for_test)
    file_name = "standard.pkl"
    path_for_file = path_for_test_folder + "\\" + file_name
    #normalize file path
    path_for_file = os.path.normpath(path_for_file)

    #2. check if file exists
    exists = os.path.exists(path_for_file)
    if exists and not overwrite:
        c = "File named ``%s`` already in place in \n%s\n\n."
        c = c % (file_name, path_for_test_folder)
        raise Exception(c)
    
    #3. run the test
    result = run_test_do(cwd, test)
    #
    #4. pull out the output and save it to
    completed = result["completed"]
    if not completed:
        c = "Test failed to complete. Function only makes standards from "
        c += "working tests."
        raise Exception(c)
        #use generic exceptions here to avoid unnecessary dependancies.
    standard = result
    file = open(path_for_file, "wb")
    pickle.dump(standard, file)

    #5. close file
    file.close()
    #the end

def print_result(result,truncate = True):
    """


    print_result(result) -> None

    
    Pretty print function for standard ``result`` dictionary.
    """
    k_order = ["testName","output","errors","completed","passed","rubric"]
    trunc_length = 20
    for key in k_order:
        space = 15 - len(key)
        line = "\t%s:"+space*" "+"%s \n"
        val = result[key]
        val_length = len(str(val))
        if truncate and val_length > trunc_length:
            val = "... (truncated)"
        print(line % (key,val))
    print("")

def run_battery(build_path, *battery, finish = False):
    #if finished = True, always finish,
                      #always log
    tracker = dict()
    for test in battery:
        name = test.name
        status = run_test(build_path, test, log = True, timer = True)
        tracker[test.name] = status
        if any(status, force_finish):
            continue
        else:
            break
    return tracker
        
def run_test(build_path, test, log = False, timer = False):
    r = run_test_do(build_path, test, log = log, timer = timer)
    s = run_test_check(build_path, test, r, log = log, timer = timer)
    return s
    
def run_test_do(build_path,
                test,
                log = False,
                timer = False,
                retain_state = False,):
    """


    run_test_do(build_path, test [, log = False
                                 [, timer = False
                                 [, retain_state = False]]]) -> dict


    Function runs the task portion of the specified test module for the build in
    bLocation.
  
    Function returns a dictionary in the standard test reporting format. See
    test module doc string for details on the response contents.
    
    -- ``build_path`` must be an existing directory. 
    -- ``log``: if True, function prints a report to the build's DiagnosticsLog
       folder; otherwise, function prints report to stdout
    -- ``timer``: if True, function times how long the test's task takes.
    -- ``retain_state``: if True, test attempts to preserve state on exceptions.

    NOTE: Function switches CWD to bLocation for the duration of the test
    
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
        dFolderName = r"DiagnosticsLog"
        dFolderPath = bLocation+"\\"+dFolderName
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
        logFilePath = sFolderPath + "\\" + test.testName + "_do"+".txt"
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

def run_test_check(bLocation,
                   test,
                   result,
                   log = False,
                   timer = False):
    """


    run_test_check(bLocation, test, result
                                [, log = False
                                [, timer = False]]) -> bool


    Function returns True if the test's Grader module finds result satisfactory,
    and False otherwise.

    E.g.:

    >>> import Tests
    >>> import Tester
    >>> p = r"c:\blackbird\blackbird_engine\core"
    >>> t = Tests.Basic.Model_01_Retail
    >>> r = Tester.runTest_do(p, t)
    >>> s = Tester.runTest_check(p, t, r)

    If ``s`` is True, build passes test ``t``. 
  
    Function returns a dictionary in the standard test reporting format. See
    test module doc string for details on the response contents.
    
    -- ``bLocation`` must be an existing directory. 
    -- ``log``: if True, function prints a report to the build's DiagnosticsLog
       folder; otherwise, function prints report to stdout
    -- ``timer``: if True, function times how long the test's task takes. 
    """
    #
    bLocation = os.path.normpath(bLocation)
    #make bLocation system-neutral
    #
    #change working directory so testing files can locate and store inputs
    #relative to the testing modules' location within root dir
    starting_wd = os.getcwd()
##    os.chdir(bLocation)
    #
    if log:
        dFolderName = r"DiagnosticsLog"
        dFolderPath = bLocation+"\\"+dFolderName
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
        logFilePath = sFolderPath + "\\" + test.testName + "_check"+".txt"
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



    
    




    

    

    
