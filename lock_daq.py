'''
Created on 22 mai 2014

@author: Thibaut
'''

from simplePyDAQ import *
from simplePyDAQ.cfg import *

class Bilame(voltOutput, object):
    def __init__(self, test=False, **kwargs):
        if test is False:
            dev=DAQDevice(cfg.DEF_CHASSIS,cfg.DEF_MOD,*cfg.DEF_CHAN)
        elif test is True:
            dev=DAQDevice(cfg.DEF_CHASSIS_TEST,cfg.DEF_MOD_TEST,*cfg.DEF_CHAN_TEST)
        else:
            dev=test
        super(Bilame, self).__init__(dev, **kwargs)

class WatchedData(voltInput, object):
        def __init__(self, test=False, **kwargs):
            if test is False:
                dev=DAQDevice(cfg.DEF_CHASSIS_IN,cfg.DEF_MOD_IN,*cfg.DEF_CHAN_IN)
            elif test is True:
                dev=DAQDevice(cfg.DEF_CHASSIS_IN_TEST,cfg.DEF_MOD_IN_TEST,*cfg.DEF_CHAN_IN_TEST)
            else:
                dev=test
            super(WatchedData, self).__init__(dev, **kwargs)