#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2014
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Diagnostics
#Module: (Basic) Model_01_Retail.__init__

#Module follows standard Test interface.
#Module requires that package contain a standard.pkl file.

"""
Model_01_Retail

Task loads the engine shell, runs through a script, and saves the model. 

Reporting structure: 

    result["testName"]   name of this test
    result["output"]     output object passed in as argument
    result["errors"]     a list of errors, if any, generated during .do()
                         and/or .check()
    result["completed"]  bool, did Test.do() run without generating exception
    result["passed"]     bool, did Grader determine output satisfies standard
    result["rubric"]     obj, optionally supplied by Grader to explain passed
                         status
Module interface:
====================  ==========================================================
Object                Description
====================  ==========================================================
testName              str, should be same as file name (var used for paths)
testPath              str, location of current file; derived from parent package
                      name and ``testName``
Function:

do()                  imports Task script, returns result, including output from
                      Task.do()
check()               checks result from do() against a standard
====================  ==========================================================
"""
#imports
import dill as pickle
import sys
import traceback

#globals
testName = "Model_01_Retail"
testPath = "Tests" + "\\" + "Basic" + "\\" + testName

def do(retainState = False):
    """

    run() -> dict

    ``result`` dictionary is a standard reporting form for tests. result
    contains 6 keys listed above. .do() fills out the values for ``output``
    and ``errors``.
    
    A Task can return any object as ``output``. Task uses output to package and
    transport data that the author of the test deems significant. The test's
    Grader module is the only object that has to know the output's interface. 

    If an exception arises when executing Task, .do() intercepts the exception
    and includes it in ``errors``.

    If ``retainState`` constructor is True, .do() sets result[``output``] to the
    state of Task.output even if an exception occurs. That is, result retains
    the state of Task.

    """
    result = {}
    result["testName"] = testName
    result["output"] = None
    result["errors"] = []
    result["completed"] = False
    result["passed"] = False
    result["rubric"] = None
    print("current build: %s \n" % sys.path[-1])
    print("running %s.do()" % testName)
    output = None
    try:
        from . import Task
        output = Task.do()
        result["output"] = output
        result["completed"] = True
        #calling Task.do() returns a dictionary object that contains
        #whatever Task wants to put in it. Necessary to pass dictionary because
        #pickle module cannot pickle a complete module itself.
    except Exception as F:
        output = F
        print("Test.do encountered an exception: ")
        print(F)
        print("running traceback funcitons")
        print("traceback.print_exc(file=sys.stdout)")
        traceback.print_exc(file=sys.stdout)
        print("traceback.print_stack(file=sys.stdout)")
        traceback.print_stack(file=sys.stdout)
        result["errors"] = [output]
        result["completed"] = False
        if retainState:
            result["output"] = Task.output
        else:
            result["output"] = None
    print("%s generated the following output: \n\t%s" % (testName,output))
    return result
    
def check(result,useRefPath = False,refPath=None):
    """
    check(result[,useRefPath=False[,refPath=None]]) -> dict

    Function checks whether output generated by Task satisfies standard.
    Builds that generate an error during .do() automatically fail. If .check()
    finds that result["errors"] is filled, it marks the result accordingly and
    skips further analysis.

    Caller can request that the function construct objects in its standard.pkl
    file using a reference build by toggling ``useRefPath`` to True. Doing so
    allows the function to compare two different builds whollistically instead
    of only following the discrete tests laid out in task and standard modules.
    
    Caller can specify the reference build path under refPath or use the latest
    reference build, which is hard-coded into the function.

    NOTE: refPath functionality not guaranteed
    Function does not clear runtime top-level namespace. Therefore, runtime may
    contain modules with identical names to those found on the refPath. The
    existing modules would then block the reference versions from being used.
    To fix, can manually implement reload or deletion functionality between
    do() and check() calls. 

    """
    print("running %s.check() on result..." % testName)
    
    if useRefPath:
        print("useRefPath: ", useRefPath)
        dRefPath = r"c:\blackbird\engine\builds\020615reference"
        if not refPath:
            refPath = dRefPath
        print("Reference Build: \n",refPath)
        print("\tappend reference build to lead sys.path; blocks test build")
        sys.path.insert(1,refPath)
    print("load standard object")
    standardPath = testPath + "\\" + "standard.pkl"
    standardFile = open(standardPath,"rb")
    standardObj = pickle.load(standardFile)
    print("\tstandard object loaded")
    standardFile.close()
    if useRefPath:
        print("remove ref build from sys.path")
        sys.path.remove(refPath)
        #ref build path will be at the front of sys.path (because we inserted it
        #there), whereas test build path will be at the end. in the event that ref
        #path is identical to the build path, list.remove() will delete the first
        #instance it finds, so one copy, at the end, will remain. 
    from . import Grader
    print("first, check whether build completed do() without generating an exception.")
    print("that is, check whether output is a descendant of the Exception class.")
    if result["errors"] != []: 
        print(".do() generated an exception. conclude verification.")
        result["completed"] = False
    else:
        result["completed"] = True
        print("build completed test.do() successfully.")
        print("compare output to standard.")
        passed, rubric = Grader.check(result,standardObj)
        result["passed"] = passed
        result["rubric"] = rubric
        print("%s result: %s \n" % (testName,result["passed"]))
    return passed


    
