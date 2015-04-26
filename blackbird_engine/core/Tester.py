#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2014
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Diagnostics
#Module: Tester

"""
This module provides diagnostic tools Blackbird Environment builds.

====================  ==========================================================
Object                Description
====================  ==========================================================

Functions:

validateBuild()       checks if build completes and passes each test in a battery
printSummary()        prints completed, passed status for each test in summary

"""
#imports:
import os
import sys
import dill as pickle
import time
import copy
import Tests

def runBattery(bLocation,battery=None,trace=False,forceFinish = False,
                  cleanUpDir = True):
    """

    runBattery(bLocation,battery=None,trace=False,forceFinish=False,
                  cleanUpDir=True) -> bool

    ``bool`` is True if the build in bLocation is valid; bool is False otherwise.

    .runBuild() locates build, appends it to sys.path, then runs each test in
    ``battery``, collects the output (which presumably relies on the build) and
    stores a pickled version of that output in the bLocation\\DiagnosticLog
    directory.

    The function then compares each test's output to its standard.
    
    .validateBuild() returns False if any test generates an exception or output
    that doesn't match up against the standard.

    Function records substantive testing operations on a log file that it places
    in the bLocation directory by redirecting sys.stdout. Function restores
    stdout to built-in default (sys.__stdout__) when it's done. 
    
    Arguments:
        ``bLocation``      a string of the top-level directory for a given
                           build, with respect to root (c:\).
        ``battery``        list of Test modules
        ``trace``          if True, function returns a tuple of (bool,summary);
                           otherwise, function returns only the bool status
        ``forceFinish``    if True, function runs through every test in battery
                           even after build fails one
        ``cleanUpDir``     delete any objects generated during testing that were
                           not found in dir() at time of call. 
    """
    if not os.path.exists(bLocation):
        status = "build location does not exist"
        return status
    if not battery: 
        battery = Tests.trial
    summary = {}
    cleanDir = dir()
    build_Valid = True
    if type(bLocation) != type(''):
        raise Exception
    sys.path.append(bLocation)
    dFolderName = r"DiagnosticsLog"
    dFolderPath = bLocation+"\\"+dFolderName
    #place a diagnostic log folder in the build directory
    if not os.path.exists(dFolderPath):
        os.makedirs(dFolderPath)
    dFilePath = dFolderPath + "\\" + "log.txt"
    logFile = open(dFilePath,"w")
    sys.stdout = logFile
    #now printing to logFile
    hLine1 = "=" * 80
    hLine2 = hLine1
    hLine3 = "Blackbird Diagnostics: TESTER"
    hLine3 = hLine3.center(80)
    hLine4 = hLine1
    hLine5 = hLine1
    hLine6 = "specified build: \n\t%s\n" % bLocation
    hLine7 = "running Tester.runBattery()"
    hLine8 = hLine1
    header = [hLine1,hLine2,hLine3,hLine4,
              hLine5,hLine6,hLine7,hLine8]
    for line in header:
        print(line)
    print("begining %s test battery ... " % battery["name"])
    startTime = time.time()
    oFolderName = "o_%s" % battery["name"]
    oFolderPath = dFolderPath + "\\" + oFolderName
    if not os.path.exists(oFolderPath):
        os.makedirs(oFolderPath)
    #NOTE: can have different batteries specified somewhere in Tests or
    #even in Validation.__init__
    oFilePattern = "out_%s"
    oFileExt = ".pkl"
    for test in battery["tests"]:
        subheader = str(test.testName)
        subheader = subheader.center(80,"*")
        print(subheader)
        oFileName = oFilePattern % test.testName
        oFileName = oFileName+oFileExt
        oFilePath = oFolderPath + "\\" + oFileName
        oFile = open(oFilePath,"wb")
        bPreResult = test.do()
        bResult = test.check(bPreResult)
        pickle.dump(bResult,oFile)
        oFile.close()
        summary[test.testName] = bResult
        if bResult["completed"] == False or bResult["passed"] == False:
            build_Valid = False
        if build_Valid == False and forceFinish == False:
            print("\nbuild failed %s. validation concluded.\n" % test.testName)
            break
        else:
            continue
    print("*"*80)
    print("*"*80)
    print("%s test battery concluded." % battery["name"])
    print("\n")
    printSummary(summary)
    if build_Valid:
        print("RESULT: Valid")
    else:
        print("RESULT: Not Valid")
    endTime = time.time()
    duration = endTime - startTime
    print("Start Time: %s" % startTime)
    print("End Time: %s" % endTime)
    print("Duration: %s" % duration)
    fLine1 = "THE END"
    fLine1 = fLine1.center(80,"=")
    fLine2 = hLine1
    footer = fLine1+"\n"+fLine2+"\n"
    print(footer)
    #clean up stdout, sys.path, dir
    sys.stdout = sys.__stdout__
    logFile.close()
    sys.path.remove(bLocation)
    usedDir = dir()
    if cleanUpDir:
        newAttrs = set(usedDir).difference(set(cleanDir))
        instruction = "del %s"
        for attr in newAttrs:
            announce = "deleting %s"
            #print(announce % attr)
            #should be an eval(del attr) here
    if trace:
        return (build_Valid,summary)
    else:
        return build_Valid

def printSummary(summary):
    """
    printSummary(summary) -> str

    For every test in summary, prints whether build (i) completed and (ii)
    passed the test. A build may not complete a test if Test.do() returns an
    exception.    
    """
    tests = list(summary.keys())
    tests.sort()
    h1 = "SUMMARY"
    h1 = h1.center(20)
    print(h1)
    for test in tests:
        c = "not completed"
        if summary[test]["completed"]:
            c = "completed"
        p = "failed"
        if summary[test]["passed"]:
            p = "passed"
        l1 = "%s: %s, %s" % (test,c,p)
        print(l1)
    print("\n")

def runTest_do(bLocation,test,retainState = False, log = False, timer = False):
    """

    runTestDo(bLocation,test[,retainState = False, log = False]) -> result

    ``result`` is a dictionary in the standard test reporting format.

    Function runs the task portion of a specified test module.

    ``bLocation`` must be an existing directory. 
    If ``retainState`` is True, test attempts to preserve state on exceptions.
    If ``log`` is True, function prints a report to the build's DiagnosticsLog
    """
    if not os.path.exists(bLocation):
        status = "build location does not exist"
        return status
    sys.path.append(bLocation)
    if log:
        dFolderName = r"DiagnosticsLog"
        dFolderPath = bLocation+"\\"+dFolderName
        #place a diagnostic log folder in the build directory
        if not os.path.exists(dFolderPath):
            os.makedirs(dFolderPath)
        ft = time.localtime()
        sFolderName = str(ft.tm_mon)+str(ft.tm_mday)+str(ft.tm_year)
        sFolderPath = dFolderPath + "\\" + sFolderName
        if not os.path.exists(sFolderPath):
            os.makedirs(sFolderPath)
        logFilePath = sFolderPath + "\\" + test.testName + "_do"+".txt"
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
        print_Result(result)
        logFile.close()
    sys.stdout = sys.__stdout__
    return result

def runTest_check(bLocation,test,result,log = False, timer = False):
    """
    bLocation required for storage path    
    """
    if log:
        dFolderName = r"DiagnosticsLog"
        dFolderPath = bLocation+"\\"+dFolderName
        #place a diagnostic log folder in the build directory
        if not os.path.exists(dFolderPath):
            os.makedirs(dFolderPath)
        ft = time.localtime()
        sFolderName = str(ft.tm_mon)+str(ft.tm_mday)+str(ft.tm_year)
        sFolderPath = dFolderPath + "\\" + sFolderName
        if not os.path.exists(sFolderPath):
            os.makedirs(sFolderPath)
        logFilePath = sFolderPath + "\\" + test.testName + "_check"+".txt"
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
    sys.stdout = sys.__stdout__
    return passed

def print_Result(result,truncate = True):
    """
    printResult(result) -> str
    
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

def logger(filePath,task,task_pargs,task_kargs,timer = True):
    """
    task_pargs must be a list
    task_kargs must be a dictionary
    """
    pass    

def timer(task,*pargs,**kargs):
    tStart = time.time()
    task(*pargs,**kargs)
    tEnd = time.time()
    return (tStart,tEnd)
    
def runTest():
    #do both
    #
    pass





    
    




    

    

    
