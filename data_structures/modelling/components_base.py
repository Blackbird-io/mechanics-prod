# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL

# Blackbird Environment
# Module: data_structures.modelling.components_base
"""

Module defines ComponentsBase class, a container for instances of
BusinessUnit[Base].
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
ComponentsBase        container that stores instances of BusinessUnit[Base]
====================  ==========================================================
"""




# imports
import copy

import bb_exceptions
import bb_settings
import tools.for_printing as views

from tools import CasefoldDict
from data_structures.system.relationships import Relationships




# globals
# n/a

# classes
class ComponentsBase(dict):
    """

    The SummaryComponents class defines a container that stores UnitSummary
    objects keyed by their bbid.
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    by_name               dict; keys are unit names, values are unit bbids
    relationships         instance of Relationships class

    FUNCTIONS:
    add_item()            adds an object to self, keyed under obj's bbid
    get_all()             returns list of all units in instance
    get_ordered()         returns a list of values, ordered by key
    ====================  ======================================================
    """

    def __init__(self):
        dict.__init__(self)
        self.by_name = CasefoldDict()
        self.relationships = Relationships(self)

    def __str__(self, lines=None):
        """


        Components.__str__(lines = None) -> str


        Method concatenates each line in ``lines``, adds a new-line character at
        the end, and returns a string ready for printing. If ``lines`` is None,
        method calls _get_pretty_lines() on instance.
        """
        if not lines:
            lines = views.view_as_components(self)
        line_end = "\n"
        result = line_end.join(lines)
        return result

    def add_item(self, bu):
        """


        ComponentsBase.add_item() -> None

        --``bu`` is an instance of BusinessUnit or BusinessUnitBase object

        Method adds bu to the instance, keyed as bu.id.bbid. If bu does not
        specify a bbid, method raises IDError.

        Method also registers each unit's id under the unit's name in
        instance.by_name.
        """
        if not bu.id.bbid:
            c = "Cannot add a component that does not have a valid bbid."
            raise bb_exceptions.IDError(c)
        bu.relationships.set_parent(self)
        self[bu.id.bbid] = bu
        if bu.tags.name:
            self.by_name[bu.tags.name] = bu.id.bbid

    def copy(self):
        """


        ComponentsBase.copy() -> ComponentsBase


        Method returns a deep copy of components. Uses Tags.copy() to create a
        shell. Method then sets result.by_name to a blank dictionary and adds a
        copy of each unit in the instance to the result.
        """
        result = copy.copy(self)
        result.relationships = self.relationships.copy()

        # customize container
        result.clear()
        result.by_name = dict()

        # fill container (automatically add names)
        for unit in self.get_ordered():
            result.add_item(unit.copy())

        return result

    def get_all(self):
        """


        ComponentsBase.get_all() -> list


        Method returns list of all units in instance; ordered if in DEBUG_MODE,
        unordered otherwise.
        """

        if bb_settings.DEBUG_MODE:
            # Use stable order to simplify debugging
            pool = self.get_ordered()
        else:
            pool = list(self.values())

        return pool

    def get_ordered(self, order_by=None):
        """


        ComponentsBase.get_ordered() -> list


        Method returns a list of every value in the instance, ordered by key.
        """
        result = []
        for k, bu in sorted(self.items(), key=order_by):
            result.append(bu)
        return result
