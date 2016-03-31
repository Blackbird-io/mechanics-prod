#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2016
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL

#Blackbird Diagnostics
#Module: testing_tools
"""

Module provides tools for use by test suite for Blackbird Engine.
====================  ==========================================================
Object                Description
====================  ==========================================================

DATA:
N/A

FUNCTIONS:
get_bat_list()        returns dictionary with batteries contained in each test
                      directory
get_battery_designation()
                      determines designation for battery to use in cmd
get_dir_list()        returns list of directories in tests directory
get_script_list()     returns list of available scripts in SCRIPT_DIR
get_test_designation()determines two-letter designation for test to use in cmd
make_test_dicts()     generates dictionary of all available testing batteries
                      and tests

CLASSES:
N/A
====================  ==========================================================
"""




#imports:
import os
from collections import OrderedDict

from test_suite import tests
from test_suite import test_maker




# Constants:
DIR_SEARCH = r"test_suite\tests"


def get_bat_list():
    """


    get_bat_list() -> dict

    Function returns a dictionary containing the names of batteries stored in
    each test directory (directory: [batteries]).
    """

    # Get list of modules containing tests, ignore any modules containing "__"
    test_modules = dir(tests)
    test_modules = [t for t in test_modules if "__" not in t]

    bat_mod_dict = dict()

    for m in test_modules:
        module = getattr(tests, m)
        bat_mod_dict[m] = []
        if hasattr(module, "batteries"):
            temp_batteries = getattr(module, "batteries")

            for k in sorted(temp_batteries.keys()):
                bat_mod_dict[m].append(k)

    return bat_mod_dict


def get_battery_designation(battery):
    """


    get_battery_designation() -> str

    --``battery`` must be the string name of a battery

    Function determines and returns the designation that will be
    used to represent the battery for command-line functionality.
    """

    adj = battery.upper()
    adj = adj.replace(" ", "_")

    return adj


def get_dir_list():
    """


    get_dir_list() -> str

    Function returns list of directories in "tests" directory.
    """

    ls = [d[0] for d in os.walk(test_maker.TEST_PATH)]

    short_list = []
    for l in ls:
        if DIR_SEARCH in l:
            idx = l.find(DIR_SEARCH)
            sub_l = l[idx:]

            temp = sub_l.split("\\")
            if len(temp) >= 3:
                if "__" not in temp[2]:
                    short_list.append(temp[2])

    dir_list = set(short_list)

    return dir_list


def get_script_list():
    """


    get_script_list() -> list

    Function returns a list of the scripts within the "scripts" directory.
    """

    files = os.listdir(test_maker.SCRIPT_DIR)
    script_list = [f[:-3] for f in files if ("__" not in f and ".py" in f)]
    return sorted(script_list)


def get_test_designation(name):
    """


    get_test_designation() -> str

    --``name`` must be the string name of a test

    Function determines and returns the two-letter designation that will be
    used to represent the test for command-line functionality.
    """

    temp = name.split(',')
    temp = temp[0].strip().upper()
    temp = temp[0]+temp[-1]

    return temp


def make_test_dicts():
    """


   make_test_dicts() -> OrderedDict


    Function makes a dictionary containing all available batteries, the tests
    contained within each battery, and the designation for each test and
    battery.  batt_dict has battery_designation: tuple(battery_name,
    <battery module>, dictionary of tests {test_designation: <test module>})
    """

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
                batt_desig = get_battery_designation(k)

                for t in battery:
                    # Define test designation for command line
                    test_desig = get_test_designation(t.name)

                    # Add test module to test dictionary
                    test_dict[test_desig] = t

                # battery dictionary -> battery designation: (battery name,
                # <battery module>, dictionary of tests contained by battery)
                batt_dict[batt_desig] = (k, battery, test_dict)

    return batt_dict
