



from data_structures.system.bbid import ID
from data_structures.system.tags_mixin import TagsMixIn




class Account(TagsMixIn):
    def __init__(self, name, namespace):
        TagsMixIn.__init__(name)

        self.id = ID()
        self.id.set_namespace(namespace)
        self.id.assign(name)

    def get_value(self, date):
        return None