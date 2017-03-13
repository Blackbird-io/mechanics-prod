



from data_structures.system.bbid import ID




class Transaction:

    def __init__(self, account_id, date, round_id=None, debit=0, credit=0):
        self._ledger = None

        self.id = ID()

        self.account_id = account_id
        self.round_id = round_id

        self.debit = debit
        self.credit = credit

        self.date = date

    def register(self, ledger):
        self.id.set_namespace(ledger.id.namespace)

        acct_id = self.account_id.hex if self.account_id else "NONE"
        rnd_id = self.round_id.hex if self.round_id else "NONE"

        seed = 'transaction %s - %s - %s - %s - %s' % (self.date.format(),
                                                       acct_id,
                                                       rnd_id,
                                                       self.debit,
                                                       self.credit)
        self.id.assign(seed)

        self._ledger = ledger

    def get_round(self):
        return self._ledger.cap_struct.rounds.get(self.round_id)

    def get_account(self):
        return self._ledger.cap_struct.accounts.get(self.account_id)
