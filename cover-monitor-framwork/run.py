import sys
try:
    import threading as _threading
except ImportError:
    import dummy_threading as _threading
from utils.misc import load_object
from utils.setting import Settings
from case import Case
import cPickle as pickle
from optparse import OptionParser
import os

class Framwork(object):
    """docstring for framwork"""
    def __init__(self, arg):
        super(Framwork, self).__init__()
        self.settings = arg
        self.work_queue = {}
        self.components={}
        self.strategies = []
        self.input_data= {}
        self.base_data = {}
        self.output_data = {}


    def _load_component(self):
        coms = self.settings.get("COMPONENTS")
        for com,attrs in coms.items():
            comcls = load_object(com)
            self.components[comcls.name]= comcls(self.settings,self.input_data)

    def _run_component(self):
        for com in self.components.values():
            com.start()
        for com in self.components.values():
            com.join()
            #self.base_data[com.name] = com.result



    def _load_strategy(self):
        coms = self.settings.get("STRATEGIES")
        for com,attrs in coms.items():
            comcls = load_object(com)
            self.strategies.append(comcls(self.settings))

    def _run_strategy(self):
        for strategy in self.strategies:
            strategy.run(self.input_data)


    def _init_data(self):
        input_file = self.settings.get("INPUT_FILE")
        schema = self.settings.get("SCHEMA",None)

        if input_file:
            handle = open(input_file,"r")
        else:
            handle = sys.stdin
        i = 0
        self.input_data = []
        for line in handle:
            self.input_data.append(Case(self.settings,line))
        handle.close()
        return True

    def dump(self):
        jobdir = self.settings.get("JOBDIR","./data")
        fname = os.path.join(jobdir,"dump.raw")
        f=open(fname,"wb")
        pickle.dump(self.input_data,f)
        f.close()        
        pass
    def load(self):
        jobdir = self.settings.get("JOBDIR","./data")
        fname = os.path.join(jobdir,"dump.raw")
        f=open(fname,"r")
        self.input_data = pickle.load(f)
        f.close()        
        pass
    def run(self):
        if not self._init_data():
            return False
        resume = self.settings.get("RESUME")
        self._load_component()
        self._load_strategy()
        resume = True
        if resume :
            self.load()
        else:
            self._run_component()
            self.dump()
        self._run_strategy()
        for case in self.input_data:
            print case


def main(setting):

    fr = Framwork(setting)
    fr.run()

    #print setting.get("COMPONENTS")   

if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option("-i", "--file", dest="file",
                      help="input FILE", metavar="FILE")
    parser.add_option("-q", "--quiet",
                      action="store_false", dest="verbose", default=True,
                      help="don't print status messages to stdout")

    (options, args) = parser.parse_args()
    setting = Settings()
    setting.setmodule("settings")
    setting.set("INPUT_FILE",options.file)

    main(setting)

