import sys
import os.path
sys.path.append(os.path.split(os.path.split(__file__)[0])[0])
#print sys.path
import upmc
upmc.main(sys.argv)
