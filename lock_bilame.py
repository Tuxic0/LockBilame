'''
Created on 13 mai 2014

@author: Thibaut
'''

from PyDAQmx import *
from PyDAQmx.DAQmxCallBack import *
import numpy as n
from ctypes import WINFUNCTYPE

inp_cor = "cDAQ1Mod1/ai0"#correction feeding to the laser
inp_pd = "cDAQ1Mod1/ai1"#photodiode after filtering cavity
inp_err = "cDAQ1Mod1/ai2"#pdh of the cavity
N_INPUT=3
inputs = inp_cor+','+inp_pd+','+inp_err

out_lock = "cDAQ1Mod4/ao0"#tension to feed the bilames's motor
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
    if cor<MAX_OUT:
        cor=-MAX_OUT+0.1
    DAQmxWriteAnalogF64(taskHandle_out,1,1,10.0,DAQmx_Val_GroupByChannel,n.array(cor),None,None)

def lock_that_bitch(taskHandle,everyNsamplesEventType, nSamples, callbackData_ptr):
    read = int32()
    DAQmxReadAnalogF64(taskHandle,nSamples,10.0,DAQmx_Val_GroupByChannel,data,N_INPUT*nSamples,byref(read),None)
    cor = data.mean()
    cor = get_cor(cor, get_callbackdata_from_id(callbackData_ptr).value )
    apply_cor(cor)
    return 0

cb_lock_that_bitch = DAQmxEveryNSamplesEventCallbackPtr(lock_that_bitch)

if __name__ == '__main__':
    g = c_float(2.)
    id_gain = create_callbackdata_id(g)
    taskHandle = TaskHandle()
    taskHandle_out = TaskHandle()
    try:
        DAQmxCreateTask("",byref(taskHandle))
        DAQmxCreateTask("",byref(taskHandle_out))
        DAQmxCreateAIVoltageChan(taskHandle,inputs,"",DAQmx_Val_Cfg_Default,-10.0,10.0,DAQmx_Val_Volts,None)
        DAQmxCreateAOVoltageChan(taskHandle_out,out_lock,"",-10.0,10.0,DAQmx_Val_Volts,None)
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