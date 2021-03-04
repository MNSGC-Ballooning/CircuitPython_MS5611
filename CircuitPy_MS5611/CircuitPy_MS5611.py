import board
import digitalio
import time
import busio

MS5611_CMD_RESET = 0x1E # binary rep:
MS5611_CMD_CONV_D1 = 0x40
MS5611_CMD_CONV_D2 = 0x50
MS5611_CMD_ADC_READ = 0x00
MS5611_CMD_PROM_READ = 0xA2 # this will be iterated for different addresses. P10

ct = 0
fc = [0,0,0,0,0,60]
oRes = 0x00

class MS5611:
    def __init__(self, MS5611_ADDRESS, i2cPort):
        self.MS5611_ADDRESS = MS5611_ADDRESS
        self.i2cPort = i2cPort
        self.oRes = oRes
        self.reset()
        self.setOversampling(oRes)
        time.sleep(0.1)
        self.readPROM()

    def setOversampling(self,ouRes):
        global cT
        if(ouRes == 0x08):
            ct = 10
        if(ouRes == 0x06):
            ct = 5
        if(ouRes == 0x04):
            ct = 3
        if(ouRes == 0x02):
            ct = 2
        if(ouRes == 0x00):
            ct = 1

    def reset(self):
        self.i2cPort.writeto(self.MS5611_ADDRESS, bytearray([MS5611_CMD_RESET]))

    def readPROM(self):
        global fc
        for i in range(0,6):
            fc[i] = self.readRegister16(MS5611_CMD_PROM_READ + i*2)
            time.sleep(.1)

    def readRegister16(self,register):
        myBuf = bytearray(2)
        self.i2cPort.writeto(self.MS5611_ADDRESS, bytearray([register]))
        self.i2cPort.readfrom_into(self.MS5611_ADDRESS, myBuf)
        x = bytes(myBuf)
        val = (x[0] << 8) + x[1]
        return val

    def readRegister24(self,register):
        myBuf = bytearray(3)
        self.i2cPort.writeto(self.MS5611_ADDRESS, bytearray([register]))
        self.i2cPort.readfrom_into(self.MS5611_ADDRESS, myBuf)
        x = bytes(myBuf)
        val = (x[0] << 16) + (x[1] << 8) + x[0]
        return val

    def readRawTemperature(self):
        self.i2cPort.writeto(self.MS5611_ADDRESS, bytearray([MS5611_CMD_CONV_D2 + self.oRes]))
        time.sleep(ct/1000)
        return self.readRegister24(MS5611_CMD_ADC_READ)

    def readRawPressure(self):
        self.i2cPort.writeto(self.MS5611_ADDRESS, bytearray([MS5611_CMD_CONV_D1 + self.oRes]))
        time.sleep(ct/1000)
        return self.readRegister24(MS5611_CMD_ADC_READ)

    def readTemperature(self):
        D2 = self.readRawTemperature()
        dT = (D2 - fc[4]*256)/1000
        Temp = 2.000 + dT*fc[5]/8388608
        Temp2 = 0

        if(Temp<=2):
            Temp2 = dT*dT/2147.483648

        Temp = Temp - Temp2
        return Temp*10

    def readPressure(self):
        D1 = self.readRawPressure()
        D2 = self.readRawTemperature()
        dT = (D2 - fc[4]*256)/1000
        OFF = (fc[1] * 65.536 + fc[3] * dT / 128)
        SENS = (fc[0] * 32.768 + fc[2] * dT / 256)

        P = (D1*SENS / 2097152 - OFF) / 32.768
        #P = 1
        return P


    def getAltitude(self):
        P = self.readPressure()
        seaLevelP = 101325.0 # Pa
        return 44330.0 * (1.0 - pow(P / seaLevelP,0.1902949))
