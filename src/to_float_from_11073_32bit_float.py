import numpy as np

def tofloat_from11073_32bit_float(data):
    tmp = int.from_bytes(data,'little')
    uint32val = np.array([tmp],dtype=np.uint32)

    # 仮数部を求める(0-24bit)
    tmp = bin(uint32val[0] & 0xffffff)
    mantissa = int(tmp,0)
    if mantissa >= 0x007FFFEE and mantissa <= 0x00800002:
        # error
        return 0

    # 指数部を求める(25-32bit)
    tmp = int(data[3])
    tmp2 = np.array([tmp],dtype=np.byte)
    exponent = int(tmp2[0])

    # 実数を計算
    ret = mantissa * pow(10,exponent)
    return ret

# 測定値を求める
temp = tofloat_from11073_32bit_float(b'\x73\x01\x00\xff')
# -> 36.1

strtemp = str(temp)
print("temp = " + strtemp + " C")