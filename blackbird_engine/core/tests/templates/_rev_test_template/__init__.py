#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2014
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Diagnostics
#Module: Tests.Basic.interview_test_template.__init__
"""
Standard test interface module. See the 4-step Quick Use instructions in
task. 

Reporting structure: 

    result["name"]       name of this test
    result["output"]     output object passed in as argument
    result["errors"]     a list of errors, if any, generated during run
    result["completed"]  bool, did Test.do() run without generating exception
    result["passed"]     bool, did grader determine output satisfies standard
    result["rubric"]     obj, optionally supplied by grader to explain passed
                         status
Module interface:
====================  ==========================================================
Object                Description
====================  ==========================================================

DATA:
name                  str, descriptive test name

FUNCTIONS:
do()                  runs local task script, returns output
check()               compares output to standard, returns bool status
====================  ==========================================================
"""




#imports
import inspect
import os
import sys
import traceback

import dill as pickle

#globals
name = "interview_test_template"
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
    
    A task can return any object as ``output``. task uses output to package and
    transport data that the author of the test deems significant. The test's
    grader module is the only object that has to know the output's interface. 

    If an exception arises when executing task, .do() intercepts the exception
    and includes it in ``errors``.

    If ``retain_state`` constructor is True, .do() sets result[``output``] to
    task.output after an exception. 
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
    print("Running task.do() for ``%s`` test . . . .\n\n" % name)
    output = None
    try:
        from . import task
        output = task.do()
        result["output"] = output
        result["completed"] = True
        #calling task.do() returns a dictionary object that contains
        #whatever task wants to put in it. Necessary to pass dictionary because
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
            result["output"] = task.output
        else:
            result["output"] = None
    print(border)
    return result
    
def check(result):
    """


    check(result) -> bool


    Function checks whether output generated by task satisfies standard.
    Builds that generate an error during .do() automatically fail. 
    """
    print(border)
    c = "Running check() on ``%s`` result . . . .\n\n" % name
    print(c)
    #1. get grader
    from . import grader
    #2. get standard file by piggy-backing on relative imports
    path_for_test = inspect.getfile(grader)
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
        c = "No exceptions in result, build completed task successfully."
        print(c)
        c = "\n\nSecond, check whether output matches standard."
        print(c)
        passed, rubric = grader.check(result, standard_obj)
        result["passed"] = passed
        result["rubric"] = rubric
    #
    print(border)
    return passed


    
