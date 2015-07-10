#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2014
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Diagnostics
#Module: Tests.Basic.interview_test_template.__init__
"""
Standard test interface module. See the 3-step Quick Use instructions in
Task. 

Reporting structure: 

    result["name"]       name of this test
    result["output"]     output object passed in as argument
    result["errors"]     a list of errors, if any, generated during run
    result["completed"]  bool, did Test.do() run without generating exception
    result["passed"]     bool, did Grader determine output satisfies standard
    result["rubric"]     obj, optionally supplied by Grader to explain passed
                         status
Module interface:
====================  ==========================================================
Object                Description
====================  ==========================================================

DATA:
name                  str, descriptive test name

FUNCTIONS:
do()                  runs local Task script, returns output
check()               compares output to standard, returns bool status
====================  ==========================================================
"""




#imports
import dill as pickle
import inspect
import os
import sys
import traceback




#globals
name = "retail interview 4, low overhead w no pending leases."
#
element = "BLACKBIRD DIAGNOSTICS "
border = element * 100
border = border[:79]
border = "\n" + border + "\n"


#functions
def do(retain_state = False):
    """


    run() -> dict


    ``result`` dictionary is a standard reporting form for tests. result
    contains 6 keys listed above. .do() fills out the values for ``compled``,
    ``output`` and ``errors``.
    
    A Task can return any object as ``output``. Task uses output to package and
    transport data that the author of the test deems significant. The test's
    Grader module is the only object that has to know the output's interface. 

    If an exception arises when executing Task, .do() intercepts the exception
    and includes it in ``errors``.

    If ``retain_state`` constructor is True, .do() sets result[``output``] to
    Task.output after an exception. 
    """
    result = {}
    result["name"] = name
    result["output"] = None
    result["errors"] = []
    result["completed"] = False
    result["passed"] = False
    result["rubric"] = None
    print(border)
    print("Build: %s \n" % sys.path[-1])
    print("Running Task.do() for ``%s`` test . . . .\n\n" % name)
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
        print("Test.do encountered an exception: \n")
        print(F)
        print("\nrunning traceback functions")
        print("\ttraceback.print_exc(file=sys.stdout):\n")
        traceback.print_exc(file=sys.stdout)
        print("\ttraceback.print_stack(file=sys.stdout):\n")
        traceback.print_stack(file=sys.stdout)
        result["errors"] = [output]
        result["completed"] = False
        if retain_state:
            result["output"] = Task.output
        else:
            result["output"] = None
    print(border)
    return result
    
def check(result):
    """


    check(result) -> bool


    Function checks whether output generated by Task satisfies standard.
    Builds that generate an error during .do() automatically fail. 
    """
    print(border)
    c = "Running check() on ``%s`` result . . . .\n\n" % name
    print(c)
    #1. get grader
    from . import Grader
    #2. get standard file by piggy-backing on relative imports
    path_for_test = inspect.getfile(Grader)
    path_for_test_folder = os.path.dirname(path_for_test)
    file_name = "standard.pkl"
    path_for_file = path_for_test_folder + "\\" + file_name
    #normalize file path
    path_for_file = os.path.normpath(path_for_file)
   
    #3. open file, get standard object
    standard_file = open(path_for_file, "rb")
    standard_obj = pickle.load(standard_file)
    standard_file.close()
    #
    if not standard_obj["name"] == name:
        c = "Standard does not match test. \n"
        c += "\ttest name:          %s\n"
        c += "\tstandard test name: %s\n"
        c = c % (name, standard_obj["name"])
        raise Exception(c)
    #
    c = "\n\nFirst, check whether build completed result without exceptions."
    print(c)
    if result["errors"] != []:
        c = "Result includes an exception. Check failed.\n"
        print(c)
        result["completed"] = False
    else:
        result["completed"] = True
        c = "No exceptions in result, build completed Task successfully."
        print(c)
        c = "\n\nSecond, check whether output matches standard."
        print(c)
        passed, rubric = Grader.check(result, standard_obj)
        result["passed"] = passed
        result["rubric"] = rubric
    #
    print(border)
    return passed


    
