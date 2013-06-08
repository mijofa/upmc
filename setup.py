#!/usr/bin/python

import urllib2
url = urllib2.urlopen("http://git.videolan.org/?p=vlc/bindings/python.git;a=blob_plain;f=generated/vlc.py;hb=HEAD")
data = url.read()
url.close()
vlc_file = open("vlc.py", 'r+')
if data != vlc_file.read():
  vlc_file.seek(0)
  vlc_file = open("vlc.py", 'w')
  vlc_file.write(data)
  vlc_file.flush()
  vlc_file.close()

from distutils.core import setup
setup(name = 'upmc',
      version = '1.0',
      py_modules = ['vlc'],
      packages = ['upmc', 'upmc/players'],
      scripts = ['bin/upmc'],
      )
