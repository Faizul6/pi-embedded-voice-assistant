from smbus2  import SMBus
I2C_ADDR = 0x3c
CMD = 0x00
DATA = 0x40

bus = SMBus(1)

def cmd(byte):
  bus.write_byte_data (I2C_ADDR, CMD, byte)

def set_pixel_byte(page, col, byte_value):

  cmd(0xB0 + page)
  cmd (0x00 | (col & 0x0F))
  cmd(0x10 | (col>>4))
  bus.write_byte_data(I2C_ADDR,DATA,byte_value)

set_pixel_byte(page = 0, col = 0, byte_value = 0b00000001)

print ("Pixel written at page 0, col 0")
