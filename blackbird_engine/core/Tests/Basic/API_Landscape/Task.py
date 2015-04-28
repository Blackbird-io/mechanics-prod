#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Diagnostics
#Module: Tests.Basic.API_Landscape.Task
"""
Task for API_Landscape

Load a pickled PortalModel, call Engine.get_landscape_summary(), pick out the
landscape summary, store summary in output for Grader review. 

====================  ==========================================================
Object                Description
====================  ==========================================================

DATA:
output                dict; populated on do()
retail_script         dict; from Retail2_Raw.answers

FUNCTIONS:
do()                  runs through interview, populates output

CLASSES:
n/a
====================  ==========================================================
"""




#imports
import dill

import Shell as Engine




#globals
output = {}
path = r"Tests\Basic\API_Landscape\starting_model.pkl"

#functions
def do():
    """


    Task.do() -> dict()

    
    NOTE: Task.do() must always return output.

    Output is usually a dictionary of data. Output can be any object that the
    Grader for this Test understands

    Function runs through an interview script until Engine declares completion. 
    """
    #
    #T18.01
    #
    c = """
    Start with a completed PortalModel stored in a file. The PortalModel
    includes all API-spec attributes and an e_model string. Call
    Shell.get_landscape_summary() on the PortalModel. Function should deliver
    a len-2 list of [PortalModel, LandscapeSummary].
    """
    print(c)
    #
    print("Load PortalModel from file.")
    c = "path: %s\n" % path
    print(c)
    #
    file = open(path, "rb")
    starting_model = dill.load(file)
    file.close()
    #
    c = """
    file = open(path, "rb")
    starting_model = dill.load(file)
    file.close()
    """
    print(c)
    #
    f_output = Engine.get_landscape_summary(starting_model)
    new_land = f_output[1]
    output["T18.01"] = dict()
    output["T18.01"]["new land"] = new_land
    #
    c = """
    f_output = Engine.get_landscape_summary(starting_model)
    new_land = f_output[1]
    output["T18.01"] = dict()
    output["T18.01"]["new land"] = new_land
    """
    print(c)
    #
    c = """
    Engine successfully delivered output for grading. 
    """
    print(c)
    #
    #
    return output
    #
    #
    #













