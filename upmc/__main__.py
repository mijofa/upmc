import sys
import os.path
sys.path.append(os.path.split(os.path.split(__file__)[0])[0])
import upmc
print sys.argv
upmc.main(sys.argv)
