# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL
# Blackbird Environment
# Module: data_structures.modelling.taxo_dir
"""

Module defines TaxoDir class.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
TaxoDir               Directory for Taxonomy units. Stored on Model.master
====================  ==========================================================
"""





# Imports
import copy
import logging

import bb_settings
import bb_exceptions
import tools.for_tag_operations

from data_structures.system.tags_mixin import TagsMixIn
from data_structures.system.bbid import ID



# Constants
# n/a

# Globals
logger = logging.getLogger(bb_settings.LOGNAME_MAIN)

# Classes
class TaxoDir(TagsMixIn):
    """

    TaxoDir objects have a bu_directory and ty_directory designed for storing
    and searching for Taxonomy BusinessUnits. These directories will be separate
    from the directories in Model. Each Taxonomy BU will have its own financials

    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    bu_directory          dict; key = bbid, val = business units
    ty_directory          dict; key = strings, val = sets of bbids
    id                    instance of ID class

    FUNCTIONS:
    clear()               clears bu and ty directory
    get_units()           return list of units from bbid pool
    get_lowest_units()    return list of units w/o components from bbid pool
    get_tagged_units()    return dict of units (by bbid) with specified tags
    ====================  ======================================================
    """
    def __init__(self, model=None):
        # content is handled differently, is not passed on to base init
        TagsMixIn.__init__(self)

        self.model = model
        self.ty_directory = dict()
        self.bu_directory = dict()
        self.financials = dict()
        self.id = ID()
        self.id.set_namespace(model.id.bbid)
        self.id.assign(seed='taxonomy directory')

    def clear(self):
        """


        TaxoDir.clear() -> None


        Method sets financials to empty dict and resets instance directories.
        """
        self.bu_directory = {}
        self.ty_directory = {}

    def get_units(self, pool):
        """


        TaxoDir.get_units() -> list


        Method returns a list of objects from self.bu_directory that
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


        TaxoDir.get_lowest_units() -> list


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

    def get_tagged_units(self, *tags, pool=None):
        """


        TaxoDir.get_tagged_units() -> dict


        Return a dictionary of units (by bbid) that carry the specified tags.

        If ``pool`` is None, uses bu_directory.
        Delegates all selection work to tools.for_tag_operations.get_tagged()
        """
        if not pool:
            pool = self.bu_directory.values()
            # We want a consistent order for the pool across run times
            pool = sorted(pool, key=lambda bu: bu.id.bbid)

        tagged_dict = tools.for_tag_operations.get_tagged(pool, *tags)

        return tagged_dict

    def register(self, bu, update_id=True):
        """


        TaxoDir.register() -> None

        --``bu`` is an instance of BusinessUnit or BusinessUnitBase

        Manually add unit to TaxoDir. Unit will appear in directories.
        If bu has child units, those units will NOT automatically register
        """
        if update_id:
            bu._update_id(namespace=self.id.bbid, recur=True)

        if not bu.id.bbid:
            c = "Cannot add content without a valid bbid."
            raise bb_exceptions.IDError(c)
        # Make sure unit has an id in the right namespace.

        bu.relationships.set_model(self.model)

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
                name=self.bu_directory[bu.id.bbid].tags.name,
                mine=self.tags.name,
            )
            print(self.bu_directory)
            raise bb_exceptions.IDCollisionError(c)

        # Register the unit.
        self.bu_directory[bu.id.bbid] = bu

        brethren = self.ty_directory.setdefault(bu.type, set())
        # Setdefault returns dict[key] if value exists, or sets dict[key]=set()
        brethren.add(bu.id.bbid)

        # Do NOT automatically register child units. May cause conflicts
        # for child_bu in bu.components.values():
        #     self.register(child_bu, update_id=True, reset_directories=False)
