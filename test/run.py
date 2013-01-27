import sys
import os

from os import path
exec_name = sys.argv[0]
exec_dir = path.dirname(exec_name)
strongchicken_path = path.join(exec_dir, "../src/")
sys.path.append(strongchicken_path)

from uncertainties import *
from assets import *
from core import *

import unittest
unittest.main()
