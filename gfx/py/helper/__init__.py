import argparse
import os
import sys



def get_graphics_basename():
  name = os.path.splitext(os.path.split(os.path.realpath(sys.argv[0]))[1])[0]
  
  if "_" in name:
    parts = name.split("_")
    number = parts[-1]
    if len(number.strip("0123456789")) == 0: name = "_".join(parts[:-1])
  
  return name



parser = argparse.ArgumentParser(description="Generate graphics for thesis.")
parser.add_argument("--build-dir", default="../../build/gfx",
                    help="Directory in which to store the generated *.tex files.")
args = parser.parse_args()
build_dir = os.path.realpath(args.build_dir)

graphics_basename = get_graphics_basename()



from .basis  import *
from .figure import *
