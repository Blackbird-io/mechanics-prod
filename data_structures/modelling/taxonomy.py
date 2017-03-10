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




# Constants
# n/a

# Globals
# n/a

# Classes
class Taxonomy(dict):
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
    def __init__(self, taxo_dir):
        dict.__init__(self)
        self.taxo_dir = taxo_dir

    def __setitem__(self, key, value):
        if isinstance(value, dict):
            if not isinstance(value, Taxonomy):
                value = Taxonomy(self.taxo_dir)
            dict.__setitem__(self, key, value)
        else:
            self.taxo_dir.add(value)
            dict.__setitem__(self, key, value)

    @classmethod
    def from_portal(cls, portal_data, taxo_dir):
        """


        Taxonomy.from_portal() -> TaxoDir

        --``portal_data`` is a dictionary containing serialized TaxoDir data
        --``model`` is the Model instance the new TaxoDir will be attached to

        Method deserializes TaxoDir into a rich object from flat portal data.
        """
        new = cls(taxo_dir)

        for taxo_unit in portal_data:
            key_list = taxo_unit.pop('keys')
            temp = new
            for k in key_list:
                this_dict = temp
                if k in this_dict:
                    temp = dict.__getitem__(this_dict, k)
                else:
                    dict.__setitem__(this_dict, k, cls(taxo_dir))
                    temp = dict.__getitem__(this_dict, k)

            bu = new.taxo_dir.get(taxo_unit['bbid'])
            dict.__setitem__(this_dict, k, bu)

        return new

    def to_portal(self):
        """


        Taxonomy.to_portal() -> list

        Method flattens TaxoDir into a serialized dictionary.
        """
        def get_taxo_rows(r, v, rl):
            if isinstance(v, Taxonomy):
                for k, val in v.items():
                    new_r = copy.deepcopy(r)
                    new_r['keys'].append(k)
                    get_taxo_rows(new_r, val, rl)
            else:
                r.update({"bbid": v.id.bbid})
                rl.append(r)         
        
        row_list = list()
        for key, value in self.items():
            row = dict()
            row['keys'] = [key]
            get_taxo_rows(row, value, row_list)

        return row_list
