# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL

# Blackbird Environment
# Module: data_structures.modelling.snapshot
"""

Module defines Snapshot class
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
Snapshot              represents capital structure at a single point in time
====================  ==========================================================
"""



import bb_exceptions
from datetime import date
from data_structures.system.bbid import ID




class Snapshot:
    """

    The Snapshot class defines a what the capital structure looks at at a single
    point in time

    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    as_of_date            datetime.date
    created_date          datetime.date
    records               dict, key=(owner_name, round_name), value=Record()

    FUNCTIONS:
    add_record()          adds a record to self.records
    get_records_by_owner() returns list of records from a single owner
    get_records_by_round() returns list of records from a single round
    ====================  ======================================================
    """
    def __init__(self, as_of_date, created_date=None):
        self.as_of_date = as_of_date
        self.created_date = created_date or date.today()
        self.records = dict()

    def add_record(self, record, overwrite=False):
        """


        Snapshot.add_record() -> None

        --``record`` is an instance of record
        --``overwrite`` is False by default

        Method adds a dict entry with key=(owner_name, round_name), value=Record
        If overwrite is False, method checks that the record does not conflict
        with existing entries before adding the new record.
        """
        key = (record.owner_name, record.round_name)

        # Make sure this record is valid
        if not overwrite:
            if key in self.records:
                c = "Cannot overwrite existing record. (%s, %s) already" \
                    " exists in directory." % key
                raise bb_exceptions.BBAnalyticalError(c)

        self.records[key] = record

    def get_records_by_owner(self, owner_name):
        """


        Snapshot.get_records_by_owner() -> list of Records

        --``owner_name`` string

        Method returns a list of Records belonging to a single owner.
        """
        records_list = []
        
        for key in self.records:
            if key[0] == owner_name:
                records_list.append(self.records[key])
            
        return records_list
       
    def get_records_by_round(self, round_name):
        """


        Snapshot.get_records_by_round() -> list of Records

        --``owner_name`` string

        Method returns a list of Records belonging to a single round.
        """

        records_list = []
        for key in self.records:
            if key[1] == round_name:
                records_list.append(self.records[key])

        return records_list
