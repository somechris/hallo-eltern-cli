import subprocess

import mda

class ProcmailMDA(mda.MDA):
    def deliver(self, message):
        subprocess.run(["/usr/bin/procmail"],
                       input=str(message),
                       text=True,
                       check=True)
