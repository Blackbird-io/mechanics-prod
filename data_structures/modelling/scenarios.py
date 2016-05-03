BASE = "base"
OTHERS = ["awesome", "good", "bad", "terrible"]


class Scenarios(dict):
    """
    - Scenarios should take precedence over TimeLine.parameters members,
    but will need to add TimeLine.parameters to self.base at some point

    """

    def __init__(self, base=dict()):
        dict.__init__(self)

        self[BASE] = base

        self.original_entries = list()
        self.original_entries.append(BASE)

        for o in OTHERS:
            self[o] = dict()
            self.original_entries.append(o)

    @property
    def base(self):
        return self[BASE]

    def get_keys(self):
        result = self.original_entries
        for k in sorted(self.keys()):
            if k not in result:
                result.append(k)

        return result

    def update_base(self, new_values):
        for k in new_values.keys():
            if k not in self.base.keys():
                self.base[k] = new_values[k]
