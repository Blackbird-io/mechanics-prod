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
from collections import OrderedDict
from tools.parsing import date_from_iso
from datetime import date
from data_structures.system.bbid import ID




class CapTable:
    """

    The CapTable class is a container for Rounds and Snapshots.

    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    rounds                OrderedDict, {round_name: Round()}
    snapshots             dict, {date: Snapshot()}

    FUNCTIONS:
    add_round()           adds a Round to self.rounds
    add_snapshot()        adds a Snapshot to self.snapshots
    get_last_snapshot()   returns most recent Snapshot
    ====================  ======================================================
    """
    def __init__(self):
        self.rounds = OrderedDict()
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
        key = new_snapshot.ref_date

        # Make sure this snapshot is valid
        if not overwrite:
            if key in self.snapshots:
                c = "Cannot overwrite existing snapshot. %s already" \
                    " exists in directory." % key
                raise bb_exceptions.BBAnalyticalError(c)

        self.snapshots[key] = new_snapshot

    def get_last_snapshot(self, ref_date=None):
        """


        CapTable.get_last_snapshot() -> Snapshot

        --``ref_date`` is datetime date, or string "YYYY-MM-DD"

        Method returns the most recent Snapshot on or before a certain date.
        Date defaults to today() if not specified
        """
        if not ref_date:
            ref_date = date.today()
        elif isinstance(ref_date, str):
            ref_date = date_from_iso(ref_date)

        last_key = None
        for key in self.snapshots:
            if key <= ref_date:
                if not last_key:
                    last_key = key
                elif key > last_key:
                    last_key = key

        if last_key:
            return self.snapshots[last_key]
        else:
            return None
            # c = "No Snapshots exist before %s" % date
            # raise bb_exceptions.BBAnalyticalError(c)

