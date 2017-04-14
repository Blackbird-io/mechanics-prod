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
TaxoDir               Directory for Taxonomy units
====================  ==========================================================
"""





# Imports
import copy
import logging

import bb_settings
import bb_exceptions
import tools.for_tag_operations

from data_structures.system.bbid import ID
from data_structures.modelling.business_unit import BusinessUnit



# Constants
# n/a

# Globals
logger = logging.getLogger(bb_settings.LOGNAME_MAIN)

# Classes
class TaxoDir:
    """

    TaxoDir objects have a bu_directory and ty_directory designed for storing
    and searching for Taxonomy BusinessUnits. These directories will be
    separate from the directories in Model.

    ====================  =====================================================
    Attribute             Description
    ====================  =====================================================

    DATA:
    model                 instance of Model class
    bu_directory          dict; key = bbid, val = business units
    ty_directory          dict; key = strings, val = sets of bbids
    id                    instance of ID class

    FUNCTIONS:
    add()                 method for adding templates to taxonomy directories
    clear()               clears bu and ty directory
    get()                 method retrieves template with specified ID
    get_by_type()         method retrieves templates of specified type
    get_tagged()          return dict of units (by bbid) with specified tags
    register()            method registers template in taxonomy directory
    ====================  =====================================================
    """
    def __init__(self, model):
        self.model = model
        self.bu_directory = dict()
        self.ty_directory = dict()

        self.id = ID()
        self.id.set_namespace(model.id.bbid)
        self.id.assign(seed='taxonomy directory')

    @classmethod
    def from_portal(cls, portal_data, model, link_list):
        """


        TaxoDir.from_portal() -> TaxoDir

        --``portal_data`` is a dictionary containing serialized TaxoDir data
        --``model`` is the Model instance the new TaxoDir will be attached to

        Method deserializes TaxoDir into a rich object from flat portal data.
        """
        new = cls(model)

        temp_dir = dict()
        for unit in portal_data['taxonomy_units']:
            tmp = BusinessUnit.from_portal(unit, link_list)
            temp_dir[unit['bbid']] = tmp
            tmp._set_components()
            new.register(tmp)

        return new

    def to_portal(self):
        """


        TaxoDir.to_portal() -> dict

        Method flattens TaxoDir into a serialized dictionary.
        """
        data = dict()

        taxo_list = list()
        for unit in self.bu_directory.values():
            taxo_list.append(unit.to_portal())

        data['taxonomy_units'] = taxo_list

        return data

    def add(self, template, overwrite=False):
        """


        TaxoDir.add() -> TaxoDir

        --``template`` is an instance of BusinessUnit to be used as a
        template unit
        --``overwrite`` bool; whether to overwrite existing template with
        matching bbid

        Method registers new template in TaxoDir, which adds the template to
        instance directories.
        """
        self.register(template, update_id=True, overwrite=overwrite,
                      recur=True)

    def clear(self):
        """


        TaxoDir.clear() -> None

        Method resets instance directories.
        """
        self.bu_directory = dict()
        self.ty_directory = dict()

    def get(self, bbid):
        """


        TaxoDir.get() -> BusinessUnit

        --``bbid`` BBID of template to retrieve

        Return the template with specified bbid or None.
        """
        template = self.bu_directory.get(bbid, None)

        return template

    def get_by_type(self, type):
        """


        TaxoDir.get_by_type() -> dict

        --``type`` string; type of unit to retrieve

        Return a dictionary of units (by bbid) of the specified type.
        """
        ids = self.ty_directory.get(type, set())

        templates = dict()
        for bbid in ids:
            templates[bbid] = self.get(bbid)

        return templates

    def get_tagged(self, *tags, pool=None):
        """


        TaxoDir.get_tagged() -> dict

        --``tags`` list of tags to search for on templates

        Return a dictionary of units (by bbid) that carry the specified tags.
        Delegates all selection work to tools.for_tag_operations.get_tagged()
        """
        if not pool:
            pool = self.bu_directory.values()

        # We want a consistent order for the pool across run times
        pool = sorted(pool, key=lambda bu: bu.id.bbid)

        tagged_dict = tools.for_tag_operations.get_tagged(pool, *tags)

        return tagged_dict

    def refresh_ids(self):
        units = list(self.bu_directory.values())
        self.clear()

        for unit in units:
            self.bu_directory[unit.id.bbid] = unit
            type_set = self.ty_directory.setdefault(unit.type, set())
            type_set.add(unit.id.bbid)

    def register(self, bu, update_id=True, overwrite=False, recur=True):
        """


        TaxoDir.register() -> None

        --``bu`` is an instance of BusinessUnit

        Manually add unit to TaxoDir. Unit will appear in directories.
        If bu has child units, those units will automatically register
        Generally it is better to avoid having child units in taxonomy
        """
        if update_id:
            bu._update_id(namespace=self.id.bbid, recur=True)

        if not bu.id.bbid:
            c = "Cannot add content without a valid bbid."
            raise bb_exceptions.IDError(c)

        if not overwrite:
            # Check for collisions first, then register if none arise.
            if bu.id.bbid in self.bu_directory:
                c = (
                    "TaxoDir.bu_directory already contains an object with "
                    "the same bbid as this unit. \n"
                    "unit id:         {bbid}\n"
                    "known unit name: {name}\n"
                    "new unit name:   {new_name}\n\n"
                ).format(
                    bbid=self.id.bbid,
                    name=self.bu_directory[bu.id.bbid].tags.name,
                    new_name=bu.name,
                )
                raise bb_exceptions.IDCollisionError(c)

        # Register the unit.
        self.bu_directory[bu.id.bbid] = bu

        # Setdefault returns dict[key] if value exists, or sets dict[key]=set()
        brethren = self.ty_directory.setdefault(bu.type, set())
        brethren.add(bu.id.bbid)

        bu.relationships.set_model(self.model)

        if recur:
            for child_bu in bu.components.values():
                self.register(child_bu, update_id=update_id,
                              overwrite=overwrite, recur=recur)
