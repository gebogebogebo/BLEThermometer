def to_date_time(data):

    tmp = data[0:2]
    yyyy = int.from_bytes(tmp,'little')

    mm = int(data[2])
    dd = int(data[3])
    hh = int(data[4])
    min = int(data[5])
    ss = int(data[6])

    strdate_time=str(yyyy)+"/"+str(mm)+"/"+str(dd)+" "+str(hh)+":"+str(min)+":"+str(ss)
    return strdate_time

# 測定日時を求める

# 2020/5/3 10:5:23
date_time = to_date_time(b'\xe4\x07\x05\x03\x0a\x05\x17')
print("date_time = " + date_time)

# 2020/5/2 10:40:19 
date_time = to_date_time(b'\xe4\x07\x05\x02\x0a\x28\x13')
print("date_time = " + date_time)
