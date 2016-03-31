#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2016
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL

#Blackbird Diagnostics
#Module: testing_shell
"""

Module provides command line testing tools for Blackbird Engine.
====================  ==========================================================
Object                Description
====================  ==========================================================

DATA:
N/A

FUNCTIONS:
N/A

CLASSES:
N/A

COMMAND LINE OPTIONS:
run_test              sub-command containing the following options:
--all                 run all tests in all batteries
--battery             run a specific battery, use -ls to get designations
--list                list all available batteries and test
--test                run a specific test, use -ls to get designations
--verbose             print test output to screen instead of logging

make_test             sub-command containing the following options:
--generate_standard   generate standard for the specified test
--make_test           make a new test from a given script; asks user for
                      necessary inputs
--make_test_and_generate_standard
                      runs make_test routine then makes a new process to
                      generate the standard for the new test
====================  ==========================================================
"""


if __name__ == "__main__":

    #imports:
    import argparse
    import os
    import string
    import subprocess
    import sys

    from test_suite import test_maker
    from test_suite import tester
    from test_suite import testing_tools




    # Constants:
    THIS_FILE_PATH = os.path.dirname(os.path.realpath(__file__))

    _BATCH_FILE_NAME = "generate_standard.bat"
    _GENERATE_STANDARD = "generate_standard"
    _LEGAL_CHARS = "-_. %s%s" % (string.ascii_letters, string.digits)
    _MAKE_TEST = "make_test"
    _P = os.path.join(THIS_FILE_PATH, "test_suite")
    _PASS_FAIL = {True: "Passed", False: "Failed"}
    _RUN_TEST = "run_test"

    # Do some prep work to make useful help screens and option lists
    batt_dict = testing_tools.make_test_dicts()

    # Get a parser and add subparsers
    parser = argparse.ArgumentParser(description="Command line test functionality "
                                                 "for engine.  Use sub-commands "
                                                 "{run_test, make_test} to access "
                                                 "specified functionality.")
    subparsers = parser.add_subparsers(dest="mode")

    # run_test mode------------------------------------------------------------
    run_test = subparsers.add_parser(_RUN_TEST,
                                     description="Sub-command for running "
                                                 "tests. Automatically logs "
                                                 "and summarizes test "
                                                 "results.",
                                     help="sub-command to access functionality"
                                          " for running tests")

    run_test.add_argument("-a", "--all", help="run all tests in all batteries",
                          action="store_true")
    run_test.add_argument("-b", "--battery", type=str,
                          choices=batt_dict.keys(),
                          metavar='', help="run a specific battery, "
                                           "use -ls to get designations")
    run_test.add_argument("-t", "--test", type=str, metavar='',
                          help="run a specific test within the specified "
                               "battery, use -ls to get designations")
    run_test.add_argument("-ls", "--list",
                          help="list all available batteries and tests",
                          action="store_true")
    run_test.add_argument("-v", "--verbose",
                          help="print output to screen, do not log",
                          action="store_true")

    # make_test mode-----------------------------------------------------------
    make_test = subparsers.add_parser(_MAKE_TEST,
                                      description="Sub-command for making "
                                                  "tests.",
                                      help="sub-command to access "
                                           "functionality for making tests")

    # generate_standard mode---------------------------------------------------
    gen_standard = subparsers.add_parser(_GENERATE_STANDARD,
                                         description="Sub-command for "
                                                     "generating standards "
                                                     "for new tests.",
                                         help="sub-command to access "
                                              "functionality for generating "
                                              "standards")

    gen_standard.add_argument("-g", "--generate_standard", nargs=2,
                              metavar=("BATTERY_DESIGNATION",
                                       "TEST_DESIGNATION"),
                              help="generate the standard for the specified "
                                   "test in the specified battery, use -ls to"
                                   " get designations")
    gen_standard.add_argument("-ls", "--list",
                              help="list all available batteries and tests",
                              action="store_true")

    # Printing function for sub-command helps
    def _print_help(subpar, name):
        """


        _print_help() -> None

        --``subpar`` must be a valid subparser instance
        --``name`` must be the string name of the subparser
        Prints help for specified subparser.
        """
        if len(name) < 9:
            blanks = " "*(9 - len(name))
        else:
            blanks = ""

        print("""

        *******************************************************************
        *             Using testing_shell in %s mode:%s              *
        *******************************************************************

        """ % (name, blanks))
        subpar.print_help()


    # Printing function for test and battery options
    def _list_options():
        """


        _list_options() -> None

        Prints the list of all available tests and batteries..
        """

        list_dict = testing_tools.make_test_dicts()

        print("""
        *******************************************************************
        *                      Available Batteries                        *
        * Use -b with the given designation to select a specific battery. *
        *******************************************************************
        """)
        for k in list_dict.keys():
            print(k+': '+list_dict[k][0])

        print("")

        print("""
        *******************************************************************
        *                         Available Tests                         *
        *  Use -t with two-letter designation to select a specific test.  *
        * When selecting a specific test, battery must also be specified. *
        *******************************************************************
        """)
        for k in list_dict.keys():
            print("Tests in "+k+' Battery')
            print("-----------------------------------")

            test_dict_temp = list_dict[k][2]

            for t in test_dict_temp.keys():
                print(t+': '+test_dict_temp[t].name)

            # add blank lines between batteries for clarity
            print("")
            print("")


    # Process user input
    args = parser.parse_args()

    if args.mode is None:
        print("""
        *******************************************************************
        *          Welcome to the Command Line Engine Test Tool           *
        *                                                                 *
        *******************************************************************
        """)
        parser.print_help()

        # also print help for args.mode -> run_test
        _print_help(run_test, _RUN_TEST)

        # also print help for args.mode -> make_test
        _print_help(make_test, _MAKE_TEST)

        # also print help for args.mode -> generate_standard
        _print_help(gen_standard, _GENERATE_STANDARD)

    #   Complete tasks based on options entered
    if args.mode == _RUN_TEST:
        if not (args.list or args.all or args.battery or args.test or args.list or
                args.verbose or args.generate_standard):
            _print_help(run_test, _RUN_TEST)

        if args.list:
            _list_options()

        if args.verbose:
            log = False
        else:
            log = True

        # list where all test results will be summarized for printing at end
        summary = []

        # Run all available tests in all available batteries
        if args.all:
            for k in batt_dict.keys():
                summary.append("Tests in "+k+' Battery')
                summary.append("-----------------------------------")
                print("Running tests in "+k+" battery...")

                battery = batt_dict[k][1]
                for test in battery:
                    print("Running test: "+test.name+"...")
                    result = tester.run_test(_P, test, log=log)
                    summary.append("Test "+_PASS_FAIL[result]+": "+test.name)

                # add blank lines between batteries for clarity
                summary.extend(["", ""])

        # Run all tests in battery if particular test not specified
        if args.battery and not args.test:
            summary.append("Tests in "+args.battery+' Battery')
            summary.append("-----------------------------------")
            print("Running tests in "+args.battery+" battery...")

            battery = batt_dict[args.battery][1]
            for test in battery:
                print("Running test: "+test.name+"...")
                result = tester.run_test(_P, test, log=log)
                summary.append("Test "+_PASS_FAIL[result]+": "+test.name)

        if args.test:
            # Make sure specified test exists in the given battery, then run it
            if args.battery:
                test_dict = batt_dict[args.battery][2]

                if args.test in test_dict.keys():
                    # test exists within battery , so run it
                    print("Running test "+args.test+" in " +
                          args.battery+" battery...")
                    result = tester.run_test(_P, test_dict[args.test], log=log)
                    summary.append("Test "+_PASS_FAIL[result]+": " +
                                   test_dict[args.test].name)
                else:
                    print("ERROR: Test does not exist in specified battery.")
                    exit()
            else:
                print("ERROR: You must specify a battery (-b %s) in order to run a"
                      " specific test." % [s for s in batt_dict.keys()])
                exit()

        # Summarize test results
        if args.test or args.battery or args.all:
            print("""
            *******************************************************************
            *                          Test Results                           *
            *******************************************************************
            """)
            for l in summary:
                print(l)

    elif args.mode == _MAKE_TEST:
        # Need to get arguments for test_maker():
        # script, desc, directory, battery

        # Ask the user which script to use
        script_list = testing_tools.get_script_list()
        script_dict = dict(enumerate(script_list))

        help_string = ["("+str(k)+") "+script_dict[k]
                       for k in script_dict.keys()]

        print("\nPlease select a script on which to base this test:\n")
        for h in help_string:
            print(h)

        while True:
            script_temp = input("\nPlease enter either the number or name of"
                                " the script you wish to use:  ")
            script_temp = script_temp.strip()

            try:
                int_script_temp = int(script_temp)
            except ValueError:
                int_script_temp = None

            if int_script_temp is not None and int_script_temp in \
                    script_dict.keys():
                script = script_dict[int_script_temp]
            elif script_temp in script_list:
                script = script_temp
            else:
                # Validate selection
                print("The selected script does not exist, please try again.")
                continue

            print("Script selected: "+script)
            break

        # Ask the user for the test description
        while True:
            desc_temp = input("\nPlease enter a test description:  ")
            desc = desc_temp.strip()
            if desc == "":
                print("Test description required, please try again.")
                continue
            else:
                print("Test description: "+desc)
                break

        # Ask the user for the directory where test should be stored
        dir_list = testing_tools.get_dir_list()
        print("\nThe following test directories already exist:\n")
        for d in dir_list:
            print(d)

        while True:
            dir_temp = input("\nPlease select the directory where the test"
                             " should be stored; directory can be existing "
                             "or new:  ")

            # Need to check that dir name is valid for file name
            dir_use = dir_temp.strip()

            # Conservatively only allow dashes, dots, underscores, letters and
            # numbers in filename. Omit other special characters.
            if dir_use not in dir_list:
                dir_use = ''.join(d for d in dir_use if d in _LEGAL_CHARS)

            if dir_use == "":
                print("Valid directory required, please try again.")
                continue
            else:
                print("Test directory: "+dir_use)
                break

        # Ask the user for which battery the test belongs to
        bat_mod_dict = testing_tools.get_bat_list()
        if dir_use in bat_mod_dict.keys():
            bat_list = bat_mod_dict[dir_use]

            print("\nThe following test batteries already exist in this "
                  "directory:\n")
            for b in bat_list:
                print(b)
        else:
            bat_list = []
            print("\nThere are no existing batteries in this directory.\n")

        while True:
            bat_temp = input("\nPlease select the battery where the test "
                             "should be stored; battery can be existing or"
                             " new:  ")

            # Need to check that dir name is valid for file name, battery name
            # can be almost any chars, just not escape chars. Don't play
            # defense for now, just make sure string is not empty or only space
            battery = bat_temp.strip()

            if battery == "":
                print("Valid battery required, please try again.")
                continue
            elif battery in bat_mod_dict.values() and battery not in bat_list:
                # Need to make sure new battery is not created that will
                # conflict with existing battery in another module

                # Get directory where battery exists
                for k in bat_mod_dict.keys():
                    if battery in bat_mod_dict[k]:
                        check_dir = k
                        break

                print("The battery named %s exists in a different directory "
                      "(%s). Creating another battery of that name in this"
                      " directory will conflict with the existing battery. "
                      "Please select a different battery or start over in %s "
                      "using Ctrl+C." % (battery, check_dir, check_dir))
                continue
            else:
                print("Test battery: "+battery)
                break

        # test maker, test maker, make me a test:
        new_test = test_maker.make_test(script, desc, dir_use, battery)
        print("Test has been created successfully.")

    elif args.mode == _GENERATE_STANDARD:
        if not (args.list or args.generate_standard):
            _print_help(gen_standard, _GENERATE_STANDARD)

        if args.list:
            _list_options()

        if args.generate_standard:
            battery = args.generate_standard[0]
            test = args.generate_standard[1]

            if battery in batt_dict.keys():
                test_dict = batt_dict[battery][2]

                if test in test_dict.keys():
                    # test exists within battery , so run it
                    print("Generating standard for test "+test+" in " +
                          battery+" battery...")
                    tester.generate_standard(_P, test_dict[test])
                    print("Standard has been generated for test " + test +
                          " in " + battery + " battery.")
                else:
                    print("ERROR: You must specify a valid test (%s)." %
                          [s for s in test_dict.keys()])
                    exit()
            else:
                print("ERROR: You must specify a valid battery (%s)." %
                      [s for s in batt_dict.keys()])
                exit()

else:
    print("This module is meant only to be run from command line.  " +
          "This module is not meant to be imported.")
