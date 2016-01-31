#Data structures for managing excel interface

class PositionTracker:
    """

    Uses absolute coordinates
    """

    def __init__(self, starting=None, ending=None):
        
        self.starting = starting
        self.ending = None
        self.active = None
        # points to active row or column

class PositionLookup(PositionTracker):
    """
    Uses position relative to starting point
    """

    def __init__(self, *pargs, **kwargs):
        PositionTracker.__init__(self, *pargs, **kwargs)
        self.by_name = dict()

    def get_position(self, name):
        result = self.starting + self.by_name[name]
        return result

    def update(self, source):
        pass

class RangeLookup:
    """
    """
    
    def __init__(self):

        self.rows = PositionLookup()
        self.cols = PositionLookup()

    def update(self, source):
        # update both rows and cols by name
        pass

        
class SplitPosition(PositionTracker):

    """
    For coordinating line location across multiple non-continguous
    ranges of rows.
    """

    def __init__(self):

        PositionTracker.__init__(self)

        self.consolidated = PositionTracker()
        self.consolidated.cells = []
        # A 1-dim array of cells where we store values
        self.derived = PositionTracker()
        self.details = PositionTracker()

class XL:
    def __init__(self):
        self.location = LineManager()
        self.book = None
        self.in_progress = True

    
