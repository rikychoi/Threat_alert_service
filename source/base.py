class SourceBase:
    cycle = 60
    name = ""
    active = True

    def __init__(self):
        self.urls = []

    def collect(self):
        pass
