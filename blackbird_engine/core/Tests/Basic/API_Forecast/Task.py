#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Diagnostics
#Module: Tests.Basic.API_Forecast.Task
"""
Task for API_Forecast

Load a pickled PortalModel, call Engine.get_landscape_summary(), pick out the
landscape summary, store summary in output for Grader review. 

====================  ==========================================================
Object                Description
====================  ==========================================================

DATA:
output                dict; populated on do()
path                  str; location of known model relative to root Engine dir

FUNCTIONS:
do()                  runs through interview, populates output

CLASSES:
n/a
====================  ==========================================================

#adding an extra comment line to make sure hg picks up changes
"""




#imports
import dill

import Shell as Engine




#globals
output = {}
path = r"Tests\Basic\portal_model_retail_2.pkl"

#functions
def do():
    """


    Task.do() -> dict()

    
    NOTE: Task.do() must always return output.

    Output is usually a dictionary of data. Output can be any object that the
    Grader for this Test understands

    Function gets 4 price and 4 size forecasts from Engine for a known model. 
    """
    #
    #T19.01
    #
    c = """
    Start with a completed PortalModel stored in a file. The PortalModel
    includes all API-spec attributes and an e_model string.
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

    c = """
    Get four size forecasts and four price forecasts. In each of the two
    categories, two forecasts (the maximum and the minimum) lie outside the
    bounds of the expected credit landscape facing the model. The remaining
    two forecasts lie within the landscape.
    """
    print(c)
    #
    
    sizes = [("$1mm", 1000000),
                 ("$5mm", 5000000),
                 ("$10mm", 10000000),
                 ("$20mm", 20000000)]
    
    prices = [("2pct", 0.02),
                  ("5pct", 0.05),
                  ("10pct", 0.10),
                  ("20pct", 0.25)]

    references = dict()
    
    #
    c = """
    sizes = [("$1mm", 1000000),
                 ("$5mm", 5000000),
                 ("$10mm", 10000000),
                 ("$20mm", 20000000)]
    
    prices = [("2pct", 0.02),
                  ("5pct", 0.05),
                  ("10pct", 0.10),
                  ("20pct", 0.25)]

    references = dict()
    """
    print(c)
    #
    
    for (label, dollars) in sizes:
        ref = Engine.get_forecast(starting_model, "size", dollars)[3]
        #get_forecast() returns len-4 list [model, fixed, ask, ref]
        references[label] = ref

    for (label, percent) in prices:
        ref = Engine.get_forecast(starting_model, "price", percent)[3]
        #get_forecast() returns len-4 list [model, fixed, ask, ref]
        references[label] = ref

    #
    c = """
    for (label, dollars) in sizes:
        ref = Engine.get_forecast(starting_model, "size", dollars)[3]
        #get_forecast() returns len-4 list [model, fixed, ask, ref]
        references[label] = ref

    for (label, percent) in prices:
        ref = Engine.get_forecast(starting_model, "price", percent)[3]
        #get_forecast() returns len-4 list [model, fixed, ask, ref]
        references[label] = ref
    """
    print(c)
    #
    
    output["T19.01"] = dict()
    output["T19.01"]["references"] = references
    #
    c = """
    output["T19.01"] = dict()
    output["T19.01"]["references"] = references
    """
    print(c)
    #
    c = """
    Engine successfully delivered all requested credit references. 
    """
    print(c)
    #
    #
    return output
    #
    #
    #













