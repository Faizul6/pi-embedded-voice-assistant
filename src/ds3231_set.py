from smbus2 import SMBus
from datetime import datetime

RTC_ADDR = 0x68
bus= SMBus(1)

def dec_to_bcd(dec):
  return (dec//10*16) + (dec%10)

def set_time():
  now = datetime.now()
  bus.write_byte_data(RTC_ADDR, 0x00, dec_to_bcd(now.second))
  bus.write_byte_data(RTC_ADDR, 0x01, dec_to_bcd(now.minute))
  bus.write_byte_data(RTC_ADDR, 0x02, dec_to_bcd(now.hour))
  print(f"RTC set to {now.hour:02d}: {now.minute:02d}:{now.second:02d}")


set_time()

