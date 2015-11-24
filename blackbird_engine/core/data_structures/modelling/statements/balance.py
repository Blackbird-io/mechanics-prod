
from .statement import Statement

class BalanceSheet:
    def __init__(self):
        self.starting = Statement(name="starting balance sheet")
        self.ending = Statement(name="ending balance sheet")
