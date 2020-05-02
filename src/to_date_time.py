def todate_time(data):

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
# e4 07 05 02 0a 28 13
date_time = todate_time(b'\xe4\x07\x05\x02\x0a\x28\x13')
# -> 2020/5/2 10:40:19

print("date_time = " + date_time)
