import os
PYTHONPATH = os.environ['PYTHONPATH'].split(os.pathsep)
print("The PYTHONPATH is:", PYTHONPATH)
PATH = os.environ['PATH'].split(os.pathsep)
print("The PATH is:", PATH)
