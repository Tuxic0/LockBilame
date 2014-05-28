'''
Created on 13 mai 2014

@author: Thibaut
'''

from lock_daq import *
import numpy as np
import scipy.signal as sign
import sys, getopt
from PyQt4 import QtCore, QtGui
from math import sqrt,pi
from time import sleep
from send_mail import threaded_send_mail
import send_mail.cfg as cfgm

#See https://code.google.com/p/guidata/source/browse/guidata/__init__.py
#from guidata import qapplication as __qapplication
#_APP = __qapplication()


class LockBilameCOM(QtGui.QWidget, object):
    def __init__(self, gain=50. , n_sample=5000, acq_time=1., cut=1., test=False, pd_max=1.4, pdh_max=0.4, is_send_mail=True):
        super(LockBilameCOM, self).__init__()
        self._createUI(gain, n_sample, acq_time, cut, pd_max, pdh_max)
        
        self.acq_time=acq_time
        self.gain=gain
        self.n_sample=n_sample
        self.cut=cut
        self.pd_max=pd_max
        self.pdh_max=pdh_max
        self.bilame=Bilame(test=test,min_val=-5, max_val=5)
        self.watch=WatchedData(test=test)
        self.sleep_time=1.
        self.is_send_mail=is_send_mail
#        if self.is_send_mail:
#            self.send_mail=threaded_send_mail(cfgm.TO, cfgm.FROM, cfgm.SUB, cfgm.TEXT)
        self.timer = QtCore.QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.lock_that_bitch)

    def _createUI(self, gain, n_sample, acq_time, cut, pd_max, pdh_max):
        self.label_lock = QtGui.QLabel('Lock Bilame')
        
        self.button_start = QtGui.QPushButton("Start")
        self.button_start.clicked.connect(self.button_start_clicked)
        
        self.button_stop = QtGui.QPushButton("Stop")
        self.button_stop.clicked.connect(self.button_stop_clicked)
        
        self.button_reset = QtGui.QPushButton("Reset")
        self.button_reset.clicked.connect(self.button_reset_clicked)
        
        self.acq_time_label = QtGui.QLabel('Acq time (s)')
        self.acq_time_box = QtGui.QDoubleSpinBox() 
        self.acq_time_box.setMaximum(int(1e2))
        self.acq_time_box.setValue(acq_time)
        
        self.n_sample_label = QtGui.QLabel('Number of samples')
        self.n_sample_box = QtGui.QSpinBox() 
        self.n_sample_box.setMaximum(int(1e4))
        self.n_sample_box.setValue(n_sample)
        
        self.gain_label = QtGui.QLabel('gain')
        self.gain_box=QtGui.QDoubleSpinBox()
        self.gain_box.setMaximum(100)
        self.gain_box.setMinimum(-100)
        self.gain_box.setValue(gain)
        
        self.cut_label = QtGui.QLabel('Cut-off frequency')
        self.cut_box=QtGui.QDoubleSpinBox()
        self.cut_box.setSingleStep(0.25)
        self.cut_box.setMaximum(100)
        self.cut_box.setMinimum(0)
        self.cut_box.setValue(cut)
        
        self.pd_max_label = QtGui.QLabel('Pd intensity')
        self.pd_max_box=QtGui.QDoubleSpinBox()
        self.pd_max_box.setSingleStep(0.1)
        self.pd_max_box.setMaximum(10)
        self.pd_max_box.setMinimum(0)
        self.pd_max_box.setValue(pd_max)
        
        self.pdh_max_label = QtGui.QLabel('PDH intensity')
        self.pdh_max_box=QtGui.QDoubleSpinBox()
        self.pdh_max_box.setSingleStep(0.1)
        self.pdh_max_box.setMaximum(10)
        self.pdh_max_box.setMinimum(0)
        self.pdh_max_box.setValue(pdh_max)
        
        self.is_send_mail_checkbox = QtGui.QCheckBox("send mail")
        self.is_send_mail_checkbox.stateChanged.connect(self.check_send_mail)
        
        self.hlay1 = QtGui.QHBoxLayout()
        self.hlay1.addWidget(self.label_lock)
        self.hlay1.addStretch(1)
        self.hlay1.addWidget(self.button_start)
        self.hlay1.addWidget(self.button_stop)
        self.hlay1.addWidget(self.button_reset)
        
        self.hlay2 = QtGui.QHBoxLayout()
        self.hlay2.addWidget(self.gain_label)
        self.hlay2.addWidget(self.gain_box)
        self.hlay2.addStretch(1)
        self.hlay2.addWidget(self.cut_label)
        self.hlay2.addWidget(self.cut_box)
        
        self.hlay3 = QtGui.QHBoxLayout()
        self.hlay3.addWidget(self.acq_time_label)
        self.hlay3.addWidget(self.acq_time_box)
        self.hlay3.addStretch(1)
        self.hlay3.addWidget(self.n_sample_label)
        self.hlay3.addWidget(self.n_sample_box)
        
        self.hlay4 = QtGui.QHBoxLayout()
        self.hlay4.addWidget(self.pd_max_label)
        self.hlay4.addWidget(self.pd_max_box)
        self.hlay4.addStretch(1)
        self.hlay4.addWidget(self.pdh_max_label)
        self.hlay4.addWidget(self.pdh_max_box)
        
        self.hlay5 = QtGui.QHBoxLayout()
        self.hlay5.addWidget(self.is_send_mail_checkbox)
        
        self.v_lay = QtGui.QVBoxLayout()
        self.v_lay.addLayout(self.hlay1)
        self.v_lay.addLayout(self.hlay2)
        self.v_lay.addLayout(self.hlay3)
        self.v_lay.addLayout(self.hlay4)
        self.v_lay.addLayout(self.hlay5)
        
        self.setLayout(self.v_lay)
        self.setWindowTitle("Lock Bilame")
        
        self.show()
        
    @property
    def gain(self):
        return self.gain_box.value()
    
    @gain.setter
    def gain(self, val):
        val=float(val)
        return self.gain_box.setValue(val)
    
    @property
    def cut(self):
        return self.cut_box.value()
    
    @cut.setter
    def cut(self, val):
        val=float(val)
        return self.cut_box.setValue(val)
    
    @property
    def acq_time(self):
        return self.acq_time_box.value()
    
    @acq_time.setter
    def acq_time(self, val):
        val=float(val)
        return self.acq_time_box.setValue(val)
    
    @property
    def n_sample(self):
        return self.n_sample_box.value()
    
    @n_sample.setter
    def n_sample(self, val):
        val=float(val)
        return self.n_sample_box.setValue(val)
    
    @property
    def pd_max(self):
        return self.pd_max_box.value()
    
    @pd_max.setter
    def pd_max(self, val):
        return self.pd_max_box.setValue(val)
    
    @property
    def pdh_max(self):
        return self.pdh_max_box.value()
    
    @pdh_max.setter
    def pdh_max(self, val):
        return self.pdh_max_box.setValue(val)
    
    @property
    def is_send_mail(self):
        return bool(self.is_send_mail_checkbox.checkState())

    @is_send_mail.setter
    def is_send_mail(self, val):
        self.is_send_mail_checkbox.setCheckState(2*val)
        
    def check_send_mail(self):
        if self.is_send_mail:
            try:
                self.send_mail
            except AttributeError:
                self.send_mail=threaded_send_mail(cfgm.TO, cfgm.FROM, cfgm.SUB, cfgm.TEXT)
    
    def button_start_clicked(self):
        self.lock_that_bitch()
        self.timer.setInterval(self.sleep_time)
        self.timer.start()
    
    def button_stop_clicked(self):
        self.timer.stop()
    
    def button_reset_clicked(self):
        pass
        
    def lock_that_bitch(self):
        self.take_data()
        print "data taken"
        if self.is_locked():
            cor=self.get_cor()
            print "cor:%g"%(cor)
            self.apply_cor(cor)
            self.timer.start()
            return 0
        else:
            print "not locked"
            return 1

    def take_data(self):
        data=self.watch.readNsamples(self.n_sample, self.n_sample/self.acq_time, 2*self.acq_time)
        self.pdh=data[:,2]
        self.pd=data[:,1]
        self.err=data[:,0]
        
    def is_locked(self,debug=False):
        try:
            pdh = abs(self.pdh.mean())
        except AttributeError:
            self.take_data()
            pdh = abs(self.pdh.mean())
        except:
            raise
        pd = abs(self.pd.mean())
        pdh_rms=sqrt(self.pdh.var())
        pd_rms=sqrt(self.pd.var())
        print "pd:%g pd_rms:%g pdh:%g pdh_rms:%g"%(pd, pd_rms, pdh, pdh_rms)
        if debug:
            print "pd >(self.pd_max/2.):%s" %(pd >(self.pd_max/2.))
            print "(pdh<self.pdh_max/10.):%s" %((pdh<self.pdh_max/10.))
            print "(pd_rms<pd/30.):%s" %((pd_rms<pd/30.))
#            print "(pdh_rms<pdh/10.):%s" %((pdh_rms<pdh/10.))
        if ((pd >(self.pd_max/2.)and(pdh<self.pdh_max/10.))and(pd_rms<pd/30.) ):#and(pdh_rms<pdh/10.) ):
            return True
        else:
            if self.is_send_mail:
                self.send_mail.ev_wait_order.set()
            return False

    def get_cor(self):
        err=self.err.mean()
        cor=err*self.gain
        return cor

    def apply_cor(self, cor):
        time=5./self.cut
        freq=20*self.cut
        n_pt=time*freq
        wfm=gaussian_wfm(n_pt)
        wfm=cor*wfm
        self.bilame.apply_voltage_curve(wfm, freq, t_out=2*time)
 
def gaussian_wfm(n_pt):
    n_pt=int(n_pt)
    sigma = n_pt/5.
    moy=n_pt/2.
    wfm = np.array(range(n_pt),dtype=float64)
    wfm=wfm-moy
    wfm = np.exp( -1*(wfm)**2/2./sigma**2 )
    wfm=wfm/sigma/sqrt(2*pi)
    wfm[-int(sigma/2.):]=np.linspace(wfm[-int(sigma/2.)], 0, int(sigma/2.))
    wfm[0:int(sigma/2.)]=np.linspace(0,wfm[int(sigma/2.)],int(sigma/2.))
    return wfm
    
#def is_locked(data, v_pd, v_pdh ):
#    pdh = abs(data[:,2].mean())
#    pd = abs(data[:,1].mean())
#    print "pd:%g pdh:%g"%(pd, pdh)
#    if ((pd >(i_pd/2.)and(pdh<i_pdh/2.))or(pd_rms>pd/5.)or(pdh_rms>pdh/5.) ):
#        return 1
#    else:
#        return 0

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
    wfm = np.hstack( (frm*np.ones(begin), to*np.ones(end)) )
    wfm = butter_lowpass_filter(wfm, cut, fs, order=1)
    return wfm

def derivative(wfm):
    d = np.gradient(wfm)
    d[0]=0
    d[-1]=0
    return d

    

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

#_APP.exec_()

if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:],"fg:t:",["test", "gain=","time="])
    except getopt.GetoptError:
        print 'lock_bilame.py [-f <test>]  -g <gain> -t <time>'
        sys.exit(2)
    test=False
    for opt, arg in opts:
        if opt in ("-g", "--gain"):
            gain=float(arg)
        if opt in ("-t", "--time"):
            time_lock=float(arg)
        if opt in ("-f", "--test"):
            test=True
    gain=gain*time_lock
    print test
    b = Bilame(test=test)
    w = WatchedData(test=test)
    while True:
        try:
            pass
        except KeyboardInterrupt:
            print "YOLO"
    sys.exit(0)

  

