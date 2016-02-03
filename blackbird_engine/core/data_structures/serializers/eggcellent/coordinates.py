class Coordinates:

    LOWEST_ROW = 1
    LOWEST_COLUMN = 1

    def __init__(self):

        self._row = None
        self._column = None
        self._sheet = None

    @property
    def row(self):

        # only set if > 0

    def to_dict(self, alpha_column=True):
        #return dictionary
