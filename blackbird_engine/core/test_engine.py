#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2016
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL

#Blackbird Diagnostics
#Module: test_engine
"""

Module provides command line testing tools for Blackbird Engine.
====================  ==========================================================
Object                Description
====================  ==========================================================

DATA:

FUNCTIONS:

CLASSES:

COMMAND LINE OPTIONS:
--all                 run all tests in all batteries
--log                 log test results to file
--list                list all available batteries and test
--test                run a specific test, use -ls to get designations
--battery             run a specific battery, use -ls to get designations
--summarize           summarize the results of tests in-line
====================  ==========================================================
"""




#imports:
import argparse
import tester
import tests
from collections import OrderedDict


# Get list of modules containing tests, ignore any modules containing "__"
test_modules = dir(tests)
test_modules = [t for t in test_modules if "__" not in t]

# battery dictionary -> battery designation: (battery name,
#  <battery module>, dictionary of tests contained by battery)
batt_dict = OrderedDict()

for m in test_modules:
    module = getattr(tests, m)
    if hasattr(module, "batteries"):
        temp_batteries = getattr(module, "batteries")

        # Make dictionaries of tests, batteries, and designations
        # Use test and battery names to assign designations
        for k in sorted(temp_batteries.keys()):
            battery = temp_batteries[k]

            # test dictionary -> test designation: <test module>
            test_dict = OrderedDict()

            # Define battery designation for command line
            adj_k = k.upper()
            adj_k = adj_k.replace(" ", "_")

            for t in battery:
                # Define test designation for command line
                temp = t.name.split(',')
                temp = temp[0].strip().upper()
                temp = temp[0]+temp[-1]

                # Add test module to test dictionary
                test_dict[temp] = t

            # battery dictionary -> battery designation: (battery name,
            # <battery module>, dictionary of tests contained by battery)
            batt_dict[adj_k] = (k, battery, test_dict)

#   Add command line options
parser = argparse.ArgumentParser(description="Command line test functionality "
                                             "for engine.  Automatically logs "
                                             "and summarizes test results.")

parser.add_argument("-a","--all", help="run all tests in all batteries",
                    action="store_true")
parser.add_argument("-ls","--list", help="list all available batteries and tests",
                    action="store_true")
parser.add_argument("-b","--battery", help="run a specific battery, use -ls to "
                                           "get designations",
                    type=str, choices=batt_dict.keys(), metavar='')
parser.add_argument("-t","--test", help="run a specific test within the "
                                        "specified battery, use -ls to get"
                                        " designations",
                    type=str, metavar='')

args = parser.parse_args()

p = r"."

if not (args.list or args.all or args.test or args.battery):
    print("""
    *****************************************************************
    *         Welcome to the Command Line Engine Test Tool          *
    *                                                               *
    *****************************************************************
    """)
    parser.print_help()


#   Complete tasks based on options entered

if args.list:
    print("""
    *****************************************************************
    *                     Available Batteries                       *
    *  Use -b with the given designation to run a specific battery. *
    *****************************************************************
    """)
    for k in batt_dict.keys():
        print(k+': '+batt_dict[k][0])

    print("")

    print("""
    *****************************************************************
    *                        Available Tests                        *
    *   Use -t with two-letter designation to run a specific test.  *
    * When running a specific test, battery must also be specified. *
    *****************************************************************
    """)
    for k in batt_dict.keys():
        print("Tests in "+k+' Battery')
        print("-----------------------------------")

        test_dict = batt_dict[k][2]

        for t in test_dict.keys():
            print(t+': '+test_dict[t].name)

        # add blank lines between batteries for clarity
        print("")
        print("")

summary = []
pass_fail = {True:"Passed", False:"Failed"}

if args.all:
    for k in batt_dict.keys():
        summary.append("Tests in "+k+' Battery')
        summary.append("-----------------------------------")
        print("Running tests in "+k+" battery...")

        battery = batt_dict[k][1]
        for test in battery:
            print("Running test: "+test.name+"...")
            result = tester.run_test(p, test, log=True)
            summary.append("Test "+pass_fail[result]+": "+test.name)

        summary.extend(["", ""]) # add blank lines between batteries for clarity

# Run all tests in battery if particular test not specified
if args.battery and not args.test:
    summary.append("Tests in "+args.battery+' Battery')
    summary.append("-----------------------------------")
    print("Running tests in "+args.battery+" battery...")

    battery = batt_dict[args.battery][1]
    for test in battery:
        print("Running test: "+test.name+"...")
        result = tester.run_test(p, test, log=True)
        summary.append("Test "+pass_fail[result]+": "+test.name)

if args.test:
    # Make sure specified test exists in the given battery, then run it
    if args.battery:
        test_dict = batt_dict[args.battery][2]

        if args.test in test_dict.keys():
            # test exists within battery , so run it
            print("Running test "+args.test+" in "+args.battery+" battery...")
            result = tester.run_test(p, test_dict[args.test], log=True)
            summary.append("Test "+pass_fail[result]+": "+
                           test_dict[args.test].name)
        else:
            print("ERROR: Test does not exist in specified battery.")
            exit()
    else:
        print("ERROR: You must specify a battery (-b %s) in order to run a" +
              " specific test." % [s for s in batt_dict.keys()])
        exit()

# Summarize test results
if args.test or args.battery or args.all:
    print("""
    *****************************************************************
    *                         Test Results                          *
    *****************************************************************
    """)
    for l in summary:
        print(l)
