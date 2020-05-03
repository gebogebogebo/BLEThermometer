import to_float_from_11073_32bit_float as tofl
import to_date_time as todt
import sendline as line

#
#line.send_notify("token xxx","a","b")

# 測定値を求める
# 36.8
temp = tofl.to_float_from_11073_32bit_float(b'\x70\x01\x00\xff')
print("temp = " + str(temp) + " C")

# 37.2
temp = tofl.to_float_from_11073_32bit_float(b'\x74\x01\x00\xff')
print("temp = " + str(temp) + " C")

# 37.1
temp = tofl.to_float_from_11073_32bit_float(b'\x73\x01\x00\xff')
print("temp = " + str(temp) + " C")

# 2020/5/3 10:5:23
date_time = todt.to_date_time(b'\xe4\x07\x05\x03\x0a\x05\x17')
print("date_time = " + date_time)

# 2020/5/2 10:40:19 
date_time = todt.to_date_time(b'\xe4\x07\x05\x02\x0a\x28\x13')
print("date_time = " + date_time)
