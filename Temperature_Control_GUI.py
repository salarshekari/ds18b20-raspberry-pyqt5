## This program is written by salar shekari

import sys
from PyQt5.QtWidgets import QApplication,QLineEdit,QDial, QWidget,QLabel,QPushButton,QMainWindow

import RPi.GPIO as gpio
import os
import glob
import time

chillerload8=22

gpio.setmode(gpio.BCM)
gpio.setwarnings(False)

gpio.setup(chillerload8,gpio.OUT)
##
##gpio.output(load1,gpio.HIGH)
##
from PyQt5 import QtCore

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir+'28*')[0]
device_file=device_folder+'/w1_slave'

class Thread_Temp(QtCore.QThread):
    anysig=QtCore.pyqtSignal(list)

    
    def read_temp_raw(self):
        f=open(device_file,'r')
        lines=f.readlines()
        f.close()
        return lines 
#     def read_temp(self):
        

#             return temp_c
    def run(self):
        temp_ci=0
        while (True):
            lines=self.read_temp_raw()
            newlines=self.read_temp_raw()
            while lines[0].strip()[-3:] != 'YES':
                time.sleep(0.2)
                lines=self.read_temp_raw()
                time.sleep(0.1)
                newlines=self.read_temp_raw()
            equals_pos=lines[1].find('t=')
            if equals_pos != -1:
                temp_string=lines[1][equals_pos+2:]
                temp_c=float(temp_string)/1000.0
                temp_ci=int(temp_c)
                
                newtemp_string=newlines[1][equals_pos+2:]
                newtemp_c=float(newtemp_string)/1000.0
                newtemp_ci=int(newtemp_c)
                
                dt=newtemp_ci-temp_ci
                
                temp=[dt,temp_ci]
            
            self.anysig.emit(temp)


class Mainwindow(QWidget):
    def __init__(self):
        QMainWindow.__init__(self)
        super(Mainwindow,self).__init__()
        self.setUI()
        self.Templbl=QLabel("Environment Temperature",self)
        self.Templbl.setStyleSheet("font-size: 16pt;font-weight: bold;background-color: (green+blue+red)")
        self.Templbl.move(90,50)
        self.Templbl.resize(290,40)
        
        self.temptexbox=QLineEdit(self)
        self.temptexbox.move(370,50)
        self.temptexbox.resize(60,40)
        self.temptexbox.setStyleSheet("font-size: 16pt;font-weight: bold;background-color: (green+blue+red)")
        
        self.Templbl=QLabel("UserDefined Temperature \n(desired Temperature)",self)
        self.Templbl.setStyleSheet("font-size: 16pt;font-weight: bold;background-color: (green+blue+red)")
        self.Templbl.move(90,110)
        self.Templbl.resize(400,60)
        
        self.destemptexbox=QLineEdit(self)
        self.destemptexbox.move(370,117)
        self.destemptexbox.resize(60,45)
        self.destemptexbox.setStyleSheet("font-size: 16pt;font-weight: bold;background-color: (green+blue+red)")
        
        
        self.oTemplbl=QLabel("Temperature Offset \n(Hysteresis)",self)
        self.oTemplbl.setStyleSheet("font-size: 16pt;font-weight: bold;background-color: (green+blue+red)")
        self.oTemplbl.move(90,205)
        self.oTemplbl.resize(210,55)
        
        self.offtemptexbox=QLineEdit(self)
        self.offtemptexbox.move(370,205)
        self.offtemptexbox.resize(60,35)
        self.offtemptexbox.setStyleSheet("font-size: 16pt;font-weight: bold;background-color: (green+blue+red)")
        
        self.destmpdial=QDial(self)
        self.destmpdial.setRange(0,40)
        self.destmpdial.setGeometry(450,105,70,70)
        self.destmpdial.setNotchesVisible(True)
        
        self.ofstmpdial=QDial(self)
        self.ofstmpdial.setRange(0,10)
        self.ofstmpdial.setGeometry(450,185,70,70)
        self.ofstmpdial.setNotchesVisible(True)


        self.start_worker()
        
        
        
    def setUI(self):
        self.setGeometry(100,100,800,480);
        self.setWindowTitle("Temperature Management")
        
    def start_worker(self):
        self.thread=Thread_Temp()
        self.thread.start()
        self.thread.anysig.connect(self.my_ff)

    
        
        
    
    def my_ff(self,counter):

        dt=counter[0]
        tempc=counter[1]
        
        
        if (tempc>=self.destmpdial.value() and dt>0 and tempc<tempc+self.ofstmpdial.value()):
            #compressor off
            gpio.output(chillerload8,gpio.HIGH)
        elif(tempc<self.destmpdial.value()):
            #compressor off
            gpio.output(chillerload8,gpio.HIGH)
        elif (tempc==self.destmpdial.value()):
            #compressor off
            gpio.output(chillerload8,gpio.HIGH)
        elif(tempc>self.destmpdial.value()):
            #compressor on
            gpio.output(chillerload8,gpio.LOW)
            
            
            
        self.temptexbox.setText(str(tempc))
        desiredtemp=int(self.destmpdial.value()+0)
        tempoffs=int(self.ofstmpdial.value()+0)
        self.offtemptexbox.setText(str(tempoffs))
        self.destemptexbox.setText(str(desiredtemp))

            
        
        
App = QApplication(sys.argv)
S = Mainwindow()
S.show()
sys.exit(App.exec_())
