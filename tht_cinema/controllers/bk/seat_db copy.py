# -*- coding: utf-8 -*-
from datetime import datetime
import pickle
import os


class db_seat():
    filename = ''
    outfile = ''
    def __init__(self, filename):
        self.filename = os.path.dirname(__file__)+'/temp/'+str(filename)
        try:
            with open(self.filename, "rb") as f:
                foo = pickle.load(f)
        except Exception:
            foo = {'lc':''}
            with open(self.filename, "wb") as f:
                pickle.dump(foo, f)
                self.outfile = f
                f.close()
            
    def open(self):
        self.outfile = open(self.filename,'wb')
    def close(self,values):
        self.outfile = open(self.filename,'wb')
        pickle.dump(values,self.outfile)
        self.outfile.close()
    def dump(self, values):
        self.outfile = open(self.filename,'wb')
        pickle.dump(values,self.outfile)
        self.outfile.close()
    def load(self):
        result = pickle.load(open(self.filename,'rb'))
        return result

# db_lc = db_seat('db_lc')


# db_lc = {
#     'timestamp': str(datetime.today())
# }

# db_pos = {}