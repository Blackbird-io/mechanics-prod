



from data_structures.system.bbid import ID




class Ledger:

    def __init__(self, cap_struct):
        self.cap_struct = cap_struct

        self.id = ID()
        self.id.set_namespace(self.cap_struct.id.namespace)
        self.directory = dict()   # store by ID

        self.by_name = dict()     # store by Name: ID
        self.by_round = dict()    # store by Round: set(IDs)
        self.by_account = dict()  # store by Account: set(IDs)

    def add_transaction(self, trx):
        trx.register(self.id.namespace)

        #  register in directories
        self.directory[trx.id.bbid] = trx

        self.by_name[trx.name] = trx.id.bbid

        rnd_set = self.by_round.setdefault(trx.round, set())
        rnd_set.add(trx.id.bbid)

        act_set = self.by_account.setdefault(trx.account, set())
        act_set.add(trx.id.bbid)

    def get_trx(self, id):
        trx = self.directory.get(id, None)

        return trx

    def get_trx_by_account(self, account):
        trx = list()

        id_list = self.by_account.get(account, set())
        for id in id_list:
            trx.append(self.directory[id])

        return trx

    def get_trx_by_name(self, name):
        id = self.by_name.get(name, None)
        trx = self.directory.get(id, None)

        return trx

    def get_trx_by_round(self, round):
        trx = list()

        id_list = self.by_round.get(round, set())
        for id in id_list:
            trx.append(self.directory[id])

        return trx
