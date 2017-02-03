
from ..statement import Statement

class IncomeStatement(Statement):
    def __init__(self, parent=None, period=None):
        Statement.__init__(self, name="income statement", parent=parent,
                           period=period)
