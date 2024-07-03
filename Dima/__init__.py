import os
import sys


# added directories
for directory in map(os.path.abspath, filter(os.path.isdir, os.listdir(os.path.dirname(os.path.dirname(__file__))))):
	if directory not in sys.path:
		sys.path.append(directory)
