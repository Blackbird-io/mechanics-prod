# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL

# Blackbird Environment
# Module: data_structures.modelling.business_unit_base
"""

Module defines BusinessUnitBase class.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
BusinessUnitBase      basic structure to hold business information
====================  ==========================================================
"""




# Imports
import copy
import logging

import bb_settings
import bb_exceptions
import tools.for_printing as views

from data_structures.serializers.chef import data_management as xl_mgmt
from data_structures.system.bbid import ID
from data_structures.system.relationships import Relationships
from data_structures.system.tags_mixin import TagsMixIn

from .dr_container import DrContainer
from .financials import Financials
from .components_base import ComponentsBase




# Constants
# n/a

# Globals
logger = logging.getLogger(bb_settings.LOGNAME_MAIN)


# Classes
class BusinessUnitBase(TagsMixIn):
    """

    Object is primarily a storage container for financial summary and business
    structure.
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    complete              bool; if financials are complete for unit in period
    components            instance of SummaryComponents class
    financials            instance of Financials object
    id                    instance of ID object
    period                pointer to PeriodSummary object
    periods_used          int; number of periods used for values in financials
    relationships         instance of Relationships class
    xl                    instance of UnitData class

    FUNCTIONS:
    set_financials()      sets instance financials attribute
    ====================  ======================================================
    """

    def __init__(self, name, fins=None, model=None):

        TagsMixIn.__init__(self, name)

        self.components = None
        self._set_components()

        self.drivers = None
        self._set_drivers()

        self.financials = None
        self.set_financials(fins)
        self.complete = False

        self.id = ID()
        # Get the id functionality but do NOT assign a bbid yet

        # self.period = None
        self.relationships = Relationships(self, model=model)
        self.periods_used = 0
        self.xl = xl_mgmt.UnitData()

    def copy(self):
        """


        BU.copy() -> BU


        Method returns a new business unit that is a deep-ish copy of the
        instance.

        The new bu starts out as a shallow Tags.copy() copy of the instance.
        The method then sets the following attributes on the new bu to either
        deep or class-specific copies of the instance values:

        - components
        - drivers
        - financials
        - id (vanilla shallow copy)

        The class-specific copy methods for components, drivers, and financials
        all return deep copies of the object and its contents. See their
        respective class documenation for mode detail.
        """
        result = copy.copy(self)
        result.tags = self.tags.copy()
        result.relationships = self.relationships.copy()
        # Start with a basic shallow copy, then add tags
        #
        r_comps = self.components.copy()
        result._set_components(r_comps)

        r_drivers = self.drivers.copy()
        result._set_drivers(r_drivers)

        r_fins = self.financials.copy()
        result.set_financials(r_fins)

        result.id = copy.copy(self.id)

        return result

    def __str__(self, lines=None):
        """


        BusinessUnitBase.__str__() -> str


        Method concatenates each line in ``lines``, adds a new-line character at
        the end, and returns a string ready for printing. If ``lines`` is None,
        method calls views.view_as_unit() on instance.
        """
        # Get string list, slap a new-line at the end of every line and return
        # a string with all the lines joined together.
        if not lines:
            lines = views.view_as_base(self)

        # Add empty strings for header and footer padding
        lines.insert(0, "")
        lines.append("")

        box = "\n".join(lines)
        return box

    def set_financials(self, fins=None):
        """


        BusinessUnitBase.set_financials() -> None


        Method for initializing instance.financials with a properly configured
        Financials object.

        Method will set instance financials to ``fins``, if caller specifies
        ``fins``. Otherwise, method will set financials to a new Financials
        instance.
        """
        if fins is None:
            fins = Financials(parent=self)

        fins.relationships.set_parent(self)
        self.financials = fins

    def get_financials(self, period=None):
        """


        BusinessUnitBase.get_financials() -> Financials()

        --``period`` TimePeriod

        Returns this BUs financials in a given period.
        """
        model = self.relationships.model
        now = model.get_timeline().current_period if model else None

        if not period:
            # method allows a call with a blank period
            # in which case bu must have financials attached
            fins = self.financials
        elif self.id.bbid in period.financials:
            # the best case we expect: financials have been assigned to a period
            fins = period.financials[self.id.bbid]
        elif period is now:
            # fallback if financials are not on period
            # financials are assigned to bu before period is
            fins = self.financials
            period.financials[self.id.bbid] = fins
        else:
            fins = self.financials.copy(clean=True)
            fins.relationships.set_parent(self)
            fins.period = period
            period.financials[self.id.bbid] = fins

        return fins

    def get_current_period(self):
        """


        BusinessUnitBase.get_current_period() -> TimePeriodBase

        Convenience method to get current_period from parent model's
        default timeline.
        """
        model = self.relationships.model
        if model:
            return model.get_timeline().current_period

    # *************************************************************************#
    #                          NON-PUBLIC METHODS                              #
    # *************************************************************************#

    def _derive_line(self, line, period=None):
        """


        BusinessUnitBase.derive_line() -> None

        --``line`` is the LineItem to work on

        Method computes the value of a line using drivers stored on the
        instance.  Method builds a queue of applicable drivers for the provided
        LineItem. Method then runs the drivers in the queue sequentially. Each
        LineItem gets a unique queue.

        Method will not derive any lines that are hardcoded or have already
        been consolidated (LineItem.hardcoded == True or
        LineItem.has_been_consolidated == True).
        """

        # Repeat for any details
        if line._details:
            for detail in line.get_ordered():
                if detail.replica:
                    continue
                    # Skip replicas to make sure we apply the driver only once
                    # A replica should never have any details
                else:
                    self._derive_line(detail, period)

        # look for drivers based on line name, line parent name, all line tags
        keys = [line.tags.name]
        keys.append(line.relationships.parent.name.casefold())
        keys.extend(line.tags.all)

        for key in keys:
            if key in self.drivers:
                matching_drivers = self.drivers.get_drivers(key)
                for driver in matching_drivers:
                    driver.workOnThis(line, bu=self, period=period)

    def _set_components(self, comps=None):
        """


        BusinessUnitBase._set_components() -> None


        Method sets instance.components to the specified object, sets object to
        point to instance as its parent. If ``comps`` is None, method generates
        a clean instance of Components().
        """
        if not comps:
            comps = ComponentsBase()
        comps.relationships.set_parent(self)
        self.components = comps

    def _set_drivers(self, dr_c=None):
        """


        BusinessUnitBase._set_drivers() -> None


        Method for initializing instance.drivers with a properly configured
        DrContainer object. Method sets instance as the parentObject for
        DrContainer and any drivers in DrContainer.
        """
        if not dr_c:
            dr_c = DrContainer()
        dr_c.setPartOf(self, recur=True)
        self.drivers = dr_c

    def _update_id(self, namespace, recur=True):
        """


        BusinessUnitBase._update_id() -> None


        Assigns instance a new id in the namespace, based on the instance name.
        If ``recur`` == True, updates ids for all components in the parent
        instance bbid namespace.
        """
        self.id.set_namespace(namespace)
        self.id.assign(self.tags.name)
        self.financials.register(namespace=namespace)
        # This unit now has an id in the namespace. Now pass our bbid down as
        # the namespace for all downstream components.

        if recur:
            for unit in self.components.values():
                unit._update_id(namespace=self.id.bbid, recur=True)
