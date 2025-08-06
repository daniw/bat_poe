import struct
import time
try:
    import smbus
except:
    pass
    

class MP3924Interface:

    MP3924_ADDRESS = 0b0100000
    
    def __init__(self):
        # Init Bus and configure device with correct data.
        try:
            self.bus = smbus.SMBus(1)    # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)
        except:
            self.bus = None
        pass
  
    def readState(self):
        STATUS_REGISTER_CLEAR_OFFSET = 0x1
        POWER_SOURCE_STATUS_REG_1 = 0x20 + STATUS_REGISTER_CLEAR_OFFSET
        data=self.bus.read_i2c_block_data(self.MP3924_ADDRESS, POWER_SOURCE_STATUS_REG_1, 1)
        
        # Decode Power Source Status 1
        for i in range(0,4):
            if(data[0] & (1<<(i+4))):
                print(F"ERROR: MOSFET {i} failure detected!")
        
        if(data[0] & (1<<(0))):
            print("ERROR: VCC Undervoltage occured")                
        if(data[0] & (1<<(1))):
            print("ERROR: Over Temperature occured")                
        if(data[0] & (1<<(2))):
            print("ERROR: VIN Overvoltage >65V occured")                
        if(data[0] & (1<<(3))):
            print("ERROR: VIN Undervoltage <29.5V occured")
        
        # Decode Power Source Status 2   
        POWER_SOURCE_STATUS_REG_2 = 0x22 + STATUS_REGISTER_CLEAR_OFFSET
        data=self.bus.read_i2c_block_data(self.MP3924_ADDRESS, POWER_SOURCE_STATUS_REG_2, 1)         
        if(data[0] & (1<<(0))):
            print("ERROR: PMAX Exceeded")
        if(data[0] & (1<<(1))):
            print("VIN OK!")

        # Decode DET/CLS Complete
        DETCLS_COMPLETE_STATUS_REG = 0x24 + STATUS_REGISTER_CLEAR_OFFSET
        data=self.bus.read_i2c_block_data(self.MP3924_ADDRESS, DETCLS_COMPLETE_STATUS_REG, 1)
        DET_CLS_RESULT1 = 0x26
        data=data+self.bus.read_i2c_block_data(self.MP3924_ADDRESS, DET_CLS_RESULT1,4)
        LEGACY_DETECT_RESULT_REG = 0x35
        legacy_data =self.bus.read_i2c_block_data(self.MP3924_ADDRESS, LEGACY_DETECT_RESULT_REG,2) 
        
        DETECTION_RESULT = ["Detection has not completed (default after a power-on reset)",
                           "The port is shorted (VIN - OUT < 1.5V)",
                           "CDET too high (exceeds 5μF)",
                           "RDET is too low (below 19kΩ)",
                           "Detection is valid (19kΩ < RDET < 26.5kΩ)",
                           "RDET is too high (exceeds 26.5kΩ)",
                           "The port is open (<15μA load current)",
                           "Low impedance to PGND (OUT - PGND < 2V)"]
        CLASSIFICATION_RESULT = ["Classification is not done",
                                 "Classified as Class 1",
                                 "Classified as Class 2",
                                 "Classified as Class 3",
                                 "Classified as Class 4",
                                 "Classified as Class 5",
                                 "Classified as Class 0",
                                 "Over-current (OC) condition",
                                 "The first and secondary class results do not match"]
        TWO_EVENT_STRING = ["", "2EV "]
        
        LEGACY_DETECTION_RESULT = ["", #No Legacy Detection
                                   " Valid (5μF < PD input capacitor < 100μF)",
                                   " Unable to discharge the PD input capacitance to 2.4V",
                                   " The first measurement exceeds the 18.5V maximum voltage",
                                   " The second measurement exceeds the 18.5V maximum voltage",
                                   " The difference between the measured voltages is below 0.5V"]
        PORT_CHANGED_STRING = ["", "*"]
        
        print("Detection and Classification")
        for i in range(0,4):
            print(F"    Port {i}:", end="")
            print(F"{PORT_CHANGED_STRING[(data[0]>>i)&0x1]}", end="")
            print(F" {DETECTION_RESULT[data[i+1]&0x7]}")
            
            print(F"            {PORT_CHANGED_STRING[(data[0]>>(i+4))&0x1]}", end="")
            print(F"{TWO_EVENT_STRING[(data[i+1]>>3)&0x1]}{CLASSIFICATION_RESULT[data[i+1]>>4]}", end="")
            print(LEGACY_DETECTION_RESULT[(legacy_data[i//2]>>(4*(i%2)))&0x4])
            
        # Power Status (0x2A)
        POWER_STATUS_REG = 0x2A
        data=self.bus.read_i2c_block_data(self.MP3924_ADDRESS, POWER_STATUS_REG, 3)
        PG_STRING = ["No PG", "PG"]
        PEN_STRING = ["No PEN", "PEN"]
        PORT_CHANGED_STRING = ["", "*"]
        print("Power Status")
        for i in range(0,4):
            print(F"    Port {i}: {PEN_STRING[(data[0]>>i)&0x1]}{PORT_CHANGED_STRING[(data[2]>>i)&0x1]}" + 
                   F" {PG_STRING[(data[0]>>(i+4))&0x1]}{PORT_CHANGED_STRING[(data[2]>>(i+4))&0x1]}")
        
        # Overload Status
        OVER_LOAD_STATUS_REG = 0x2D + STATUS_REGISTER_CLEAR_OFFSET
        data=self.bus.read_i2c_block_data(self.MP3924_ADDRESS, OVER_LOAD_STATUS_REG, 1)
        CURRENT_LIMIT_STATUS_REG = 0x2F + STATUS_REGISTER_CLEAR_OFFSET
        data=data + self.bus.read_i2c_block_data(self.MP3924_ADDRESS, CURRENT_LIMIT_STATUS_REG, 1)
        
        STARTUP_FAILURE_STRING = [""," Startup Failure occured."]
        OCUT_STRING = [""," Overcurrent CUT Timer finished."]
        OLIM_STRING = [""," Hardware overcurrent tripped."]
        
        print("Overload Status")
        for i in range(0,4):
            print(F"    Port {i}:", end="")
            print(STARTUP_FAILURE_STRING[(data[0]>>i)&0x1], end="")
            print(OCUT_STRING[(data[0]>>(i+4))&0x1], end="")
            print(OLIM_STRING[(data[1]>>i)&0x1], end="")
            print("")
        
        #Disconnect register
        DISCONNECT_STATUS_REG = 0x32 + STATUS_REGISTER_CLEAR_OFFSET
        data=self.bus.read_i2c_block_data(self.MP3924_ADDRESS, DISCONNECT_STATUS_REG, 1)
        for i in range(0,4):
            if((data[0]>>i)&0x1):
                print(F"Port {i} got disconnected.")

        
        
        
    def readCurrentLimit(self):
        ICUT1_THRESHOLD_REGISTER = 0x13
        data=self.bus.read_i2c_block_data(self.MP3924_ADDRESS, ICUT1_THRESHOLD_REGISTER, 8)
        
        ICUT_VALUES = ["375 mA", "110 mA", "188 mA", "375 mA", "650 mA", "920 mA", "500 mA","625 mA"]
        ILIM_VALUE = ["425 mA", "850 mA"]
        
        for i in range(0,4):
            print(F"I Cut Limit Port {i}: {ICUT_VALUES[data[i]]}")
        for i in range(0,4):
            print(F"I OC Limit Port {i}: {ILIM_VALUE[data[4+i]]}")
        
        
    def readADCValues(self):
        PORT1_CURRENT_REGISTER_LOW = 0x40
        REGISTER_NAMES = ["Current Port 1 %0.2f mA", "Voltage Port 1 %0.2f V", 
                          "Current Port 2 %0.2f mA", "Voltage Port 2 %0.2f V", 
                          "Current Port 3 %0.2f mA", "Voltage Port 3 %0.2f V", 
                          "Current Port 4 %0.2f mA", "Voltage Port 4 %0.2f V",
                          "Input Voltage\t%0.2f V", "Temperature\t%0.2f °C",
                          "Max Power\t%0.2f W"]
                          
        SCALE = [2.4, 0.15,
                 2.4, 0.15,
                 2.4, 0.15,
                 2.4, 0.15,
                 0.15, 0.4,
                 0.4]
                 
        OFFSET =[-10, 0,
                 -10, 0,
                 -10, 0,
                 -10, 0,
                 0, -40.0,
                 0]
        data=self.bus.read_i2c_block_data(self.MP3924_ADDRESS, PORT1_CURRENT_REGISTER_LOW, 23)
        
        value=[]
        for i in range(0,11):
            data1, data2=struct.unpack("BB",bytes(data[2*i:2*i+2]))
            value.append((data1+(data2<<1))*SCALE[i]+OFFSET[i])
        
        for i in range(1,8,2):
            value[i] = value[8]-value[i]
        
        print("ADC\t\tCurrent\t\tVoltage")
        for i in range(0,4):
            print(F"    Port {i}:\t{value[2*i]:0.2f} mA\t{value[2*i+1]:0.2f} V")
        
        
        for i in range(8,11):
            print(REGISTER_NAMES[i]%value[i])
            
        
    def readDieID(self):
        DIE_ID_REGISTER = 0x60
        data=self.bus.read_i2c_block_data(self.MP3924_ADDRESS, DIE_ID_REGISTER, 1)
            
        print("DIE ID:\n FAB: %X \n REV: %X.%X\n Vendor: %x"%(data[0]>>6, (data[0]>>4) & 0x3, (data[0]>>2) & 0x3, (data[0]) & 0x3))
        
        
if __name__ == "__main__":
    poe = MP3924Interface()
    poe.readDieID()
    poe.readCurrentLimit()
    for i in range(0,100):
        poe.readState()
        poe.readADCValues()
        time.sleep(5)
        