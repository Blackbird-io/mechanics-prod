#Data structures for managing excel interface

class Range:
    """

    Uses absolute coordinates
    """

    def __init__(self, starting=None, ending=None):
        
        self.starting = starting
        self.ending = None
##        self.data = list() 
        # points to active row or column

    # May be starting should be a property, so when you change it, you move
    # all values up or down. Should also get error if its < 1. 

class Lookup(Range):
    """
    values in the lookup are always relative to the starting point
    """
    @property
    def ending(self):
        result = None
        
        if self.by_name: 
            starting_value = self.starting or 0
            result = starting_value + max(self.by_name.values())

        return result

    def __init__(self, *pargs, **kwargs):
        Range.__init__(self, *pargs, **kwargs)
        self.by_name = dict()

    def get_position(self, name):
        first_position = self.starting or 0
        result = first_position + self.by_name[name]
        return result
        # Return natural if starting is blank

    def update(self, source):
        pass

class Area:
    """
    could also name this ``Field``
    """
    
    def __init__(self, name=None):
        self.name = name
        self.parent = None
        
        self.rows = Lookup()
        self.cols = Lookup()
        
class LineData(Range):

    """
    For coordinating line location across multiple non-continguous
    ranges of rows.
    """

    def __init__(self):

        Range.__init__(self)

        self.consolidated = Range()
        self.consolidated.sources = list()
        # List should contain pointers to source lines
        
        self.derived = Range()
        self.derived.calculations = list()
        # Each item should be a driver_data object

        self.detailed = Range()

    def get_coordinates(self, column):
        """
        -> tuple(int, int)

        x (column), y (row)

        # should return a dictionry of "sheet":, "row":, "column":
        """
        x = column
        y = self.ending

        result = (x, y)
        return result
        # Each line must be able to deliver a full coordinate set, with
        # sheet. Could add a ._set_sheet() method that goes through
        # each line and sets the sheet pointer. Or could do something with
        # like a shared pointer, though that's uglier. Let's just have
        # a function. When we get the right sheet for that unit we, we
        # _set_sheet() and then we can derive. Or can pass it in during the
        # call somehow. But that requires the coordinator to know where to look

    def set_sheet(self):
        pass
        
class UnitData:
    def __init__(self, book=None, sheet=None):
        self.sheet = sheet

    def set_sheet(self):
        pass
        
class RowData:
    def __init__(self):
        dict.__init__(self)
        self["value"] = None
        self["label"] = None
        self["comment"] = None
        self["references"] = None

class DriverData:
    """
    rows : list of RowData objects
    references : dictionary of strings to objects, suite
    """
    def __init__(self):
        self.rows = []
        self.formula_string = None
        self.formula_references = None
        self.conversion_map = None

class SheetData:

    def __init__(self):

        self.general = Area()
        self.current_row = None
        self.current_column = None

    # Alternative interface:
        # def __init__(self):
        #   Area.__init__(self)
        #   self.current_row = None
        #   self.current_column = None
        #
        ## then can add new subareas (time_line, params, etc)
        ## so have a general and a specific

        ## sheet can also have a .public and .private attrs
        ## each of which could be a dictionary of areas.
        ## 




        


    

        

    
