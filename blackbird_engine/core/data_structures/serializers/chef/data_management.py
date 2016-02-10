#Data structures for managing excel interface

# Imports
import copy

from .field_names import FieldNames

# Module Globals
# n/a

class Range:
    """

    Uses absolute coordinates
    """
    ending = None
    # To allow property below

    def __init__(self, starting=None):
        
        self.starting = starting

    # May be starting should be a property, so when you change it, you move
    # all values up or down. Should also get error if its < 1. 

class Lookup(Range):
    """
    values in the lookup are always relative to the starting point
    """
    def __init__(self, *pargs, **kwargs):
        Range.__init__(self, *pargs, **kwargs)
        self.by_name = dict()

    @property
    def ending(self):
        result = None
        
        if self.by_name: 
            starting_value = self.starting or 0
            result = starting_value + max(self.by_name.values())

        return result

    def copy(self):
        """

        -> Lookup
        
        Return a deep copy
        """
        result = copy.copy(self)
        result.by_name = self.by_name.copy()

        return result
        
    def get_position(self, name):
        first_position = self.starting or 0
        result = first_position + self.by_name[name]
        return result
        # Return natural if starting is blank

    def update(self, source):
        """
        -> None
        """
        self.by_name.update(source.by_name)
        

class Area:
    """
    could also name this ``Field``
    """
    
    def __init__(self, name=None):
        self.name = name
        self.parent = None
        
        self.rows = Lookup()
        self.columns = Lookup()

    def copy(self):
        """

        -> Area

        Return deep copy
        """
        result = copy.copy(self)
        result.rows = self.rows.copy()
        result.columns = self.columns.copy()

        return result

    def update(self, source_area):
        """
        -> None
        """
        self.rows.update(source_area.rows)
        self.columns.update(source_area.columns)
        
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
        self.consolidated.cell = None
        
        self.derived = Range()
        self.derived.calculations = list()
        # Each item should be a driver_data object
        self.derived.cell = None

        self.detailed = Range()
        self.detailed.cell = None

        self.sheet = None
        self.cell = None

##    def copy(self):
##        result = copy.copy(self)       
    
    def get_coordinates_old(self, column):
        """
        -> tuple(int, int)

        x (column), y (row)

        # should return a dictionry of "sheet":, "row":, "column":
        # shoudl return a formatted string {sheet}!{column}{row}
        """
        result = ""
        if self.sheet:
            result += sheet.title
            result += "!"

        result += get_column_letter(column)
        result += str(self.ending)
        
        return result

    def get_coordinates(self, include_sheet=True):
        result = None
        if not self.cell:
            raise ExcelPrepError

        else:
            result = "'" + self.cell.parent.title + "'" + "!"
            result += self.cell.coordinate
            
        return result
        
        # Each line must be able to deliver a full coordinate set, with
        # sheet. Could add a ._set_sheet() method that goes through
        # each line and sets the sheet pointer. Or could do something with
        # like a shared pointer, though that's uglier. Let's just have
        # a function. When we get the right sheet for that unit we, we
        # _set_sheet() and then we can derive. Or can pass it in during the
        # call somehow. But that requires the coordinator to know where to look

    def set_sheet(self, sheet):
        self.sheet = sheet

    
        
class UnitData:
    def __init__(self, sheet=None):
        self.sheet = sheet

    def set_sheet(self, sheet):
        self.sheet = sheet
        
class RowData(dict):
    field_names = FieldNames()
    
    def __init__(self):
        self[self.field_names.VALUES] = None
        self[self.field_names.LABELS] = None
        
##        self[self.field_names.COMMENT] = None
        # Comment always goes on the labels line?
##        self[self.field_names.REFERENCES] = None

        # Probably better to change this into a regular instance with attributes (.value, .label), etc.
        # then have a .get_dict() method that delivers the instance dictionary.

        # Would fit in better anyways. 

class DriverData:
    """
    rows : list of RowData objects
    references : dictionary of strings to objects, suite
    """
    def __init__(self):
        self.rows = []
        self.formula = None
        self.references = None
        self.conversion_map = None
        self.name = None

class SheetData:
    def __init__(self):

        self.general = Area()
        self.current_row = None
        self.current_column = None
        self.consolidation_size = None
        # Number of rows that consolidation area will take up

    def add_area(self, area_name, overwrite=False):
        result = None
        if getattr(self, area_name, None):

            c = "No implicit overwrites."
            raise Exception(c)

        else:

            new_area = Area(area_name)
            setattr(self, area_name, new_area)
            new_area.parent = self

            result = new_area

        return result

    def set_sheet(self, sheet):

        self.sheet = sheet

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




        


    

        

    
