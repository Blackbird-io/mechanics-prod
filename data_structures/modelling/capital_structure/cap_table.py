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
    get_ownership_summary()  returns a Portal schema to display Ownership Table
    get_rounds_summary()     returns a Portal schema to display Rounds Table
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

    def get_ownership_summary(self):
        """


        CapTable.get_ownership_summary() -> dict, schema below

        {
            "type" : "debt",
            "rows" : [
                {"shareholder":"Series B Preferred",
                 "shares":3500,
                 "investment":1000,
                 "ownership":0.350},
                {"shareholder":"Series A Preferred",
                 "shares":1900,
                 "investment":2000,
                 "ownership":0.190},
                {"shareholder":"Common Equity",
                 "shares":1700,
                 "investment":3000,
                 "ownership":0.170}                 ],
            "total" :  {"shares":7100, "investment":6000, "ownership":1.0}
        }

        Method returns information for the Ownership Table to be displayed in
        the portal.
        """
        result = dict()
        result["type"] = "equity"
        result["rows"] = []
        result['total'] = dict()

        snapshot = self.get_last_snapshot()

        # Get a unique list of owners and total outstanding shares
        owner_list = []
        total_shares = 0
        total_investment = 0
        total_ownership = 0
        for key in snapshot.records:
            # key is (owner_name, round_name)
            owner_name = key[0]
            if owner_name not in owner_list:
                owner_list.append(owner_name)

            record = snapshot.records[key]
            total_shares += record.units or 0
            total_investment += record.cash or 0

        # Create entries in result["rows"]
        for owner_name in owner_list:
            records_list = snapshot.get_records_by_owner(owner_name)

            owner_units = 0
            owner_cash = 0

            for record in records_list:
                owner_units += record.units
                owner_cash += record.cash

            new_row = dict()
            new_row["shareholder"] = owner_name
            new_row["shares"] = owner_units
            new_row["investment"] = owner_cash
            new_row["ownership"] = owner_units/total_shares
            result['rows'].append(new_row)

            total_ownership += new_row["ownership"]

        result['total']['shares'] = total_shares
        result['total']['investment'] = total_investment
        result['total']['ownership'] = total_ownership

        return result

    def get_rounds_summary(self):
        """


        CapTable.get_rounds_summary() -> dict, schema below

        {
            "rounds" : [
                {
                    "round": "Series A Preferred",
                    "date": "2010-01-01",
                    "investment": 1000,
                    "participants": "Ares Capital",
                    "participant_summary": [
                        {"participant":"Accel", "investment":1000},
                        {"participant":"JPM", "investment":1000},
                        {"participant":"Total", "investment":3000}
                        ]
                    "detail_summary": [
                        {"item": "Pre-Money Valuation", "value": "1000"},
                        {"item": "Post-Money Valuation", "value": "10.0"},
                        {"item": "Participation", "value":"1x"},
                        ]
                },
                {
                    "round": "Series B Preferred",
                    "date": "2010-01-01",
                    "investment": 1000,
                    "participants": "Ares Capital",
                    "participant_summary": [
                         {"participant":"Accel", "investment":1000},
                         {"participant":"JPM", "investment":1000},
                         {"participant":"Total", "investment":3000}
                        ]
                    "detail_summary": [
                        {"item": "Pre-Money Valuation", "value": "1000"},
                        {"item": "Post-Money Valuation", "value": "10.0"},
                        {"item": "Participation", "value":"1x"},
                        ]
                },
            ],
            "rounds_total": {"investment": 3000},
        }
        
        Method returns information for the Rounds Table to be displayed in
        the portal.
        """

        snapshot = self.get_last_snapshot()
        
        result = dict()
        result['rounds'] = list()
        result['rounds_total'] = dict()

        total_investment = 0
        for round_name in self.rounds:

            records_list = snapshot.get_records_by_round(round_name)

            round_units = 0
            round_cash = 0
            owners_list = []
            participant_summary = []
            detail_summary = []

            round = self.rounds[round_name]
            if round.valuation:
                pre_money_val = round.valuation - round.size
            else:
                pre_money_val = None
            detail_summary.append({"item": "Pre-Money Valuation",
                                   "value": pre_money_val})
            detail_summary.append({"item": "Post-Money Valuation",
                                   "value": round.valuation})
            # detail_summary.append({"item": "Participation",
            #                        "value": "%.1fx" % round.participation})
            detail_summary.append({"item": "Preference",
                                   "value": "%.1fx" % round.preference})

            for record in records_list:
                round_units += record.units
                round_cash += record.cash
                if record.owner_name not in owners_list:
                    owners_list.append(record.owner_name)
                    participant_dict = dict()
                    participant_dict["participant"] = record.owner_name
                    participant_dict["investment"] = record.cash
                    participant_summary.append(participant_dict)

            new_round_dict = dict()
            new_round_dict['round'] = round_name
            new_round_dict["date"] = None
            new_round_dict["investment"] = round_cash
            new_round_dict["participants"] = owners_list
            new_round_dict["participant_summary"] = participant_summary
            new_round_dict["detail_summary"] = detail_summary

            result['rounds'].append(new_round_dict)

            total_investment += round_cash

        result['rounds_total'] = {"investment": total_investment}

        return result
