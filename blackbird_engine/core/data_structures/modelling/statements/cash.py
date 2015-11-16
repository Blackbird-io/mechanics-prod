
from .statement import Statement

class CashFlowStatement(Statement):
    def __init__(self):
        Statement.__init__(self, name="cash flow statement")
