from pysgpp_swig import *
import sys
# disable extensions in Python 3.x as relative
# imports need to be converted first
if sys.version_info.major < 3: import extensions
