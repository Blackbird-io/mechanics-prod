# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL
# Blackbird Environment
# Module: data_structures.modelling.taxo_dir
"""

Module defines TaxiDir class.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
TaxiDir               Directory for Taxonomy units. Stored on Model.master
====================  ==========================================================
"""





# Imports
import copy
import logging

import bb_settings
import bb_exceptions

from data_structures.system.tags_mixin import TagsMixIn
from data_structures.system.bbid import ID
from data_structures.system.relationships import Relationships

from .parameters import Parameters




# Constants
# n/a

# Globals
logger = logging.getLogger(bb_settings.LOGNAME_MAIN)

# Classes
class TaxoDir(TagsMixIn):
    """

    TaxiDir objects have a bu_directory and ty_directory designed for storing
    and searching for Taxonomy BusinessUnits. These directories will be separate
    from the directories in Model.

    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    bu_directory          dict; all business units in this period, keyed by bbid
    ty_directory          dict; keys are strings, values are sets of bbids
    id                    instance of ID class
    parameters            Parameters object, specifies shared parameters
    relationships         instance of Relationships class

    FUNCTIONS:
    clear()               clears content, resets bu_directory
    copy()                returns new TaxiDir with a copy of content
    get_units()           return list of units from bbid pool
    get_lowest_units()    return list of units w/o components from bbid pool
    set_content()         attach company to period
    ====================  ======================================================
    """
    def __init__(self, model=None):
        # content is handled differently, is not passed on to base init
        TagsMixIn.__init__(self)

        self.ty_directory = dict()
        self.bu_directory = dict()
        self.financials = dict()
        self.id = ID()
        
    def clear(self):
        """


        TaxiDir.clear() -> None


        Method sets financials to empty dict and resets instance directories.
        """
        self.financials = dict()
        self._reset_directories()

    def copy(self, clean=False):
        """


        TaxiDir.copy() -> TaxiDir


        Method returns a new TaxiDir object whose content is a class-specific
        copy of the caller content.
        """
        result = copy.copy(self)

        result.tags = self.tags.copy()
        result.ty_directory = copy.copy(self.ty_directory)
        result.bu_directory = copy.copy(self.ty_directory)

        for bbid, fins in self.financials.items():
            result.financials[bbid] = fins.copy(clean=clean)

        return result

    def get_units(self, pool):
        """


        TaxiDir.get_units() -> list


        Method returns a list of objects from instance.bu_directory that
        correspond to each bbid in ``pool``. Method sorts pool prior to
        processing.

        Method expects ``pool`` to be an iterable of bbids.
        """
        pool = sorted(pool)
        # make sure to sort pool for stable output order
        units = []
        for bbid in pool:
            u = self.bu_directory[bbid]
            units.append(u)
        return units

    def get_lowest_units(self, pool=None, run_on_empty=False):
        """


        TaxiDir.get_lowest_units() -> list


        Method returns a list of units in pool that have no components.

        Method expects ``pool`` to be an iterable of bbids.

        If ``pool`` is None, method will build its own pool from all keys in
        the instance's bu_directory. Method will raise error if asked to run
        on an empty pool unless ``run_on_empty`` == True.

        NOTE: method performs identity check (``is``) for building own pool;
        accordingly, running a.select_bottom_units(pool = set()) will raise
        an exception.
        """
        if pool is None:
            pool = sorted(self.bu_directory.keys())
        else:
            pool = sorted(pool)
        #make sure to sort pool for stable output order
        #
        if any([pool, run_on_empty]):
            foundation = []
            for bbid in pool:
                bu = self.bu_directory[bbid]
                if bu.components:
                    continue
                else:
                    foundation.append(bu)
            #
            return foundation
            #
        else:
            c = "``pool`` is empty, method requires explicit permission to run."
            raise bb_exceptions.ProcessError(c)

    def register(self, bu, reset_directories=False):
        """


        TaxiDir.register() -> None

        --``bu`` is an instance of BusinessUnit or BusinessUnitBase

        Manually add unit to TaxoDir. Unit will appear in directories.

        If ``reset_directories`` is True, method will clear existing type
        and id directories. Parameter should be True when registering the
        top (company) node of a structure.
        """
        if not bu.id.bbid:
            c = "Cannot add content without a valid bbid."
            raise bb_exceptions.IDError(c)
        # Make sure unit has an id in the right namespace.

        if reset_directories:
            self._reset_directories()

        # bu._register_in_dir(self, recur=True, overwrite=False)
        # Note that Period.register normal delagates to bu._register_in_dir
        # _register_in_dir looks for bu.period which

        # Check for collisions
        if bu.id.bbid in self.bu_directory:
            c = (
                "TaxoDir.bu_directory already contains an object with "
                "the same bbid as this unit. \n"
                "unit id:         {bbid}\n"
                "known unit name: {name}\n"
                "new unit name:   {mine}\n\n"
            ).format(
                bbid=self.id.bbid,
                name=self.bu_directory[self.id.bbid].tags.name,
                mine=self.tags.name,
            )
            print(self.bu_directory)
            raise bb_exceptions.IDCollisionError(c)

        # Register the unit.
        self.bu_directory[bu.id.bbid] = bu

        brethren = self.ty_directory.setdefault(bu.type, set())
        brethren.add(bu.id.bbid)

        # Recusion DOES NOT WORK unless bu._register_in_dir works for TaxoDir
        # if recur:
        #     for unit in self.components.values():
        #         unit._register_in_dir(recur, overwrite)

    #*************************************************************************#
    #                          NON-PUBLIC METHODS                             #
    #*************************************************************************#

    def _reset_directories(self):
        """


        TaxiDir.reset_directories() -> None


        Method sets instance.bu_directory and instance.ty_directory to blank
        dictionaries.
        """
        self.bu_directory = {}
        self.ty_directory = {}
