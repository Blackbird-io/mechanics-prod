# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL

# Blackbird Environment
# Module: data_structures.tests.test
"""

Unit tests for data_structures
Usage (from one folder up):
    python -m unittest
With coverage (from one folder up):
    coverage run tests\test.py
    coverage report -m
====================  =========================================================
Test Case             Target
====================  =========================================================
component_get_ordered Working of order_by parameter in components.get_ordered.
====================  =========================================================
"""




# Imports
import unittest, os, sys
from pkg_resources import resource_filename

# this contraption will add the location of config.py to sys.path
# config.py will then be imported, and in turn will set all additional paths
try:
    import test_suite
except:
    cwd = resource_filename(__name__, None)
    cfd = os.path.join(cwd, '../../../../Core Interface/Core-Interface')
    sys.path.insert(1, os.path.realpath(cfd))
    import config

import simple_portal
from data_structures.modelling import common_events
from test_suite.scripts.retail_3_low_sga_five_new import answers as R3
from test_suite.scripts.retail_4_no_new_stores import answers as R4
from test_suite.scripts.retail_5_no_marketing import answers as R5




# Globals
# n/a

# Tests
class component_get_ordered(unittest.TestCase):
    def test(self):
        scripts = (R3, R4, R5)
        for answers in scripts:
            simple_portal.use_script(answers, display=False)
            simple_portal.continuous()
            model = simple_portal.get_model()
            model.time_line.extrapolate()
            unit = model.time_line.current_period.content
        # test correct sorting on birth date
            sorter = lambda t: t[1].life.events[common_events.KEY_BIRTH]
            self.unit_sorted(unit, sorter)
        # test returning something with no sorter given
        # no asserts, just checking for failures
            sorter = None
            children = unit.components.get_ordered(order_by=sorter)

    def unit_sorted(self, unit, sorter):
        children = unit.components.get_ordered(order_by=sorter)
        if children:
            print(unit.name)
            for i, child in enumerate(children):
                birth_date_new = child.life.events[common_events.KEY_BIRTH]
                if i:
                    message = '    {.name:<40} {}'.format(
                        child,
                        birth_date_new,
                    )
                    print(message)
                    self.assertGreaterEqual(birth_date_new, birth_date_old)
                birth_date_old = birth_date_new


if __name__ == '__main__':
    unittest.main()
