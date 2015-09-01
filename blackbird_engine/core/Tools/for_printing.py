#PROPRIETARY AND CONFIDENTIAL
#Property of Blackbird Logical Applications, LLC
#Copyright Blackbird Logical Applications, LLC 2015
#NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL OF ILYA PODOLYAKO

#Blackbird Environment
#Module: Tools.for_printing
"""

Module provides functions for formatting data into standard strings.
====================  ==========================================================
Attribute             Description
====================  ==========================================================

DATA:
n/a

FUNCTIONS:
format_as_line()      format data into a ``name...value`` line

CLASSES:
n/a
====================  ==========================================================
"""




#imports
import BBGlobalVariables as Globals




#globals
#n/a

#functions
def format_as_line(obj,
                   name = None,
                   value = None,
                   prefix = "",
                   header = False,
                   width = Globals.screen_width,
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

def format_completed(obj, *kargs):
    """

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
    completed = False
    mark_full = "[x]"
    mark_empty = "[ ]"
    #
    completed = getattr(obj, "blah")
    if completed:
        kargs["value"] = mark_full
    else:
        kargs["value"] = mark_empty
    #
    result = format_as_line(obj, *kargs)
    return result
    
    
