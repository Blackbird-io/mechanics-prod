# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL

# Blackbird Environment
# Module: data_structures.system.tags
"""

Module defines past and future for children of TimeLine->TimePeriod (BU).
For these objects, time travel goes through the parent TimeLine.

====================  =========================================================
Attribute             Description
====================  =========================================================

DATA:
N/A

FUNCTIONS:
N/A

CLASSES:
HistoryLine           history mixin for objects hanging on a TimeLine
====================  =========================================================
"""




# Imports
from bb_exceptions import DefinitionError




# Constants
# n/a

# Globals
# n/a

# Classes
class HistoryLine:
    """

    History traverser for objects hanging off TimeLine->TimePeriod->content
    that define .period as reference to parent TimePeriod.
    For these objects, .past and .future access the predecessor and successor
    objects via the parent TimePeriod.

    ====================  =====================================================
    Attribute             Description
    ====================  =====================================================

    DATA:
    n/a

    FUNCTIONS:
    set_history()         set past to argument, recur if necessary
    past                  getter/setter, finds own predecessor on period's
                          timeline
    future                getter/setter, finds own successor on period's
                          timeline
    ====================  =====================================================
    """

    def __init__(
            self,
            locator_attribute='bu_directory',
            recursive_attribute=None
    ):
        # name of leaf in parent period on which this object hangs, a dict
        self._locator_attribute = locator_attribute
        self._recursive_attribute = recursive_attribute

    def set_history(self, history, clear_future=True, recur=True):
        """

        set_history() -> None

        ``history`` and instance should usually be two instances of the same
        class. If ``clear_future`` is True, method will set future on instance
        to None. Generally want to keep this setting when extrapolating forward
        on a timeline. You would want to set the argument to False if you are
        substituting the past while preserving linkages to the future, or if you
        are extrapolating backwards.
        """
        self.past = history
        history.future = self

        if clear_future:
            self.future = None

        if recur:

            if self._recursive_attribute is not None:

                attr = getattr(self, self._recursive_attribute)
                attr_history = getattr(history, self._recursive_attribute)

                if attr:
                    attr.set_history(
                        attr_history,
                        clear_future=clear_future,
                        recur=True
                    )

    @property
    def past(self):
        """

        **property**

        This object should have a .period attribute to access its parent
        TimePeriod.
        """
        if self.period:
            bbid = self.id.bbid
            period_past = self.period.past
            if period_past:
                locator = getattr(period_past, self._locator_attribute)
                unit_past = locator.get(bbid)
            else:
                unit_past = None
            return unit_past
        else:
            raise DefinitionError('Call out of context')

    @past.setter
    def past(self, value):
        """

        **property setter**

        """
        if self.period:
            bbid = self.id.bbid
            period_past = self.period.past
            if period_past:
                locator = getattr(period_past, self._locator_attribute)
                locator[bbid] = value
        else:
            raise DefinitionError('Call out of context')

    @property
    def future(self):
        """

        **property**

        This object should have a .period attribute to access its parent
        TimePeriod.
        """
        if self.period:
            bbid = self.id.bbid
            period_next = self.period.future
            if period_next:
                locator = getattr(period_next, self._locator_attribute)
                unit_next = locator.get(bbid)
            else:
                unit_next = None
            return unit_next
        else:
            raise DefinitionError('Call out of context')

    @future.setter
    def future(self, value):
        """

        **property setter**

        """

        if self.period:
            bbid = self.id.bbid
            period_next = self.period.future
            if period_next:
                locator = getattr(period_next, self._locator_attribute)
                locator[bbid] = value
        else:
            raise DefinitionError('Call out of context')

    def __iter__(self):
        """

        __iter__() -> iterator of obj

        This object should have a .period attribute to access its parent
        TimePeriod.
        """

        if self.period:
            bbid = self.id.bbid

            # defer to parent period's iterator
            for period in self.period:
                locator = getattr(period, self._locator_attribute)
                yield locator.get(bbid)
