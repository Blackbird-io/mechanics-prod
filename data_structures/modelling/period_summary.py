# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL
# Blackbird Environment
# Module: data_structures.modelling.period_summary
"""

Module defines PeriodSummary class.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
TimePeriod            a snapshot of data over a period of time.
====================  ==========================================================
"""

# Imports
import bb_exceptions
import bb_settings

from data_structures.system.bbid import ID
from data_structures.system.relationships import Relationships

from .history import History


# Constants
# n/a

# Classes
class PeriodSummary(History):
    """

    PeriodSummary objects represent periods of time and store a snapshot of some
    data during that period in their ``content`` attribute.

    Class represents an interval that includes its endpoints: [start, end].

    If one thinks of a TimeLine as a clothesrack, TimePeriods are individual
    hangers. This structure enables Blackbird to track the evolution of the data
    over real-world wall/calendar) time.

    The data in ``content`` is usually a top-level business unit. TimePeriod
    provides a reference table ``bu_directory`` for objects that the data
    contains. The bu_directory tracks objects by their bbid. Only one object
    with a given bbid should exist within a PeriodSummary. bbid collisions within
    a time period represent the time-traveller's paradox.

    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    bu_directory          dict; all business units in this period, keyed by bbid
    content               pointer to content, usually a business unit
    end                   datetime.date; last date in period
    id                    instance of ID class
    length                float; seconds between start and end
    relationships         instance of Relationships class
    start                 datetime.date; first date in period.

    FUNCTIONS:
    __str__               basic print, shows starts, ends, and content
    get_units()           return list of units from bbid pool
    register()            conform and register unit
    set_content()         attach company to period
    ====================  ======================================================
    """

    def __init__(self, start_date, end_date, content=None):
        History.__init__(self, recursive_attribute="content")

        self.start = start_date
        self.end = end_date

        self.bu_directory = dict()

        self.content = content
        self.id = ID()
        self.relationships = Relationships(self)

    def __str__(self):
        dots = "*" * bb_settings.SCREEN_WIDTH
        s = "\t starts:  \t%s\n" % self.start.isoformat()
        e = "\t ends:    \t%s\n" % self.end.isoformat()
        c = "\t content: \t%s\n" % self.content
        result = dots + "\n" + s + e + c + dots + "\n"
        return result

    def get_units(self, pool):
        """


        PeriodSummary.get_units() -> list


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

    def register(self, bu, updateID=True, reset_directories=False):
        """


        PeriodSummary.register() -> None


        Manually add unit to period. Unit will conform to period and appear
        in directories. Use sparingly: designed for master (taxonomy) period.

        NOTE: Period content should generally have a tree structure, with a
        single bu node on top. That node will manage all child relationships.
        Accordingly, the best way to add units to a period is to run
        bu.add_component(new_unit).

        If ``updateID`` is True, method will assign unit a new id in the
        period's namespace. Parameter should be False when moving units
        between scenarios.

        If ``reset_directories`` is True, method will clear existing type
        and id directories. Parameter should be True when registering the
        top (company) node of a structure.
        """

        if updateID:
            bu._update_id(self.id.namespace, recur=True)
        if not bu.id.bbid:
            c = "Cannot add content without a valid bbid."
            raise bb_exceptions.IDError(c)
        # Make sure unit has an id in the right namespace.

        if reset_directories:
            self._reset_directories()
        bu._register_in_period(recur=True, overwrite=False)
        # Register the unit.

    def set_content(self, bu, updateID=True):
        """


        PeriodSummary.set_content() -> None


        Register bu and set instance.content to point to it.

        NOTE: ``updateID`` should only be True when adding external content to
        a model for the first time (as opposed to moving content from period to
        period or level to level within a model).

        PeriodSummary's in a Model all share the model's namespace_id.
        Accordingly, a UnitSummary will have the same bbid in all time periods.
        The UnitSummary can elect to get a different bbid if it's name changes,
        but in such an event, the Model will treat it as a new unit altogether.
        """
        self.register(bu, updateID=updateID, reset_directories=True)
        # Reset directories when setting the top node in the period.
        self.content = bu

    # *************************************************************************#
    #                          NON-PUBLIC METHODS                             #
    # *************************************************************************#

    def _reset_directories(self):
        """


        PeriodSummary.reset_directories() -> None


        Method sets instance.bu_directory and instance.ty_directory to blank
        dictionaries.
        """
        self.bu_directory = dict()
