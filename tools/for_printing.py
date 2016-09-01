# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL
# Blackbird Environment
# Module: tools.for_printing

"""

Module provides functions for formatting data into standard strings.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
format_as_line()      format data into a ``name...value`` line
format_completed()    format as line with a completed indicator

CLASSES:
n/a
====================  ==========================================================
"""




# imports
import bb_settings




# globals
DEFAULT_LINE_WIDTH = bb_settings.SCREEN_WIDTH


# functions
def format_as_line(obj,
                   name=None,
                   value=None,
                   prefix="",
                   header=False,
                   width=DEFAULT_LINE_WIDTH,
                   left_tab=4,
                   right_tab=4):
    """


    format_as_line() -> str


    Function formats objects into a line.

    Output follows the format:
    [left_tab][prefix][name]..................................[value][right_tab]

    If ``name`` and ``value`` are left blank, function will try to read the
    attributes off the object.

    If ``header`` is True, function will hide dots and value in the output. The
    setting is useful for displaying headers before a bunch of details.

    EXAMPLE 1:

    >>>line_1 = format_as_line(None, "revenue", 5)
    >>>print(line_1)
    revenue............................................................5

    EXAMPLE 2:

    >>>class New:
    ...     def __init__(self, name, value):
                self.name = name
                self.value = value
    >>>rev = New("revenue", 5)
    >>>line_2 = format_as_line(rev)
    >>>print(line_2)
    revenue...........................................................5
    """
    result = None
    #
    dot = "."
    header_mark = ":"

    # where args are blank, check for obj data
    if name is None:
        name = None
        if getattr(obj, "tags", None):
            name = getattr(obj.tags, "name", None)

    if value is None:
        if not header:
            value = getattr(obj, "value", None)
    # add a trailing space to any nonempty prefix
    if not prefix == "":
        prefix += " "

    # format value
    try:
        value = "%.2F" % value
    except (TypeError, ValueError):
        value = str(value)
    #
    max_chars = width - left_tab - right_tab
    dots = dot * (max_chars - len(prefix) - len(str(name)) - len(value))
    #
    if not header:
        result = prefix + str(name) + dots + value
    else:
        result = prefix + str(name) + header_mark
    left_tabbed = result.rjust(left_tab + len(result))
    result = left_tabbed.ljust(right_tab + len(left_tabbed))
    #
    return result


def format_completed(obj, **kargs):
    """


    format_completed() -> str


    Function formats obj and arguments as a line with a completeness indicator
    (``[ ]`` or ``[x]``).

    Function shows line as complete iff obj.guide.complete is True. In all other
    cases, function shows line as incomplete. Function intercepts attribute
    errors for objects without a ``guide`` attribute.

    Function only sets the ``value`` key in kargs; format_as_line() then does
    all of the real formatting work.

    EXAMPLE:

    ...
    >>>metric_1
    <Guide object at 0x00065670>
    >>>print(metric_1.guide.completed)
    False
    >>>print(format_completed(metric_1, name = "pecan pie"))
    pecan pie ........................................................[ ]
    >>>metric_1.guide.completed = True
    >>>print(format_completed(metric_1, name = "pecan pie"))
    pecan pie ........................................................[x]
    """

    mark_full = "[x]"
    mark_empty = "[ ]"
    completed = getattr(obj.guide, 'complete', False)

    if completed:
        kargs["value"] = mark_full
    else:
        kargs["value"] = mark_empty

    result = format_as_line(obj, **kargs)
    return result


def view_as_unit(
    company,
    top_element = "=", side_element = "|", box_width = 23, field_width = 5
):
    """


    as_unit() -> list[str]

    --``company`` BusinesUnitBase

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
    data_width = box_width - field_width - 2 * len(side_element) - 5
    # formatting rules
    template = (
        "{side} {{0:<{0}}} : {{1:>{1}}} {side}"
    ).format(
        field_width, data_width, side=side_element
    )

    # fields:
    fields = ["NAME", "ID", "COMPS"]
    # data
    data = {}

    # name
    unit_name = str(company.name)
    # abbreviate unit name if its too long
    if len(unit_name) > data_width:
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
    id_tail = str(company.id.bbid)[-tail_width:]
    data["ID"] = id_dots + id_tail

    data["COMPS"] = str(len(company.components.get_all()))

    lines = []
    top_border = reg_corner + top_element * (box_width - 2) + reg_corner
    lines.append(top_border)

    for field in fields:
        new_line = template.format(field, data[field])
        lines.append(new_line)

    # add a bottom border symmetrical to the top
    lines.append(top_border)

    return lines
