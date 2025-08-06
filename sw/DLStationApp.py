import sys
try:
    import smbus
    import DLStationLEDControl
except:
    pass
    
import time
import struct
from PyQt5 import QtGui, QtCore, uic
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QGridLayout, QWidget , QVBoxLayout


'''
Add to /etc/xdg/lxsession/LXDE-pi/autostart

@xcompmgr -C -c -o 0.5 -l -19 -t -10 -r 14 -f -O 0.05 -I 0.05

For Transparency to work on Raspberry Pi
'''
class DLStationApp(QMainWindow ):
    
    def __init__(self):
        QMainWindow .__init__(self)
        self.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.X11BypassWindowManagerHint
        )

        self.setWindowTitle("DLStation")
        #self.setGeometry(
        #    QtWidgets.QStyle.alignedRect(
        #        QtCore.Qt.LeftToRight, QtCore.Qt.AlignRight,
        #        QtCore.QSize(140, 60),
        #        QtWidgets.qApp.desktop().screenGeometry()
        #))
        self.setGeometry(QtWidgets.qApp.desktop().screenGeometry())        

        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)        
        self.setStyleSheet("background-color:rgba(255, 255, 255, 2)")
        #self.setStyleSheet("background-color:transparent")
        self.setCursor(QtCore.Qt.BlankCursor)  
        
        centralWidget = QWidget();
        self.setCentralWidget(centralWidget);
        layout = QGridLayout()
        centralWidget.setLayout(layout);

        layout.setColumnStretch(0, 1)
        layout.setRowStretch(2, 1)
        
        self.voltageLabel = QtWidgets.QLabel('Light green')
        self.voltageLabel.setText(F"Voltage: {99.99:0.2f} V")
        self.currentLabel = QtWidgets.QLabel('Light green')
        self.currentLabel.setText(F"Current: {99.99:0.2f} A")
        
        layout.addWidget(self.voltageLabel,0,1)
        layout.addWidget(self.currentLabel,1,1)
        
        self.timer = QtCore.QTimer(self)
        self.timer.setSingleShot(False)
        self.timer.setInterval(1000) # in milliseconds, so 1000 = 1 seconds
        self.timer.timeout.connect(self.updateChargeState)
        self.timer.start()
    
        self.initPowerMonitor()
        try:
            self.LEDControl = DLStationLEDControl.DLStationLEDControl()
        except:
            self.LEDControl = None
        
    def initPowerMonitor(self):
        '''Configure the power meter IC'''
        self.PWR_MONITOR_ADDRESS = 0x48      #7 bit address (will be left shifted to add the read write bit)
        DEVICE_CONFIG_REG = 0x0
        DEVICE_SHUNT_REG = 0x5
        
        SHUNT_CAL_HI = 0x01
        SHUNT_CAL_LO = 0x9A
                
        CONFIG_REGISTER_HIGH = 0b00001111
        CONFIG_REGISTER_LOW  = 0b00100111
        
        
        # Here Read out ADC and display voltage
        # sudo apt-get install python-smbus
        # https://pypi.org/project/smbus-cffi/
        # https://www.ti.com/lit/ds/symlink/ina232.pdf
        #
        
        # Init Bus and configure device with correct data.
        try:
            self.bus = smbus.SMBus(1)    # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)
            self.bus.write_i2c_block_data(self.PWR_MONITOR_ADDRESS,DEVICE_CONFIG_REG,[CONFIG_REGISTER_HIGH, CONFIG_REGISTER_LOW])
            self.bus.write_i2c_block_data(self.PWR_MONITOR_ADDRESS,DEVICE_SHUNT_REG,[SHUNT_CAL_HI, SHUNT_CAL_LO])
        except:
            self.bus = None
        
    def updateChargeState(self):
        ''' Updater function to read out the Power Meter IC and update the labels'''
        BUS_VOLTAGE_REG = 0x2
        CURRENT_LSB = 0.0005 # A/bit
        POWER_LSB = 0.016 # W/bit
        VOLTAGE_LSB = 0.0016 #V/bit
        SHUNT_LSB = 0.0000025 #V/bit
        
        data = []
        if(self.bus):
            for i in range(0,3):
                data = data + self.bus.read_i2c_block_data(self.PWR_MONITOR_ADDRESS, BUS_VOLTAGE_REG+i, 2)
            voltage_pu, current_pu, power_pu = struct.unpack(">HHh", bytes(data))
            voltage = voltage_pu*VOLTAGE_LSB
            current = current_pu*CURRENT_LSB
            power = power_pu*POWER_LSB
        
        else:
            voltage = 99.99
            current = 99.99
            power = 999.99
        
        #print("Voltage: %f" % voltage)
        #print("Current: %f" % current)
        #print("Power:   %f" % power)
        self.voltageLabel.setText("Voltage: %0.2f V"%voltage)
        self.currentLabel.setText("Current: %0.2f A"%current)

    def mousePressEvent(self, event):
        ''' Touch event to cycle through colors, when top right corner is clicked'''
        if(event.x()> (QtWidgets.qApp.desktop().screenGeometry().width() -140) and
            event.y()< 60):
            if(self.LEDControl):
                self.LEDControl.loopPWMBrightness()
            else:
                self.close()
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mywindow = DLStationApp()
    mywindow.show()
    app.exec_()
