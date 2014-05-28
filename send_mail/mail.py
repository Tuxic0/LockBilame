'''
Created on 27 mai 2014

@author: Thibaut
'''

import PyQt4.QtGui as q
import smtplib as smtp
from email.mime.text import MIMEText
import threading
#    def setUI(self):
#        self.w=q.QWidget()
#        self.line=q.QLineEdit()
#        self.line.setEchoMode(q.QLineEdit.Password)
#        self.ok = q.QPushButton("OK")
#        self.ok.clicked.connect(set_pwd)
#        self.hlay=q.QHBoxLayout()
#        self.vlay=q.QVBoxLayout()
#        self.hlay.addWidget(line)
#        self.hlay.addStretch(1)
#        self.hlay.addWidget(ok)
#        self.vlay.addLayout(hlay)
#        self.w.setLayout(vlay)
#        self.w.setWindowTitle("Enter Password")

def create_mail(to, from_, sub, text):
    msg=MIMEText(text, 'plain')
    msg['To']=to
    msg['From']=from_
    msg['Subject']=sub
    return msg

def get_pwd(text):
    w=q.QWidget()
    pwd,garbage=q.QInputDialog.getText(w,"Send_mail",text,q.QLineEdit.Password)
    w.close()
    return str(pwd)

def get_good_pwd():
    pwd=get_pwd("Enter password")
    pwd2=get_pwd("Confirm password")
    while pwd != pwd2:
        pwd=get_pwd("Passwords don't match")
        pwd2=get_pwd("Confirm password")
    return pwd

def send(msg, pwd):
    s=smtp.SMTP_SSL("smtp.lkb.upmc.fr", 465)
    f=msg["From"]
    t=msg["To"]
    try:
        s.set_debuglevel(True)
        s.ehlo()
        s.login(f.split('@')[0].split('.')[-1], pwd)
        s.sendmail(f, [t], msg.as_string())
    finally:
        s.quit()

def send_mail(msg, pwd=None):
    if pwd is None:
        pwd=get_good_pwd()
    send(msg, pwd)

class threaded_send_mail(threading.Thread, object):
    def __init__(self, to, from_, sub, text):
        super(threaded_send_mail, self).__init__()
        self.to=to
        self.from_=from_
        self.sub=sub
        self.text=text
        self.ev_wait_order=threading.Event()
        self.ev_end=threading.Event()
        self.pwd=get_good_pwd()
        self.start()
    
    def run(self):
        while not self.ev_end.is_set():
            print "creating msg"
            msg=create_mail(self.to, self.from_, self.sub, self.text)
            print "waiting"
            self.ev_wait_order.wait()
            print "going"
            send(msg,self.pwd)
            print "gone"
            self.ev_wait_order.clear()
        print "send_mail stopping"

        



        
        