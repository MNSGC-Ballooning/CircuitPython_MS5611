import board
import digitalio
import time
import busio
import MS.adafruit_MS5611 as adafruit_MS5611

i2c = busio.I2C(board.SCL, board.SDA)
while not i2c.try_lock():
    pass
MS5611_ADDRESS = i2c.scan()[0]

led = digitalio.DigitalInOut(board.D13)
led.direction = digitalio.Direction.OUTPUT

altimeter = adafruit_MS5611.MS5611(MS5611_ADDRESS, i2c)

while True:
    print("Temperature (C): " + str(altimeter.readTemperature()))
    print("Pressure (Pa): " + str(altimeter.readPressure()))
    print("Alitimeter (m): " + str(altimeter.getAltitude()))
    led.value = True
    time.sleep(0.3)
    led.value = False
    time.sleep(0.3)