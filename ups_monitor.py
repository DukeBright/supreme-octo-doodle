import smbus
import time

I2C_ADDR = 0x36
bus = smbus.SMBus(1)

def read_battery_voltage():
    data = bus.read_word_data(I2C_ADDR, 2)
    voltage = ((data & 0xff) << 8 | (data >> 8)) * 1.25 / 1000 / 16
    return voltage

def read_battery_percent():
    data = bus.read_word_data(I2C_ADDR, 4)
    percent = ((data & 0xff) << 8 | (data >> 8)) / 256
    return percent

while True:
    print(f"Battery Voltage: {read_battery_voltage():.2f} V")
    print(f"Battery Percent: {read_battery_percent():.1f} %")
    time.sleep(10);