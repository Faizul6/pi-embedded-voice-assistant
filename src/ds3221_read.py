from smbus2 import SMBus

RTC_ADDR = 0x68
bus = SMBus(1)

def bcd_to_dec(bcd):
  return (bcd//16*10) + (bcd %16)

def read_time():
  data = bus.read_i2c_block_data(RTC_ADDR,0x00, 3)
  seconds = bcd_to_dec(data[0] & 0x7F)
  minutes = bcd_to_dec(data[1])
  hours = bcd_to_dec(data[2] &0x3F)
  return hours,minutes,seconds


h,m,s = read_time()
print(f"Time: {h:02d}: {m:02d}: {s:02d}")


