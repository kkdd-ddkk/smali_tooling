
import os


class chdir (object):
    def __init__ (self, dir):
        self.dir = dir    
        self.olddir = os.getcwd()
    
    def __enter__(self):  os.chdir(self.dir)
    def __exit__ (self ,type, value, traceback): os.chdir(self.olddir)