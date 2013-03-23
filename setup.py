#!/usr/bin/env python

import re
import requests.certs
import shutil
import sys
from cx_Freeze import setup, Executable

shutil.copyfile("ressources/lib/putio2/putio2.py",
                "ressources/lib/putio2/putio2.py.save")

with open("ressources/lib/putio2/putio2.py", 'r+') as f:
    sub = re.sub(r'(allow_redirects=redir)',
                 r'\1, verify="cacert.pem"', f.read())
    f.seek(0)
    f.write(sub)
buildOptions = dict(
        compressed = True,
        path = sys.path + ["ressources/lib"],
        includes = ["argparse", "collections", "configparser", "datetime",
                    "json", "logging", "os", "putio2", "re", "requests",
                    "signal", "subprocess", "sys", "urllib.parse"],
        include_files = [(requests.certs.where(),"cacert.pem")],
        packages = ["requests"])

setup(name="puclio",
      version="0.1",
      description="A Putio Utility, Command LIne Oriented.",
      executables = [Executable("puclio.py")],
      options = dict(build_exe=buildOptions),
     )

shutil.copyfile("ressources/lib/putio2/putio2.py.save",
                "ressources/lib/putio2/putio2.py")
