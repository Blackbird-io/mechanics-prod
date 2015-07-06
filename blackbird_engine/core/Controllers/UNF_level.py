#level


class Level(list):
    def __init__(self):
        list.__init__(self)
        self.guide = Guide()
        self.last = 0
