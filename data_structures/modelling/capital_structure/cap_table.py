# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL

# Blackbird Environment
# Module: data_structures.modelling.cap_table
"""

Module defines CapTable class
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
CapTable              storage for capital structure information
====================  ==========================================================
"""



import bb_exceptions
from datetime import date
from data_structures.system.bbid import ID




class CapTable:
    """

    The CapTable class is a container for Rounds and Snapshots.

    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    rounds                dict, {round_name: Round()}
    snapshots             dict, {date: Snapshot()}

    FUNCTIONS:
    add_round()           adds a Round to self.rounds
    add_snapshot()        adds a Snapshot to self.snapshots
    ====================  ======================================================
    """
    def __init__(self):
        self.rounds = dict()
        self.snapshots = dict()

    def add_round(self, new_round, overwrite=False):
        """


        CapTable.add_record() -> None

        --``new_round`` is an instance of Round
        --``overwrite`` is False by default

        Method adds a dict entry with key=round_name, value=Round
        If overwrite is False, method checks that the record does not conflict
        with existing entries before adding the new Round.
        """
        key = new_round.name

        # Make sure this round is valid
        if not overwrite:
            if key in self.rounds:
                c = "Cannot overwrite existing round. %s already" \
                    " exists in directory." % key
                raise bb_exceptions.BBAnalyticalError(c)

        self.rounds[key] = new_round

    def add_snapshot(self, new_snapshot, overwrite=False):
        """


        CapTable.add_snapshot() -> None

        --``new_snapshot`` is an instance of Snapshot
        --``overwrite`` is False by default

        Method adds a dict entry with key=snapshot_date, value=Snapshot
        If overwrite is False, method checks that the snapshot does not conflict
        with existing entries before adding the new Snapshot.
        """
        key = new_snapshot.as_of_date

        # Make sure this snapshot is valid
        if not overwrite:
            if key in self.snapshots:
                c = "Cannot overwrite existing snapshot. %s already" \
                    " exists in directory." % key
                raise bb_exceptions.BBAnalyticalError(c)

        self.snapshots[key] = new_snapshot

