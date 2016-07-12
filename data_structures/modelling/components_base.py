# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL

# Blackbird Environment
# Module: data_structures.modelling.components_base
"""

Module defines ComponentsBase class, a container for instances of
BusinessUnit[Base].
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
ComponentsBase        container that stores instances of BusinessUnit[Base]
====================  ==========================================================
"""




# imports
import copy
import bb_exceptions
import bb_settings

from data_structures.system.relationships import Relationships




# globals
# n/a

# classes
class ComponentsBase(dict):
    """

    The SummaryComponents class defines a container that stores UnitSummary
    objects keyed by their bbid.
    ====================  ======================================================
    Attribute             Description
    ====================  ======================================================

    DATA:
    by_name               dict; keys are unit names, values are unit bbids
    relationships         instance of Relationships class

    FUNCTIONS:
    add_item()            adds an object to self, keyed under obj's bbid
    get_all()             returns list of all units in instance
    get_ordered()         returns a list of values, ordered by key
    ====================  ======================================================
    """

    def __init__(self):
        dict.__init__(self)
        self.by_name = dict()
        self.relationships = Relationships(self)

    def __str__(self, lines=None):
        """


        Components.__str__(lines = None) -> str


        Method concatenates each line in ``lines``, adds a new-line character at
        the end, and returns a string ready for printing. If ``lines`` is None,
        method calls _get_pretty_lines() on instance.
        """
        if not lines:
            lines = self._get_pretty_lines()
        line_end = "\n"
        result = line_end.join(lines)
        return result

    def add_item(self, bu):
        """


        ComponentsBase.add_item() -> None

        --``bu`` is an instance of BusinessUnit or BusinessUnitBase object

        Method adds bu to the instance, keyed as bu.id.bbid. If bu does not
        specify a bbid, method raises IDError.

        Method also registers each unit's id under the unit's name in
        instance.by_name.
        """
        if not bu.id.bbid:
            c = "Cannot add a component that does not have a valid bbid."
            raise bb_exceptions.IDError(c)
        bu.relationships.set_parent(self)
        self[bu.id.bbid] = bu
        if bu.tags.name:
            self.by_name[bu.tags.name] = bu.id.bbid

    def copy(self):
        """


        ComponentsBase.copy() -> ComponentsBase


        Method returns a deep copy of components. Uses Tags.copy() to create a
        shell. Method then sets result.by_name to a blank dictionary and adds a
        copy of each unit in the instance to the result.
        """
        result = copy.copy(self)
        result.relationships = self.relationships.copy()

        # customize container
        result.clear()
        result.by_name = dict()

        # fill container (automatically add names)
        for C in self.getOrdered():
            rC = C.copy()
            result.add_item(rC)

        return result

    def get_all(self):
        """


        ComponentsBase.get_all() -> list


        Method returns list of all units in instance; ordered if in DEBUG_MODE,
        unordered otherwise.
        """

        if bb_settings.DEBUG_MODE:
            # Use stable order to simplify debugging
            pool = self.get_ordered()
        else:
            pool = list(self.values())

        return pool

    def getOrdered(self, order_by=None):
        return self.get_ordered(order_by=order_by)

    def get_ordered(self, order_by=None):
        """


        ComponentsBase.get_ordered() -> list


        Method returns a list of every value in the instance, ordered by key.
        """
        result = []
        for k, bu in sorted(self.items(), key=order_by):
            result.append(bu)
        return result

    def _get_pretty_lines(self):
        """


        ComponentsBase._get_pretty_lines() -> list


        Method returns a list of strings that show each component in rows of
        three.
        """
        # Get string list for every unit, slap a new-line at the end of every
        # line and return a string with all the lines joined together.
        main_lines = []

        units = self.get_ordered()
        unit_count = len(units)

        group_size = 9
        group_count = unit_count // group_size
        # there are exactly 9 units in each group
        tail_count = unit_count % group_size
        group_header = "\nComponents %s through %s...\n"
        group_footer = "--"

        bunch_footer = ""
        bunch_size = 3

        box_width = None
        unit_spacer = " " * 3
        unit_header = r"#%s"

        # build out lines one group at a time. go through units in a group
        # in bunches of 3. each bunch of units makes up a row. there are
        # 3 bunches in group.

        # get the pretty print lines for each unit a bunch. zip the lines
        # together (line 1a with line 1b, etc.), separated by spacers. that
        # produces the row. then add headers on top of each unit. the row
        # is complete.

        # group print is 3 rows (one for each bunch), plus the group header.

        for i in range(group_count):
            group_lines = []

            group_start = i * group_size
            group_end = (i + 1) * group_size - 1

            filled_group_hdr = group_header % (group_start, group_end)
            group_lines.append(filled_group_hdr)

            # process the bunches; j is the index in the ordered list of units
            j = group_start
            while j < group_end:
                bunch = units[j:(j + bunch_size)]

                bunch_lines = []

                boxes = []
                for unit in bunch:
                    unit_box = unit._get_pretty_lines()
                    boxes.append(unit_box)
                if i == 0:
                    box_width = len(boxes[0][0])
                    # set box width once, to the first line of the first unit

                filled_unit_hdrs = []
                for k in range(j, (j + bunch_size)):
                    hdr = unit_header % k
                    hdr = hdr.center(box_width)
                    filled_unit_hdrs.append(hdr)

                filled_bunch_hdr = unit_spacer.join(filled_unit_hdrs)
                filled_bunch_hdr = "\t" + filled_bunch_hdr
                bunch_lines.append(filled_bunch_hdr)

                # boxes now contains 3 lists of strings. the lists are all the
                # same length because each unit prints in the same format. zip
                # all those lists together into tuples of (line1a, line1b,
                # line1c), (line2a, line2b, line2c), etc.

                zipped_boxes = zip(*boxes)

                for triplet in zipped_boxes:
                    line = unit_spacer.join(triplet)
                    line = "\t" + line
                    bunch_lines.append(line)

                bunch_lines.append(bunch_footer)
                # add a footer string after each bunch; footer can be empty

                group_lines.extend(bunch_lines)
                # row is over, move to the next 3 units. unit index goes up by 3.
                j = j + bunch_size

            # loop is over, add the group lines and a group footer to main lines.
            main_lines.extend(group_lines)
            main_lines.append(group_footer)

        # finished all the groups; now go through the tail
        # HAVE TO MANUALLY ADD A TAIL HEADER
        filled_tail_hdr = group_header % ((unit_count - tail_count),
                                          (unit_count - 1))
        main_lines.append(filled_tail_hdr)
        if tail_count != 0:
            tail_lines = []

            bunch_count = tail_count // bunch_size
            tail_start = unit_count - tail_count
            stub_count = tail_count % bunch_size

            j = tail_start
            for i in range(bunch_count):
                # build each bunch-row, extend tail_lines; then add the final
                # stub row
                bunch = units[j: (j + bunch_size)]

                bunch_lines = []

                boxes = []
                for unit in bunch:
                    unit_box = unit._get_pretty_lines()
                    boxes.append(unit_box)
                if not box_width:
                    box_width = len(boxes[0][0])
                    # set box_width in case tail is the only group

                filled_bunch_hdr = None
                filled_unit_hdrs = []
                for k in range(j, (j + bunch_size)):
                    hdr = unit_header % k
                    hdr = hdr.center(box_width)
                    filled_unit_hdrs.append(hdr)
                filled_bunch_hdr = unit_spacer.join(filled_unit_hdrs)
                filled_bunch_hdr = "\t" + filled_bunch_hdr
                bunch_lines.append(filled_bunch_hdr)

                # boxes now contains 3 lists of strings. the lists are all the
                # same length because each unit prints in the same format. zip
                # all those lists together into tuples of (line1a, line1b,
                # line1c), (line2a, line2b, line2c), etc.

                zipped_boxes = zip(*boxes)

                for triplet in zipped_boxes:
                    line = unit_spacer.join(triplet)
                    line = "\t" + line
                    bunch_lines.append(line)

                bunch_lines.append(bunch_footer)
                # add a footer string after each bunch; footer can be empty

                main_lines.extend(bunch_lines)
                # row is over, move to the next 3 units. unit index goes up by 3.
                j = j + bunch_size

            # finally, manually append the tail_stub row
            stub_lines = []
            bunch = units[(stub_count * -1):]
            boxes = []
            for unit in bunch:
                unit_box = unit._get_pretty_lines()
                boxes.append(unit_box)

            if not box_width:
                box_width = len(boxes[0][0])
                # set box_width in case the tail stub is the only row

            filled_unit_hdrs = []
            for k in range(j, (j + stub_count)):
                hdr = unit_header % k
                hdr = hdr.center(box_width)
                filled_unit_hdrs.append(hdr)
            filled_bunch_hdr = unit_spacer.join(filled_unit_hdrs)
            filled_bunch_hdr = "\t" + filled_bunch_hdr
            stub_lines.append(filled_bunch_hdr)

            zipped_boxes = zip(*boxes)

            for triplet in zipped_boxes:
                line = unit_spacer.join(triplet)
                line = "\t" + line
                stub_lines.append(line)

            stub_lines.append(bunch_footer)
            main_lines.extend(stub_lines)

        main_lines.append(group_footer)
        main_lines.append(group_footer)

        return main_lines
