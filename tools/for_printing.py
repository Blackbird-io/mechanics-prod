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
import itertools

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
        if getattr(obj, "tags", None):
            name = getattr(obj.tags, "title", None)

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


def view_as_base(
    company,
    top_element = "=", side_element = "|", box_width = 23, field_width = 5
):
    """


    view_as_base() -> list[str]

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
    data["NAME"] = _compact_name(company.title, data_width)

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


def view_as_unit(
    company,
    top_element="=", side_element="|", box_width=23, field_width=5
):
    """


    view_as_unit() -> list


    Method returns a list of strings that displays a box if printed in
    order. Line ends are naked (i.e, lines do **not** terminate in a
    new-line character).

    Box format (live units):

    +=====================+
    | NAME  : Baltimore-4 |
    | ID    : ...x65-0b78 |
    | DOB   :  2015-04-01 |
    | LIFE  :         43% |
    | STAGE :      MATURE |
    | TYPE  :         OPS |
    | FILL  :        True |
    | COMPS :          45 |
    +=====================+

    Box format (dead units):

    +=====\========/======+
    | name \: Balt/more-4 |
    | id    \ .../65-0b78 |
    | dob   :\ 2/15-04-01 |
    | life  : \/      43% |
    | stage : /\   MATURE |
    | type  :/  \     OPS |
    | fill  /    \   True |
    | comps/:     \    45 |
    +=====/========\======+

    Box format (unborn units):

    ?  = = = = = = = = =  ?
    | NAME  : Baltimore-4 |
      ID    : ...x65-0b78
    | DOB   :  2015-04-01 |
      LIFE  :         43%
    | STAGE :      MATURE |
      TYPE  :         OPS
    | FILL  :        True |
      COMPS :          45
    ?  = = = = = = = = =  ?

    """
    reg_corner = "+"
    alt_corner = "?"
    alt_element = " "
    data_width = box_width - field_width - 2 * len(side_element) - 5
    # formatting rules
    template = (
        "{side} {{0:<{0}}} : {{1:>{1}}} {side}"
    ).format(
        field_width, data_width, side=side_element
    )
    # fields:
    fields = ["NAME",
              "ID",
              "DOB",
              "LIFE",
              "EVENT",
              "TYPE",
              "FILL",
              "SIZE",
              "COMPS"]
    # data
    data = {}
    data["NAME"] = _compact_name(company.tags.title, data_width)

    id_dots = "..."
    tail_width = data_width - len(id_dots)
    id_tail = str(company.id.bbid)[-tail_width:]
    data["ID"] = id_dots + id_tail

    date_of_birth = company.life.events.get(company.life.KEY_BIRTH)
    if date_of_birth:
        dob = date_of_birth.isoformat()
    else:
        dob = "n/a"
    data["DOB"] = dob

    percent = company.life.percent
    if percent is not None:
        life = '{}%'.format(round(percent))
    else:
        life = "n/a"
    data["LIFE"] = life

    event_name = company.life.get_latest()[0]
    event_name = event_name or "n/a"
    # Choose empty string if life has no events yet
    data["EVENT"] = event_name[:data_width]

    unit_type = str(company.type)[:data_width]
    data["TYPE"] = unit_type.upper()

    data["FILL"] = str(company.filled)

    data["COMPS"] = str(len(company.components.get_living()))

    data["SIZE"] = str(company.size)[:data_width]

    #
    # assemble the real thing
    lines = []
    top_border = reg_corner + top_element * (box_width - 2) + reg_corner
    lines.append(top_border)
    #
    for field in fields:
        new_line = template.format(field, data[field])
        lines.append(new_line)
    #
    # add a bottom border symmetrical to the top
    lines.append(top_border)

    # Post-processing (dashed lines for units scheduled to open in the
    # future, x's for units that have already closed)
    if company.life.ref_date and date_of_birth:
        if company.life.ref_date < date_of_birth:
            #
            alt_width = int(box_width / 2) + 1
            alt_border = (top_element + alt_element) * alt_width
            alt_border = alt_border[:(box_width - 2)]
            alt_border = alt_corner + alt_border + alt_corner
            #
            core_lines = lines[1:-1]
            for i in range(0, len(core_lines), 2):
                line = core_lines[i]
                core_symbols = line[1:-1]
                line = alt_element + core_symbols + alt_element
                core_lines[i] = line
            #
            lines = [alt_border] + core_lines + [alt_border]

    date_of_death = company.life.events.get(company.life.KEY_DEATH)
    if company.life.ref_date and date_of_death:
        if company.life.ref_date > date_of_death:

            alt_lines = []
            line_count = len(lines)
            down_start = int((box_width - line_count) / 2)
            # X is line_count lines wide
            up_start = down_start + line_count

            for i in range(line_count):
                #
                # replace the character at (down_start + i) with "\"
                # replace the character at (up_start - i) with "/"
                #
                line = lines[i]
                #
                down_pos = (down_start + i)
                seg_a = line[: (down_pos)]
                seg_b = line[(down_pos + 1):]
                line = seg_a + "\\" + seg_b
                #
                up_pos = (up_start - i)
                seg_a = line[:(up_pos)]
                seg_b = line[(up_pos + 1):]
                line = seg_a + "/" + seg_b
                # line = line.casefold()
                #
                alt_lines.append(line)
            lines = alt_lines

    return lines


def view_as_time_line(time_line, dates=None, sep="<<", border="-", hook=True):
    """


    view_as_time_line() -> list

    Method returns a list of strings. Strings are raw: they do NOT end in
    new-line characters.

    When printed in order, the strings illustrate the instance contents for
    each date in ``dates``. Illustration follows the form:


    Row Label       Graphic
    ------------------------------------------------------------------------
    top_pad	        	  __________________
    top_brdr  	---------|------------------|---------------------------
    calendar	PERIOD: <|   2015-06-01    <|   2015-07-01  <<    . . .
    bot_brdr	---------|---------}--------|---------------------------
    hanger		         |         |        |
    bu_line	        	 | +==============+ |
    bu_line		         | |              | |
    bu_line	        	 | |  BU CONTENT  | |
    bu_line		         | |     . . .    | |
    bu_line	        	 | |              | |
    bu_line		         | +==============+ |
    bot_pad	        	 |__________________|
    \n
    """

    clean_lines = []
    # lines is the final, flat list of strings
    #
    if not dates:
        dates = sorted(time_line.keys())
    cushion = 1
    hook_char = "}"
    lead = "PERIOD:"
    space = " "
    #
    underscore = "_"
    bu_lines = list()
    bu = time_line.model.get_company()
    if bu:
        bu_lines = view_as_unit(bu)
    bu_width = 20
    # default width should be a setting (probably same as bu view)
    if bu_lines:
        bu_width = len(bu_lines[0])
    bu_height = len(bu_lines)
    sep_width = len(sep)
    column_width = bu_width + cushion * 2 + sep_width
    column_count = bb_settings.SCREEN_WIDTH // column_width
    #
    # the first column stays constant from row to row: it's just the lead,
    # plus borders and white space. make all the strings once, then use them
    # for each row.
    #
    c0_width = len(lead) + cushion + sep_width
    #
    top_pad_c0 = space * c0_width
    top_brdr_c0 = border * c0_width
    calendar_c0 = lead + space * cushion + sep
    bot_brdr_c0 = top_brdr_c0[:]
    hanger_c0 = space * c0_width
    bu_line_c0 = space * c0_width
    bot_pad_c0 = top_pad_c0[:]
    c0 = [top_pad_c0,
          top_brdr_c0,
          calendar_c0,
          bot_brdr_c0,
          hanger_c0]
    c0.extend([bu_line_c0 for i in range(bu_height)])
    c0.append(bot_pad_c0)
    #
    # now, build each row. to do so, walk dates in steps of column_count. for
    # each date, build a column (list) of strings. if the column contains the
    # current date, apply ``box`` post-processing to that column. store each
    # column in the columns list for that row. then, when done with all the
    # dates in the row, zip all of the columns together. the zipped object
    # will contain tuples that represent each display line necessary to show
    # that row: ([c0_line0], [c1_line0], ...).
    #
    # to make a flat string suitable for ``lines``, join all of the elements
    # in a tuple, then append that line to lines. do so for all lines in the
    # row (all tuples in the zipped object).
    #
    # finally, when all the hard work is done, add an empty string at the end
    # of the row
    #
    for i in range(0, len(dates), column_count):
        #
        # build a row of c0 plus column_count date-specific columns
        #
        row = []
        row.append(c0)
        row_dates = dates[i : (i + column_count)]
        #
        for end_date in row_dates:
            #
            # build a column for each date
            #
            period = time_line[end_date]
            post_processing = False
            if end_date == time_line.current_period.end:
                post_processing = True
            #
            top_pad = space * column_width
            top_brdr = border * column_width
            calendar = end_date.isoformat().center(column_width - sep_width)
            calendar = calendar + sep
            bot_brdr = top_brdr[:]
            hanger = space * column_width
            col_bu_lines = []
            if bu:
                bot_brdr = hook_char.center(column_width, border)
                hanger = "|".center(column_width)
                for line in bu._get_pretty_lines():
                    adj_line = line.center(column_width)
                    col_bu_lines.append(adj_line)
            else:
                for k in range(bu_height):
                    bu_line_blank = space * column_width
                    col_bu_lines.append(bu_line_blank)
            bot_pad = top_pad[:]
            #
            if post_processing:
                top_pad = space + underscore * (column_width - 2) + space
                bot_pad = underscore * column_width
            #
            column = [top_pad,
                      top_brdr,
                      calendar,
                      bot_brdr,
                      hanger]
            column.extend(col_bu_lines)
            column.append(bot_pad)
            #
            if post_processing:
                for j in range(1, len(column)):
                    line = column[j]
                    column[j] = "|" + line[1:-1] + "|"
            #
            row.append(column)
        #
        # now zip the columns together into clean lines
        zipped_row = zip(*row)
        # zipped_row should be a tuple w len == column_count + 1
        for line_elements in zipped_row:
            flat_line = "".join(line_elements)
            clean_lines.append(flat_line)
        else:
            clean_lines.append("")
            # add a blank line after every row
    #
    return clean_lines


def view_as_components(comps):
    """


    view_as_components() -> list

    Method returns a list of strings that show each component in rows of
    three.
    """

    # Get string list for every unit, slap a new-line at the end of every
    # line and return a string with all the lines joined together.
    units = comps.get_ordered()

    group_size = 9
    group_header = "\nComponents %s through %s...\n"
    group_footer = "--"

    bunch_footer = ""
    bunch_size = 3

    box_width = None
    unit_spacer = " " * 3

    # build out lines one group at a time. go through units in a group
    # in bunches of 3. each bunch of units makes up a row. there are
    # 3 bunches in group.

    # get the pretty print lines for each unit a bunch. zip the lines
    # together (line 1a with line 1b, etc.), separated by spacers. that
    # produces the row. then add headers on top of each unit. the row
    # is complete.

    # group print is 3 rows (one for each bunch), plus the group header.

    lines = []
    # format and number all components
    box_list = enumerate(map(view_as_unit, units))
    # group all components into chunks of 9
    grouper = itertools.repeat(box_list, group_size)
    for i, group in enumerate(itertools.zip_longest(*grouper)):
        group = [u for u in group if u]
        if not group:
            continue

        # group header. 0th element in each row is unit number.
        group_tip = group[0][0]
        group_end = group[-1][0]
        filled_group_hdr = group_header % (group_tip, group_end)
        lines.append(filled_group_hdr)

        # bunch the group into chunks of 3
        buncher = itertools.repeat(iter(group), bunch_size)
        for j, bunch in enumerate(itertools.zip_longest(*buncher)):
            bunch = [u for u in bunch if u]
            if not bunch:
                continue

            if i == 0:
                # set box width once, to the first line of the first unit
                box_width = len(bunch[0][1][0])

            filled_unit_hdrs = []
            for unit_num, box in bunch:
                hdr = '#{}'.format(unit_num)
                hdr = hdr.center(box_width)
                filled_unit_hdrs.append(hdr)
            filled_bunch_hdr = unit_spacer.join(filled_unit_hdrs)
            filled_bunch_hdr = "\t" + filled_bunch_hdr
            lines.append(filled_bunch_hdr)

            # join unit boxes line-by-line, side-by-side
            zipped_boxes = zip(*(u[1] for u in bunch))
            for triplet in zipped_boxes:
                line = unit_spacer.join(triplet)
                line = "\t" + line
                lines.append(line)
            lines.append(bunch_footer)
    lines.extend(2 * [group_footer])
    return lines


# *************************************************************************#
#                          NON-PUBLIC METHODS                              #
# *************************************************************************#

def _compact_name(unit_name, data_width):
    """


    _compact_name() -> str

    Fits the name into a width-size box.
    """

    if len(unit_name) > data_width:
        unit_name_parts = unit_name.split()
        if len(unit_name_parts) > 1:
            last_part = unit_name_parts[-1]
            initials = ""
            for part in unit_name_parts[:-1]:
                initial = part[:1] + "."
                initials = initials + initial
            unit_name = initials + last_part
    return unit_name[:data_width]
