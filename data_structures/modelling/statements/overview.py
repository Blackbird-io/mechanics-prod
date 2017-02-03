from ..statement import Statement

class OverviewStatement(Statement):
    def __init__(self, parent=None, period=None):
        Statement.__init__(self, name="overview", parent=parent, period=period)
