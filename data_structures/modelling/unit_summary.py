# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL

# Blackbird Environment
# Module: data_structures.modelling.unit_summary
"""

Module defines BusinessUnit class.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
UnitSummary           structured summary of a business and its components
====================  ==========================================================
"""




# Imports
import bb_exceptions

from data_structures.serializers.chef import data_management as xl_mgmt
from data_structures.system.bbid import ID
from data_structures.system.relationships import Relationships
from data_structures.system.tags_mixin import TagsMixIn

from .summary_components import SummaryComponents
from .financials import Financials
from .history_line import HistoryLine




# Constants
# n/a

# Globals
# n/a

# Classes
class UnitSummary(HistoryLine, TagsMixIn):
    """

    Object is primarily a storage container for financial summary and business
    structure.
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    components            instance of SummaryComponents class
    financials            instance of Financials object
    id                    instance of ID object
    period                pointer to PeriodSummary object
    relationships         instance of Relationships class
    xl                    instance of UnitData class

    FUNCTIONS:
    add_component()       adds UnitSummary to instance components
    set_financials()      sets instance financials attribute
    ====================  ======================================================
    """

    def __init__(self, name, fins=None):

        HistoryLine.__init__(self)
        TagsMixIn.__init__(self, name)

        self._type = None

        self.components = None
        self._set_components()

        self.set_financials(fins)
        self.complete = False

        self.id = ID()
        # Get the id functionality but do NOT assign a bbid yet

        self.period = None
        self.relationships = Relationships(self)
        self.xl = xl_mgmt.UnitData()

    def __str__(self, lines=None):
        """


        UnitSummary.__str__() -> str


        Method concatenates each line in ``lines``, adds a new-line character at
        the end, and returns a string ready for printing. If ``lines`` is None,
        method calls _get_pretty_lines() on instance.
        """
        # Get string list, slap a new-line at the end of every line and return
        # a string with all the lines joined together.
        if not lines:
            lines = self._get_pretty_lines()

        # Add empty strings for header and footer padding
        lines.insert(0, "")
        lines.append("")

        box = "\n".join(lines)
        return box

    def add_component(self, bu, update_id=True, register_in_period=True,
                      overwrite=False):
        """


        UnitSummary.add_component() -> None

        --``bu``
        --``update_id``
        --``register_in_period``
        --``overwrite``

        Method prepares a bu and adds it to instance components.

        Method always sets bu namespace_id to instance's own namespace_id. If
        ``updateID`` is True, method then assigns a new bbid to the instance.

        Method raises IDNamespaceError if the bu's bbid falls outside the
        instance's namespace id. This is most likely if updateID is False and
        the bu retains an old bbid from a different namespace (e.g., when
        someone inserts a business unit from one model into another without
        updating the business unit's bbid).

        If register_in_period is true, method raises IDCollisionError if the
        period's directory already contains the new business unit's bbid.

        If all id verification steps go smoothly, method delegates insertion
        down to SummaryComponents.add_item().
        """

        # optionally update ids.
        if update_id:
            bu._update_id(namespace=self.id.bbid, recur=True)

        # register the unit, will raise errors on collisions
        if register_in_period:
            bu._register_in_period(recur=True, overwrite=overwrite)
        self.components.add_item(bu)

    def set_financials(self, fins=None):
        """


        UnitSummary.set_financials() -> None


        Method for initializing instance.financials with a properly configured
        Financials object.

        Method will set instance financials to ``fins``, if caller specifies
        ``fins``. Otherwise, method will set financials to a new Financials
        instance.
        """
        if fins is None:
            fins = Financials()

        self.financials = fins

    # *************************************************************************#
    #                          NON-PUBLIC METHODS                              #
    # *************************************************************************#
    def _build_directory(self, recur=True, overwrite=True):
        """


        UnitSummary._build_directory() -> (id_directory, ty_directory)


        Register yourself and optionally your components, by type and by id
        return id_directory, ty_directory
        """

        # return a dict of bbid:unit
        id_directory = dict()
        if recur:
            for unit in self.components.values():
                lower_level = unit._build_directory(recur=True,
                                                    overwrite=overwrite)
                lower_ids = lower_level[0]
                id_directory.update(lower_ids)

            # update the directory for each unit in self
            pass
        if self.id.bbid in id_directory:
            if not overwrite:
                c = "Can not overwrite existing bbid"
                raise bb_exceptions.BBAnalyticalError(c)

        id_directory[self.id.bbid] = self

        return id_directory

    def _get_pretty_lines(self,
                          top_element="=",
                          side_element="|",
                          box_width=23,
                          field_width=5):
        """


        UnitSummary._get_pretty_lines() -> list


        Method returns a list of strings that displays a box if printed in
        order. Line ends are naked (i.e, lines do **not** terminate in a
        new-line character).

        Box format:

        +=====================+
        | NAME  : Baltimore-4 |
        | ID    : ...x65-0b78 |
        | COMPS :          45 |
        +=====================+

        """
        reg_corner = "+"
        # formatting rules
        template = "%s %s : %s %s"
        empty_line = template % (side_element,
                                 ("x" * field_width),
                                 "",
                                 side_element)
        # empty_line should equal " | xxxxxxxx :  |"
        data_width = box_width - len(empty_line)

        # fields:
        fields = ["NAME",
                  "ID",
                  "COMPS"]
        # data
        data = {}
        unit_name = str(self.tags.name)
        if len(unit_name) > data_width:
            # abbreviate unit name if its too long
            unit_name_parts = unit_name.split()
            if len(unit_name_parts) > 1:
                last_part = unit_name_parts[-1]
                initials = ""
                for part in unit_name_parts[:-1]:
                    initial = part[:1] + "."
                    initials = initials + initial
                unit_name = initials + last_part
        data["NAME"] = unit_name[:data_width]

        id_dots = "..."
        tail_width = data_width - len(id_dots)
        id_tail = str(self.id.bbid)[(tail_width * -1):]
        data["ID"] = id_dots + id_tail

        data["COMPS"] = str(len(self.components.get_all()))

        lines = []
        top_border = reg_corner + top_element * (box_width - 2) + reg_corner
        lines.append(top_border)

        for field in fields:
            new_line = template % (side_element,
                                   field.ljust(field_width),
                                   data[field].rjust(data_width),
                                   side_element)
            lines.append(new_line)

        # add a bottom border symmetrical to the top
        lines.append(top_border)

        return lines

    def _register_in_period(self, period, recur=True, overwrite=True):
        """


        UnitSummary._register_in_period() -> None


        Method updates the bu_directory on the instance period with the contents
        of instance.components (bbid:bu). If ``recur`` == True, repeats for
        every component in instance.

        If ``overwrite`` == False, method will raise an error if any of its
        component bbids is already in the period's bu_directory at the time of
        call.

        NOTE: Method will raise an error only if the calling instance's own
        components have ids that overlap with the bu_directory. To the extent
        any of the caller's children have an overlap, the error will appear only
        when the recursion gets to them. As a result, by the time the error
        occurs, some higher-level or sibling components may have already updated
        the period's directory.
        """
        self.period = period

        if not overwrite:
            if self.id.bbid in self.period.bu_directory:
                c1 = "TimePeriod.bu_directory already contains an object with "
                c2 = "the same bbid as this unit. \n"
                c3 = "unit id:         %s\n" % self.id.bbid
                c4 = "known unit name: %s\n"
                c4 = c4 % self.period.bu_directory[self.id.bbid].tags.name
                c5 = "new unit name:   %s\n\n" % self.tags.name
                print(self.period.bu_directory)
                c = c1 + c2 + c3 + c4 + c5
                raise bb_exceptions.IDCollisionError(c)

        # Check for collisions first, then register if none arise.
        self.period.bu_directory[self.id.bbid] = self

        if recur:
            for unit in self.components.values():
                unit._register_in_period(period, recur, overwrite)

    def _set_components(self, comps=None):
        """


        UnitSummary._set_components() -> None


        Method sets instance.components to the specified object, sets object to
        point to instance as its parent. If ``comps`` is None, method generates
        a clean instance of Components().
        """
        if not comps:
            comps = SummaryComponents()
        comps.relationships.set_parent(self)
        self.components = comps

    def _update_id(self, namespace, recur=True):
        """


        UnitSummary._update_id() -> None


        Assigns instance a new id in the namespace, based on the instance name.
        If ``recur`` == True, updates ids for all components in the parent
        instance bbid namespace.
        """
        self.id.set_namespace(namespace)
        self.id.assign(self.tags.name)
        # This unit now has an id in the namespace. Now pass our bbid down as
        # the namespace for all downstream components.
        if recur:
            for unit in self.components.values():
                unit._update_id(namespace=self.id.bbid, recur=True)
