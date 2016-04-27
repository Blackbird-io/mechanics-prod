
from data_structures.modelling.line_item import LineItem

class Link(LineItem):
    def __init__(self, target):
        LineItem.__init__(self, target.name)
        self.target = target