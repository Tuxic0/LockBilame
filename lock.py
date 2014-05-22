'''
Created on 13 mai 2014

@author: Thibaut
'''

from lock_daq import *
import numpy as np
import scipy.signal as sign
import sys, getopt
from PyQt4 import QtCore, QtGui

class LockBilameCOM(QtGui.QWidget, object):
    def __init__(self, gain=1. , n=1000, t=10., cut=2., fake=None):
        super(LockBilameCOM, self).__init__()
        

#        self.acq_time=t
#        self.gain=gain
#        self.n_sample=n
#        self.cut=cut
#        self.bilame=Bilame(test=fake)
#        self.watch=WatchedData(test=fake)
        
#        self.timer = QtCore.QTimer()
#        self.timer.setSingleShot(True)
#        self.timer.timeout.connect(self.lock_that_bitch)
#        
#        self.label_lock = QtGui.QLabel('Lock Bilame')
#        
#        self.button_start = QtGui.QPushButton("Start")
#        self.button_start.clicked.connect(self.button_start_clicked)
#        
#        self.button_stop = QtGui.QPushButton("Stop")
#        self.button_stop.clicked.connect(self.button_stop_clicked)
#        
#        self.button_reset = QtGui.QPushButton("Reset")
#        self.button_reset.clicked.connect(self.button_reset_clicked)
#        
#        self.label_acq_time = QtGui.QLabel('Acq time (s)')
#        self.sleep_time_lock_box = QtGui.QSpinBox() 
#        self.sleep_time_lock_box.setMaximum(int(1e2))
#        self.sleep_time_lock_box.setValue(self.acq_time)
#        
#        self.label_acq_time = QtGui.QLabel('Number of samples)')
#        self.sleep_time_lock_box = QtGui.QSpinBox() 
#        self.sleep_time_lock_box.setMaximum(int(1e4))
#        self.sleep_time_lock_box.setValue(self.n_sample)
#        
#        self.gain_label = QtGui.QLabel('gain')
#        self.gain_box=QtGui.QSpinBox()
#        self.gain_box.setMaximum(100)
#        self.gain_box.setMinimum(-100)
#        self.gain_box.setValue(self.gain)
#        
#        self.gain_label = QtGui.QLabel('Cut-off')
#        self.gain_box=QtGui.QSpinBox()
#        self.gain_box.setMaximum(100)
#        self.gain_box.setMinimum(0)
#        self.gain_box.setValue(self.cut)
#        
#        self.hlay1 = QtGui.QHBoxLayout()
#        self.hlay1.addWidget(self.label_lock)
#        self.hlay1.addStretch(1)
#        self.hlay1.addWidget(self.button_start)
#        self.hlay1.addWidget(self.button_stop)
#        self.hlay1.addWidget(self.button_reset)
#        
#        self.v_lay = QtGui.QVBoxLayout()
#        self.v_lay.addLayout(self.hlay1)
#        
#        self.setLayout(self.v_lay)
#        self.setWindowTitle("Lock Bilame")
#        
        self.show()
#        
#        def button_start_clicked(self):
#            self.lock_that_bitch(self.gain, self.n_sample, self.acq_time)
#            self.timer.setInterval(0.1)
#            self.timer.start()
#        
#        def button_stop_clicked(self):
#            self.timer.stop()
#        
#        def button_reset(self):
#            pass
#            
#        def lock_that_bitch():
#            pass
#            print "err:%g"%(cor)
#            if abs(cor) > THRSLD:
#                cor = get_cor(cor, get_callbackdata_from_id(callbackData_ptr).value )
#                if is_locked(data2):
#                    apply_cor(cor,taskHandle_out)
#            print "cor:%g applied"%(cor)
#        else:
#            print "not locked"
#            return 1
#    else:
#        if is_locked(data2):
#            print "err below threshold, correction not applied"
#        else:
#            print "not locked"
#            return 1
#    return 0



def get_cor(err, gain):
    return err*gain


def apply_cor(cor,  prev_cor=None, filter=None):
    if filter is None:
        bilame.apply_voltage(cor)
    
def is_locked(data, v_pd, v_pdh ):
    pdh = abs(data[:,2].mean())
    pd = abs(data[:,1].mean())
    print "pd:%g pdh:%g"%(pd, pdh)
    if ((pd >(i_pd/2.)and(pdh<i_pdh/2.))or(pd_rms>pd/5.)or(pdh_rms>pdh/5.) ):
        return 1
    else:
        return 0

def butter_lowpass(cut, fs, order=2):
    nyq = 0.5 * fs
    cut = cut / nyq
    b, a = sign.butter(order, [cut], btype='lowpass')
    return b, a

def butter_lowpass_filter(data, cut, fs, order=2):
    b, a = butter_lowpass(cut, fs, order=order)
    y = sign.lfilter(b, a, data)
    return y

def filter_low_pass(npt, t, cut, frm, to):
    fs = npt/float(t)
    begin=int(npt*5/100.)
    end=npt-begin
    wfm = np.hstack( frm*np.ones(begin), to*np.ones(end) )
    wfm = butter_lowpass_filter(wfm, cut, fs, order=2)
    return wfm

def lock_that_bitch(bilame, n, t):
    
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

#cb_lock_that_bitch = DAQmxEveryNSamplesEventCallbackPtr(lock_that_bitch)

if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:],"fg:t:",["fake", "gain=","time="])
    except getopt.GetoptError:
        print 'lock_bilame.py [-f <fake>]  -g <gain> -t <time>'
        sys.exit(2)
    fake=False
    for opt, arg in opts:
        if opt in ("-g", "--gain"):
            gain=float(arg)
        if opt in ("-t", "--time"):
            time_lock=float(arg)
        if opt in ("-f", "--fake"):
            fake=True
    gain=gain*time_lock
    print fake
    b = Bilame(test=fake)
    w = WatchedData(test=fake)
    while True:
        try:
            pass
        except KeyboardInterrupt:
            print "YOLO"
    sys.exit(0)

        

