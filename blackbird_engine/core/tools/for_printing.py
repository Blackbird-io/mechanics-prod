#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: tools.for_printing

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




#imports
#n/a




#globals
DEFAULT_LINE_WIDTH = 80

#functions
def format_as_line(obj,
                   name = None,
                   value = None,
                   prefix = "",
                   header = False,
                   width = DEFAULT_LINE_WIDTH,
                   left_tab = 4,
                   right_tab = 4):
    """


    format_as_line(obj,
                   [name = None,
                   [value = None,
                   [prefix = ""
                   [header = False,
                   [width = Globals.screen_width,
                   [left_tab = 4,
                   [right_tab = 4]]]]]]]) -> str


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
    blank = " "
    header_mark = ":"
    #
    #where args are blank, check for obj data
    if name is None:
        name = getattr(obj, "name", None)
    if value is None:
        if not header:
            value = getattr(obj, "value", None)
    #add a trailing space to any nonempty prefix
    if not prefix == "":
        prefix = prefix + " "
    #
    #format value
    try:
        value = "%.2F" % value
    except (TypeError,ValueError):
        value = str(value)
    #
    max_chars = width - left_tab - right_tab
    dots = dot * (max_chars - len(prefix) - len(str(name)) - len(value))
    blanks = " " * (max_chars - len(prefix) - len(str(name)) - len(header_mark))
    #
    if not header:
        result = prefix + str(name)+ dots + value
    else:    
        result = prefix + str(name) + header_mark
    left_tabbed = result.rjust(left_tab+len(result))
    result = left_tabbed.ljust(right_tab+len(left_tabbed))
    #
    return result

def format_completed(obj, **kargs):
    """


    format_completed(obj, *kargs) -> str


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
    result = None
    #
    mark_full = "[x]"
    mark_empty = "[ ]"
    try:
        completed = obj.guide.complete
    except AttributeError:
        completed = False
    #
    if completed:
        kargs["value"] = mark_full
    else:
        kargs["value"] = mark_empty
    #
    result = format_as_line(obj, **kargs)
    return result
    
    
