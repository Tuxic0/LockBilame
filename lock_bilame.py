'''
Created on 13 mai 2014

@author: Thibaut
'''

from PyDAQmx import *
from PyDAQmx.DAQmxCallBack import *
import numpy as n
from ctypes import WINFUNCTYPE

DAQ='cDAQ9184-COM'
MOD_inp='Mod1'
MOD_out='Mod4'
inp_cor = DAQ+MOD_inp+"/ai0"#correction feeding to the laser
inp_pd = DAQ+MOD_inp+"/ai1"#photodiode after filtering cavity
inp_err = DAQ+MOD_inp+"/ai2"#pdh of the cavity
N_INPUT=3
inputs = inp_cor+','+inp_pd+','+inp_err

out_lock = DAQ+MOD_out+"/ao0"#tension to feed the bilames's motor
MAX_OUT = 10

time_lock = 5.
n_pt = 100
freq_smpl = n_pt/time_lock

data = n.zeros((N_INPUT*n_pt,), dtype=n.float64)

def get_cor(err, gain):
    return err*gain

def apply_cor(cor):
    if cor>MAX_OUT:
        cor=MAX_OUT-0.1
    if cor<-MAX_OUT:
        cor=-MAX_OUT+0.1
    DAQmxWriteAnalogF64(taskHandle_out,1,1,10.0,DAQmx_Val_GroupByChannel,n.array(cor,dtype=float64),None,None)

def lock_that_bitch(taskHandle,everyNsamplesEventType, nSamples, callbackData_ptr):
    read = int32()
    DAQmxReadAnalogF64(taskHandle,nSamples,10.0,DAQmx_Val_GroupByScanNumber,data,N_INPUT*nSamples,byref(read),None)
    data2=data.reshape( (-1, N_INPUT) )
    cor = data[:,0].mean()
    print data2
    print "err:%g"%(cor)
    cor = get_cor(cor, get_callbackdata_from_id(callbackData_ptr).value )
    print "cor:%g"%(cor)
    apply_cor(cor)
    print "cor applied"
    return 0

cb_lock_that_bitch = DAQmxEveryNSamplesEventCallbackPtr(lock_that_bitch)

if __name__ == '__main__':
    g = c_float(1.)
    id_gain = create_callbackdata_id(g)
    taskHandle = TaskHandle()
    taskHandle_out = TaskHandle()
    try:
        DAQmxCreateTask("",byref(taskHandle))
        DAQmxCreateTask("",byref(taskHandle_out))
        DAQmxCreateAIVoltageChan(taskHandle,inputs,"",DAQmx_Val_Cfg_Default,-MAX_OUT,MAX_OUT,DAQmx_Val_Volts,None)
        DAQmxCreateAOVoltageChan(taskHandle_out,out_lock,"",-MAX_OUT,MAX_OUT,DAQmx_Val_Volts,None)
        DAQmxCfgSampClkTiming(taskHandle,"",freq_smpl,DAQmx_Val_Rising,DAQmx_Val_ContSamps,N_INPUT*n_pt)
        DAQmxRegisterEveryNSamplesEvent(taskHandle,DAQmx_Val_Acquired_Into_Buffer,n_pt,0,cb_lock_that_bitch,id_gain)
        DAQmxStartTask(taskHandle)
        DAQmxStartTask(taskHandle_out)
        
        # DAQmx Read Code
        
        raw_input("Acquiring samples continuously. Press Enter to interrupt")
    except DAQError as err:
        print "DAQmx Error: %s"%err
    finally:
        if taskHandle:
            # DAQmx Stop Code
            DAQmxStopTask(taskHandle)
            DAQmxClearTask(taskHandle)
            DAQmxStopTask(taskHandle_out)
            DAQmxClearTask(taskHandle_out)