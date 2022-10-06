import mda

class StdoutMDA(mda.MDA):
    def deliver(self, message):
        print(message)
