# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL
# Blackbird Environment
# Module: data_structures.modelling.parameters
"""

Module defines dict-type storage container for parameters.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
Parameters            dictionary with overwrite controls
====================  ==========================================================
"""




# Imports
from pydoc import locate

import bb_exceptions




# Constants
# n/a

# Classes
class Parameters(dict):
    """

    Dictionary-type container that monitors whether keys overwrite existing
    data on add() calls.
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    n/a

    FUNCTIONS:
    add()                 add data, throw exception for overlap with known keys
    copy()                copy the instance and return the copy
    ====================  ======================================================
    """
    def __init__(self):
        dict.__init__(self)

    def add(self, new_data, overwrite=False):
        """


        Parameters.add() -> None


        Add new_data to instance. If overwrite is False, throw [ ] if new_data
        contains keys that already exist in instance.
        """
        if not overwrite:
            existing = new_data.keys() & self.keys()
            if existing:
                c = (
                    "New params overlap with existing keys. "
                    "Implicit overwrite prohibited:\n{}"
                ).format(sorted(existing))
                raise bb_exceptions.DefinitionError(existing, c)
        self.update(new_data)

    def copy(self):
        """


        Parameters.copy() -> obj

        Function returns a copy of the instance.
        """
        dict_copy = dict.copy(self)
        result = Parameters()
        result.update(dict_copy)

        return result

    @classmethod
    def from_portal(cls, portal_data, target=None):
        """

        Parameters.from_portal(portal_data) -> Parameters

        --``target`` if given, will filter the rows based on 'target' field

        **CLASS METHOD**

        Method extracts Parameters from portal_data.
        """
        result = cls()
        for data in portal_data:
            if target and data.get('target') and data['target'] != target:
                continue
            keyhold = result
            keypath = data['key_path'].split('\n')
            while keypath:
                k = keypath.pop(0)
                if keypath:
                    keyhold = keyhold.setdefault(k, cls())
                else:
                    # cast value to the stored type
                    keyhold[k] = locate(data['value_type'])(data['value'])
        return result

    def to_portal(self, key_path=None):
        """

        TimeLine.to_portal() -> dict

        Method yields a serialized representation of self.
        """
        for k, v in self.items():
            path = '{}\n{}'.format(key_path, k) if key_path else format(k)
            if isinstance(v, dict):
                yield from v.to_portal(key_path=path)
            else:
                data = dict(
                    key_path=path,
                    value=v,
                    value_type=type(v).__name__,
                )
                yield data
