#Data structures for managing excel interface

class Range:
    """

    Uses absolute coordinates
    """

    def __init__(self, starting=None, ending=None):
        
        self.starting = starting
        self.ending = None
        self.data = list() 
        # points to active row or column

class Lookup(Range):
    """
    values in the lookup are always relative to the starting point
    """

    def __init__(self, *pargs, **kwargs):
        Range.__init__(self, *pargs, **kwargs)
        self.by_name = dict()

    def get_position(self, name):
        result = self.starting + self.by_name[name]
        return result

    def update(self, source):
        pass

class Area:
    """
    could also name this ``Field``
    """
    def __init__(self):
        
        self.rows = Lookup()
        self.cols = Lookup()
        
class LineData(PositionTracker):

    """
    For coordinating line location across multiple non-continguous
    ranges of rows.
    """

    def __init__(self):

        Range.__init__(self)

        self.consolidated = Range()
        # Expects each item in consolidated.data to be a row_data object
        self.derived = Range()
        # Expects each item in derived.data to be a driver_data object
        self.detailed = Range()
        # detailed.data should be empty?

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

class UnitData:
    def __init__(self, book=None, sheet=None):
        self.sheet = sheet
        
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
        
             

        


    

        

    
