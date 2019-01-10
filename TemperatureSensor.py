import smbus


class TemperatureSensor:
    
    def __init__(self):
        self.bus = smbus.SMBus(1)
        self.config = [0x00, 0x00]
        self.bus.write_i2c_block_data(0x18, 0x01, self.config)
        self.bus.write_byte_data(0x18, 0x08, 0x03)
        self.data = self.bus.read_i2c_block_data(0x18, 0x05, 2)
    
    #returns double representing the temperature in Fahrenheit
    def getTemperatureInFahrenheit(self):
        self.updateData()
        ctemp = ((self.data[0] & 0x1F) * 256) + self.data[1]
        
        if ctemp > 4095 :
            ctemp -= 8192
        
        return ctemp * 0.0625 * 1.8 + 32
    
    def updateData(self):
        self.data = self.bus.read_i2c_block_data(0x18, 0x05, 2)
    
    #returns double representing the temperature in Celsius
    def getTemperatureInCelsius(self):
        self.updateData()
        ctemp = ((self.data[0] & 0x1F) * 256) + self.data[1]
        
        if ctemp > 4095 :
            ctemp -= 8192
        
        return ctemp * 0.0625
