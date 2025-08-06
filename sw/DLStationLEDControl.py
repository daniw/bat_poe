from rpi_hardware_pwm import HardwarePWM
import math 

class DLStationLEDControl:
    '''This Module uses the Hardware PWM Instances. These must be activated using the hardware overlay: 
        
        dtoverlay=pwm-2chan,pin=12,func=4,pin2=13,func2=4
        
        Add this to /boot/firmware/config.txt or /boot/config.txt
        
    '''  
    
    # PWM Parameters
    FREQ = 1000  # Frequency in Hz
    
    # MAX PWM
    MAX_DUTY = 50
    
    def __init__(self):           
        self._pwmFront = HardwarePWM(pwm_channel=0, hz=self.FREQ, chip=0)
        self._pwmBack = HardwarePWM(pwm_channel=1, hz=self.FREQ, chip=0)
        
        self._PwmStateBack = 0
        self._PwmStateFront = 0
        
        self._pwmFront.start(0)
        self._pwmBack.start(0)
    
    def __del__(self):
        self._pwmFront.stop()      
        self._pwmBack.stop()      
    
    @property    
    def PwmStateBack(self):
        return self._PwmStateBack
    
    @PwmStateBack.setter
    def PwmStateBack(self, value):
        self._PwmStateBack = value if value <=self.MAX_DUTY else 0
        self._pwmBack.change_duty_cycle(self._PwmStateBack)

    @property    
    def PwmStateFront(self):
        return self._PwmStateFront

    @PwmStateFront.setter
    def PwmStateFront(self, value):
        self._PwmStateFront = value if value <=self.MAX_DUTY else 0
        self._pwmFront.change_duty_cycle(self._PwmStateFront)
    
    
    def loopPWMBrightness(self):
        '''Toggle PWM with 25% Steps (of maxduty)'''
        self.PwmStateFront = self.PwmStateFront + math.ceil(self.MAX_DUTY/4)
        self.PwmStateBack = self.PwmStateBack + math.ceil(self.MAX_DUTY/4)
        
        
if __name__ == '__main__':
    
    LED = DLStationLEDControl()
    while 1:
        input()
        LED.loopPWMBrightness()