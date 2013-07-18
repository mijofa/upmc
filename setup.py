#!/usr/bin/python

import os.path
import urllib2
try:
  url = urllib2.urlopen("http://git.videolan.org/?p=vlc/bindings/python.git;a=blob_plain;f=generated/vlc.py;hb=HEAD")
  data = url.read()
  url.close()
  updatevlc = False
  if updatevlc != ""  and os.path.exists("vlc.py") and os.path.isfile("vlc.py"):
    vlc_file = open("vlc.py", 'r+')
    if data != vlc_file.read():
      updatevlc = True
  else:
    vlc_file = open("vlc.py", 'w')
    updatevlc = True
  if updatevlc == True:
    vlc_file.seek(0)
    vlc_file.write(data)
    vlc_file.flush()
    vlc_file.close()
except Exception as e:
  print "Can not update vlc.py:", e

from distutils.core import setup
setup(name = "upmc",
      version = "1.0",
      py_modules = ["vlc"],
      package_dir = {"upmc": "src"},
      packages = ["upmc", "upmc.players"],
      package_data = {"upmc": ["data/background.png", "data/dvd.jpg"]},
      scripts = ["bin/upmc"],
      )
