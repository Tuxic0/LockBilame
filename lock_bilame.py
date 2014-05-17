'''
Created on 13 mai 2014

@author: Thibaut
'''

from PyDAQmx import *
from PyDAQmx.DAQmxCallBack import *
import numpy as n

DAQ='cDAQ9184-COM'
#DAQ='CDAQ1'
MOD_inp='Mod1'
MOD_out='Mod4'
inp_cor = DAQ+MOD_inp+"/ai0"#correction feeding to the laser
inp_pd = DAQ+MOD_inp+"/ai1"#photodiode after filtering cavity
inp_err = DAQ+MOD_inp+"/ai2"#pdh of the cavity
N_INPUT=3
inputs = inp_cor+','+inp_pd+','+inp_err

out_lock = DAQ+MOD_out+"/ao0"#tension to feed the bilames's motor
MAX_OUT = 10 #max output tension
MAX_IN=2.

time_lock = 5. #refresh time in second
n_pt = 100 #number of points that will be averaged together to determine dc values
gain=1.

intensity = 1.
intensity_pdh = 0.1
OFFSET=0.
THRSLD=OFFSET/3.

freq_smpl = n_pt/time_lock
data = n.zeros((N_INPUT*n_pt,), dtype=n.float64)

class Bilame():
    def __init__(self):
        self.taskHandle_out = TaskHandle()
        try:
            DAQmxCreateTask("",byref(self.taskHandle_out))
            DAQmxCreateAOVoltageChan(self.taskHandle_out,out_lock,"",-MAX_OUT,MAX_OUT,DAQmx_Val_Volts,None)
            DAQmxStartTask(self.taskHandle_out)
        except DAQError as err:
            print "DAQmx Error: %s"%err
            
    def apply_v(self,volt):
        try:
            apply_voltage(volt,self.taskHandle_out)
        except DAQError as err:
            print "DAQmx Error: %s"%err

def get_cor(err, gain):
    return err*gain

def apply_voltage(volt, taskHandle):
    DAQmxWriteAnalogF64(taskHandle,1,1,10.0,DAQmx_Val_GroupByChannel,n.array(volt,dtype=float64),None,None)

def apply_cor(cor,TaskHandle):
    if cor>MAX_OUT:
        cor=MAX_OUT-0.1
    if cor<-MAX_OUT:
        cor=-MAX_OUT+0.1
    apply_voltage(cor,taskHandle)
    
def is_locked(data):
    pdh = abs(data[:,2].mean())
    pd = abs(data[:,1].mean())
    print "pd:%g pdh:%g"%(pd, pdh)
    if (pd > (intensity/2.)) and ((pdh < (intensity_pdh/2.))):
        return 1
    else:
        return 0

def curve_low_pass():
    pass

def lock_that_bitch(taskHandle,everyNsamplesEventType, nSamples, callbackData_ptr):
    read = int32()
    DAQmxReadAnalogF64(taskHandle,nSamples,10.0,DAQmx_Val_GroupByScanNumber,data,N_INPUT*nSamples,byref(read),None)
    data2=data.reshape( (-1, N_INPUT) )
    cor = data2[:,0].mean()-OFFSET
    print "err:%g"%(cor)
    if abs(cor) > THRSLD:
        cor = get_cor(cor, get_callbackdata_from_id(callbackData_ptr).value )
        if is_locked(data2):
            apply_cor(cor,taskHandle_out)
            print "cor:%g applied"%(cor)
        else:
            print "not locked"
            return 1
    else:
        if is_locked(data2):
            print "err below threshold, correction not applied"
        else:
            print "not locked"
            return 1
    return 0

cb_lock_that_bitch = DAQmxEveryNSamplesEventCallbackPtr(lock_that_bitch)

if __name__ == '__main__':
    gain=gain*time_lock
    g = c_float(gain)
    id_gain = create_callbackdata_id(g)
    taskHandle = TaskHandle()
    taskHandle_out = TaskHandle()
    try:
        DAQmxCreateTask("",byref(taskHandle))
        DAQmxCreateTask("",byref(taskHandle_out))
        DAQmxCreateAIVoltageChan(taskHandle,inputs,"",DAQmx_Val_Cfg_Default,-MAX_IN,MAX_IN,DAQmx_Val_Volts,None)
        DAQmxCreateAOVoltageChan(taskHandle_out,out_lock,"",-MAX_OUT,MAX_OUT,DAQmx_Val_Volts,None)
        DAQmxCfgSampClkTiming(taskHandle,"",freq_smpl,DAQmx_Val_Rising,DAQmx_Val_ContSamps,N_INPUT*n_pt)
        DAQmxRegisterEveryNSamplesEvent(taskHandle,DAQmx_Val_Acquired_Into_Buffer,n_pt,0,cb_lock_that_bitch,id_gain)
        DAQmxStartTask(taskHandle)
        DAQmxStartTask(taskHandle_out)
        
        # DAQmx Read Code
        print ' '
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
