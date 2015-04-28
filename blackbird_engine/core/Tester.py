#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2014
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Diagnostics
#Module: Tester

"""

Module provides tools for running individual tests. 
====================  ==========================================================
Object                Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
run_test_do()         returns dict, use build to perform one test's task
run_test_check()      returns True if build output passes test, else False
====================  ==========================================================
"""




#imports:
import os
import sys
import dill as pickle
import time
import copy




#functions
def run_test_do(bLocation,
                test,
                retainState = False,
                log = False,
                timer = False):
    """


    run_test_do(bLocation, test [,retainState = False
                                [, log = False
                                [, timer = False]]]) -> dict


    Function runs the task portion of the specified test module for the build in
    bLocation.
  
    Function returns a dictionary in the standard test reporting format. See
    test module doc string for details on the response contents.
    
    -- ``bLocation`` must be an existing directory. 

    -- ``retainState``: if True, test attempts to preserve state on exceptions.
    -- ``log``: if True, function prints a report to the build's DiagnosticsLog
       folder; otherwise, function prints report to stdout
    -- ``timer``: if True, function times how long the test's task takes.

    NOTE: Function switches CWD to bLocation for the duration of the test
    
    Function returns to the original working directory after the test completes
    operation. 
    """
    #
    bLocation = os.path.normpath(bLocation)
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
    os.chdir(bLocation)
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
    result = test.do(retainState)
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
    os.chdir(bLocation)
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

def print_result(result,truncate = True):
    """


    print_result(result) -> str

    
    Pretty print function for standard ``result`` dictionary.
    """
    k_order = ["testName","output","errors","completed","passed","rubric"]
    truncLength = 20
    for key in k_order:
        space = 15 - len(key)
        line = "\t%s:"+space*" "+"%s \n"
        val = result[key]
        valLength = len(str(val))
        if truncate and valLength > truncLength:
            val = "... (truncated)"
        print(line % (key,val))
    print("")  



    
    




    

    

    
