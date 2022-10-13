from . import MDA


class StdoutMDA(MDA):
    def deliver(self, message):
        print(message)
