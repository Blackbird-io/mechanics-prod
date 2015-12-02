class Parameters(dict):
    def __init__(self):
        dict.__init__(self)

    def add(self, params, overwrite=False):
        """
        expects data to be a dictionary
        """
        if overwrite:
            self.update(params)
        else:
            existing = params.keys() & self.keys()
            if existing:
                c = "New params overlap with existing keys. Implicit overwrite prohibited."
                raise Error(existing, c)
            else:
                self.update(params)

             
