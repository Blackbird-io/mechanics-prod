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
import pdb

# Make dictionaries of tests, batteries, and designations
dest_dict = OrderedDict()
test_dict = OrderedDict()

desb_dict = OrderedDict()
batt_dict = OrderedDict()

for k in sorted(tests.basic.batteries.keys()):
    desb_dict[k[0].strip().upper()] = k
    batt_dict[k[0].strip().upper()] = tests.basic.batteries[k]

    for t in tests.basic.batteries[k]:
        temp = t.name.split(',')
        temp = temp[0].strip().upper()
        temp = temp[0]+temp[-1]

        dest_dict[temp] = t.name
        test_dict[temp] = t

#   Add command line options
parser = argparse.ArgumentParser()
parser.add_argument("-a","--all", help="run all tests in all batteries",
                    action="store_true")
parser.add_argument("-l","--log", help="log test results to file",
                    action="store_true")
parser.add_argument("-ls","--list", help="list all available batteries and tests",
                    action="store_true")
parser.add_argument("-t","--test", help="run a specific test, use -ls to get designations",
                    type=str, choices=dest_dict.keys())
parser.add_argument("-b","--battery", help="run a specific battery, use -ls to get designations",
                    type=str, choices=desb_dict.keys())
parser.add_argument("-s","--summarize",help="summarize the results of tests in-line",
                    action="store_true")

args = parser.parse_args()

p = ".\\"

#   Complete tasks based on options entered

if args.list:
    print("""
    *****************************************************************
    *                     Available Batteries                       *
    * Use -b with one-letter designation to run a specific battery. *
    *****************************************************************
    """)
    for k in desb_dict.keys():
        print(k+': '+desb_dict[k])

    print("""
    **************************************************************
    *                     Available Tests                        *
    * Use -t with two-letter designation to run a specific test. *
    **************************************************************
    """)
    for k in dest_dict.keys():
        print(k+': '+dest_dict[k])

summary = []
pass_fail = {True:"Passed", False:"Failed"}

if args.all:
    for k in tests.basic.batteries.keys():
        for t in tests.basic.batteries[k]:
            result = tester.run_test(p, t, log=args.log)
            summary.append("Test "+pass_fail[result]+": "+t.name)

if args.test:
    result = tester.run_test(p, test_dict[args.test], log=args.log)
    summary.append("Test "+pass_fail[result]+": "+test_dict[args.test].name)

if args.battery:
    for t in batt_dict[args.battery]:
        result = tester.run_test(p, t, log=args.log)
        summary.append("Test "+pass_fail[result]+": "+t.name)

if args.summarize:
    print("""
    **********************************************************
    *                     Test Results                       *
    **********************************************************
    """)
    for l in summary:
        print(l)
