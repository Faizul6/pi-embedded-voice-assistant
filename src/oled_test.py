from smbus2 import SMBus
import time

I2C_ADDR = 0x3C
CMD = 0x00
DATA = 0x40

bus = SMBus(1)

def cmd(byte):
  bus.write_byte_data(I2C_ADDR, CMD, byte)

init_sequence = [
  0xAE,
  0xD5,0x80,
  0xA8,0x3F,
  0xD3,0x00,
  0x40,
  0x8D,0x14,
  0x20,0x00,
  0xA1,
  0xC8,
  0xDA,0x12,
  0x81,0xCF,
  0xD9,0xF1,
  0xDB,0x40,
  0xA4,
  0xA6,
  0xAF,
]

for byte in init_sequence:
  cmd(byte)

print("Init sequence sent - screen should be blank but powered on")

def clear_display():
  for page in range(8):
    bus.write_byte_data(I2C_ADDR, CMD,0xB0 +page)
    bus.write_byte_data(I2C_ADDR, CMD, 0x00)
    bus.write_byte_data(I2C_ADDR, CMD, 0x10)
    for col in range(128):
        bus.write_byte_data(I2C_ADDR, DATA, 0x00)

clear_display()
print("Display cleared")
