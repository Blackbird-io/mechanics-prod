



from .ledger import Ledger

from data_structures.modelling.container import Container
from data_structures.system.bbid import ID




class CapStruct:
    def __init__(self, bu):
        self.id = ID()
        self.id.set_namespace(bu.id.bbid)

        self.ledger = Ledger(self)
        self.accounts = Container(self)
        self.rounds = Container(self)

    def get_value(self, date):
        return 88
