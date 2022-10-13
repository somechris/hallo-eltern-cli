import subprocess

from . import MDA


class ProcmailMDA(MDA):
    def deliver(self, message):
        subprocess.run(["/usr/bin/procmail"],
                       input=str(message),
                       text=True,
                       check=True)
