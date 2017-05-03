# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2017
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL
# Blackbird Environment
# Module: data_structures.modelling.line_item_usage
"""

Module defines the LineItemUsage class, which holds information that helps
the Engine decide how to treat the LineItem it is attached to.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
LineItemUsage         simple class containing behavior information for LineItems
====================  ==========================================================
"""




# Imports
# N/A



# Constants
# N/A

# Classes
class LineItemUsage:
    """

    A LineItemUsage is a data structure that holds information that helps
    the Engine decide how to treat the LineItem it is attached to.
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    status_rules          dict;
    alert_commentary      dict;
    behavior              dict;
    monitor               bool; 

    FUNCTIONS:
    copy()                returns a new line w copies of key attributes
    to_database()         creates a flattened version of LineItem for Portal

    CLASS METHODS:
    from_database()       class method, extracts LineItem out of API-format
    ====================  ======================================================
    """
    def __init__(self):
        self.status_rules = dict()
        self.alert_commentary = dict()
        self.behavior = dict()
        self.monitor = False
    
    @classmethod
    def from_database(cls, data):
        new = cls()
        
        status_rules = data.get('status_rules', None)
        if status_rules:
            new.status_rules.update(status_rules)

        alert_commentary = data.get('alert_commentary', None)
        if alert_commentary:
            new.alert_commentary.update(alert_commentary)

        behavior = data.get('behavior', None)
        if behavior:
            new.behavior.update(behavior)

        monitor = data.get('monitor', False)
        new.monitor = monitor

        return new

    def to_database(self):
        data = dict()

        data['status_rules'] = self.status_rules
        data['alert_commentary'] = self.alert_commentary
        data['behavior'] = self.behavior
        data['monitor'] = self.monitor

        return data

    def copy(self):
        result = LineItemUsage()
        result.status_rules = self.status_rules.copy()
        result.alert_commentary = self.alert_commentary.copy()
        result.behavior = self.behavior.copy()
        result.monitor = self.monitor

        return result
