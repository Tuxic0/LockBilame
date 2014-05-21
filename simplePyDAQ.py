'''
Created on 20 mai 2014

@author: Thibaut
'''

from PyDAQmx import *
import cfg
import numpy as np


class DAQDevice(object):
    def __init__(self,chassis,mod,*chans):
        self.chassis=str(chassis)
        self.mod=str(mod)
        self._get_phy_chans(*chans)
        
    def _get_phy_chans(self, *chans):
        phy_chans=""
        n_chans=0
        for c in chans:
            phy_chans+=self.chassis+self.mod+'/'+str(c)+','
            n_chans+=1
        phy_chans.strip(',')
        self.phy_chans=phy_chans
        self.n_chans=n_chans

class Task(object):
    def __init__(self,dev, **kwargs):
        self.dev=dev
        self.taskHandle=TaskHandle()
        def_args = {"name":cfg.DEF_NAME, 
                    "min_val":cfg.DEF_MIN, "max_val":cfg.DEF_Max,
                    "term_cfg":cfg.DEF_TERM_CFG}
        for k,v in def_args.iteritems():
            if k in kwargs:
                self.__dict__[k]=kwargs[k]
            else:
                self.__dict__[k]=v
        DAQmxCreateTask("",byref(self.taskHandle))
        
    def start(self):
        DAQmxStartTask(self.taskHandle)
        
    def stop(self):
        DAQmxStopTask(self.taskHandle)
    
    def clear(self):
        DAQmxClearTask(self.taskHandle)
        
    def stop_clear(self):
        DAQmxStopTask(self.taskHandle)
        DAQmxClearTask(self.taskHandle)

        
class Acq(Task, object):
    '''
    kwargs: buffer, name, freq_smpl, acq_mode, min_val, max_val, src_clk
    '''
    def __init__(self,dev,**kwargs):
        super(Acq, self).__init__(dev, **kwargs)
        def_args = {"buffer":cfg.DEF_BUFF, "freq_smpl":cfg.DEF_FS, "acq_mode":cfg.DEF_ACQ, 
                    "clk":cfg.DEF_CLK, "act_edge":cfg.DEF_EDGE}
        for k,v in def_args.iteritems():
            if k in kwargs:
                self.__dict__[k]=kwargs[k]
            else:
                self.__dict__[k]=v

class voltOutput(Acq, object):
    def __init__(self, dev, **kwargs):
        super(voltOutput, self).__init__(dev, **kwargs)
        self.createAOVoltage()
        
    def createAOVoltage(self):
        DAQmxCreateAOVoltageChan(self.taskHandle,self.dev.phy_chans,self.name,self.min_val,self.max_val,DAQmx_Val_Volts,None)

    def apply_voltage(self, volt, t_out=1):
        DAQmxWriteAnalogF64(self.taskHandle,1,1,10.0,DAQmx_Val_GroupByChannel, np.array(volt,dtype=float64),None,None)
        self.stop()
    
    def apply_voltage_curve(self, curve, t_out=1):
        size=curve.size/self.dev.phy_chans
        DAQmxWriteAnalogF64(self.taskHandle,size,1,10.0,DAQmx_Val_GroupByChannel, curve,None,None)
        self.stop()

class voltInput(Acq, object):
    def __init__(self, dev, **kwargs):
        super(voltInput, self).__init__(dev, **kwargs)
        self.createAIVoltage()
            
    def cfgSamplClk(self):
        DAQmxCfgSampClkTiming(self.taskHandle,self.clk,self.freq_smpl,self.act_edge,self.acq_mode,self.buffer)
        
    def createAIVoltage(self):
        DAQmxCreateAIVoltageChan(self.taskHandle,self.dev.phy_chans,self.name,self.term_cfg,self.min_val,self.max_val,DAQmx_Val_Volts,None)
    
#    def registerEveryNSamplesEvent(n_pt,cb_f,cb_opt,opt=0):
#        DAQmxRegisterEveryNSamplesEvent(self.taskHandle,DAQmx_Val_Acquired_Into_Buffer,n_pt,opt,cb_f,cb_opt)
    
    def readNsamples(self,n, freq_smpl=None, t_out=-1):
        if freq_smpl is not None:
            self.freq_smpl = freq_smpl
        self.acq_mode = DAQmx_Val_FiniteSamps
        self.buffer = n
        self.cfgSamplClk()
        data=data = np.zeros((self.dev.n_chans*n,), dtype=np.float64)
        read=int32()
        self.start()
        DAQmxReadAnalogF64(self.taskHandle, -1, t_out, DAQmx_Val_GroupByScanNumber, data,self.dev.n_chans*n,byref(read), None)
        self.stop()
        data2=data.reshape( (-1, self.dev.n_chans) )
        return data2

class Bilame(voltOutput, object):
    def __init__(self, test=None, **kwargs):
        if test is None:
            dev=DAQDevice(cfg.DEF_CHASSIS,cfg.DEF_MOD,cfg.DEF_CHAN)
        elif test is True:
            dev=DAQDevice(cfg.DEF_CHASSIS_TEST,cfg.DEF_MOD_TEST,cfg.DEF_CHAN_TEST)
        else:
            dev=test
        super(Bilame, self).__init__(dev, **kwargs)


        