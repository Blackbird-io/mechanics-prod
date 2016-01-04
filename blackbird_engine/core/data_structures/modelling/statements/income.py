
from .._new_statement import Statement

class IncomeStatement(Statement):
    def __init__(self):
        Statement.__init__(self, name="income statement")
