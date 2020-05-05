# はじめに

[BLE体温計からラズパイでLINEに体温を通知する #1](https://qiita.com/gebo/items/67aca91d07e3d7fccc85)の続きです。  
今回はpythonで実装していきます。  
BLEライブラリはbluepyを使います。  

 

# bluepyのインストール

BLEのライブラリは[bluepy](https://github.com/IanHarvey/bluepy)を使います。  
bluepyをインストールします。

```bash
$ sudo apt-get update
$ sudo apt-get -y upgrade
$ sudo apt-get -y install python3-pip libglib2.0-dev
$ sudo pip3 install bluepy
>Successfully installed bluepy-1.3.0

$ reboot
```



# bluepyでいろいろやってみる

bluepyでBLEデバイスとお話しします。  


## アドバタイズパケットのスキャン

まずはアドバタイズパケットのスキャンです。

```python
from bluepy import btle

scanner = btle.Scanner(0) 
devices = scanner.scan(3.0) 
for device in devices:
  print(f'BLE Address：{device.addr}')
  for (adTypeCode, description, valueText) in device.getScanData():
    print(f'- {description}：{valueText}')
```

コードは簡単ですが、トラップがあって、bluepyでスキャンを実行するには**sudo権限が必要**です。権限が足りないと`scanner.scan()`でエラーになります。  

 体温計を**ペアリングモード**にしてからpyを実行ます。

```bash
$ sudo python3 bluepyadv.py
BLE Address：18:93:d7:76:c9:b8
- Flags：05
- Incomplete 16b Services：00001809-0000-1000-8000-00805f9b34fb
- 0x12：5000a000
- Tx Power：00
- Complete Local Name：A&D_UT201BLE_76C9B8
BLE Address：6f:1a:a5:25:58:55
- Flags：06
- Manufacturer：4c001005571cf70bed
```

`BLE Address：18:93:d7:76:c9:b8`のところが体温計デバイスの情報です。ちゃんとスキャンされています。



## 接続してサービス一覧を取得する

体温計と接続してサービス一覧を取得します。  
BLEアドレスはMACアドレスみたいなものなんで、デバイスによって違います。自分のデバイスのBLEアドレスを指定してください。  
私の持っている体温計のBLEアドレスは`18:93:D7:76:C9:B8`です。

```python
from bluepy import btle

BLE_ADDRESS="18:93:D7:76:C9:B8"

peripheral = btle.Peripheral()
peripheral.connect(BLE_ADDRESS)

for service in peripheral.getServices():
    print(f'Service UUID：{service.uuid}')
    for characteristic in service.getCharacteristics():
        print(f'- Characteristic UUID：{characteristic.uuid} , Handle：{hex(characteristic.getHandle())} , Property：{characteristic.propertiesToString()}')
```

体温計で測定して**送信モード**になったらpyを実行します。接続するのでペアリングモードではなく送信モードです。先ほどのようにsudo権限は無くてもOKです。

```bash
$ python3 bluepyconnect.py
Service UUID：00001800-0000-1000-8000-00805f9b34fb
- Characteristic UUID：00002a00-0000-1000-8000-00805f9b34fb , Handle：0x3 , Property：READ 
- Characteristic UUID：00002a01-0000-1000-8000-00805f9b34fb , Handle：0x5 , Property：READ 
- Characteristic UUID：00002a02-0000-1000-8000-00805f9b34fb , Handle：0x7 , Property：READ WRITE 
- Characteristic UUID：00002a03-0000-1000-8000-00805f9b34fb , Handle：0x9 , Property：WRITE 
- Characteristic UUID：00002a04-0000-1000-8000-00805f9b34fb , Handle：0xb , Property：READ 
Service UUID：00001801-0000-1000-8000-00805f9b34fb
- Characteristic UUID：00002a05-0000-1000-8000-00805f9b34fb , Handle：0xe , Property：INDICATE 
Service UUID：00001809-0000-1000-8000-00805f9b34fb
- Characteristic UUID：00002a1c-0000-1000-8000-00805f9b34fb , Handle：0x12 , Property：INDICATE 
- Characteristic UUID：00002a1d-0000-1000-8000-00805f9b34fb , Handle：0x15 , Property：READ 
- Characteristic UUID：00002a08-0000-1000-8000-00805f9b34fb , Handle：0x17 , Property：READ WRITE 
Service UUID：0000180a-0000-1000-8000-00805f9b34fb
- Characteristic UUID：00002a29-0000-1000-8000-00805f9b34fb , Handle：0x1a , Property：READ 
- Characteristic UUID：00002a24-0000-1000-8000-00805f9b34fb , Handle：0x1c , Property：READ 
- Characteristic UUID：00002a25-0000-1000-8000-00805f9b34fb , Handle：0x1e , Property：READ 
- Characteristic UUID：00002a27-0000-1000-8000-00805f9b34fb , Handle：0x20 , Property：READ 
- Characteristic UUID：00002a26-0000-1000-8000-00805f9b34fb , Handle：0x22 , Property：READ 
- Characteristic UUID：00002a28-0000-1000-8000-00805f9b34fb , Handle：0x24 , Property：READ 
- Characteristic UUID：00002a23-0000-1000-8000-00805f9b34fb , Handle：0x26 , Property：READ 
- Characteristic UUID：00002a2a-0000-1000-8000-00805f9b34fb , Handle：0x28 , Property：READ 
Service UUID：0000180f-0000-1000-8000-00805f9b34fb
- Characteristic UUID：00002a19-0000-1000-8000-00805f9b34fb , Handle：0x2b , Property：READ 
Service UUID：233bf000-5a34-1b6d-975c-000d5690abe4
- Characteristic UUID：233bf001-5a34-1b6d-975c-000d5690abe4 , Handle：0x2e , Property：READ WRITE 
```



## 体温計からデータを取得する

測定したデータを受信してみます。

```python
import sys
from bluepy import btle

BLE_ADDRESS="18:93:D7:76:C9:B8"
SERVICE_UUID="00001809-0000-1000-8000-00805f9b34fb"

class MyDelegate(btle.DefaultDelegate):
    def __init__(self):
        btle.DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
        print("Handle = " + hex(cHandle))
        print("- Flags = " + hex(data[0]))
        print("- C1:Temperature Measurement Value(Celsius) = " + hex(data[1])+":"+hex(data[2])+":"+hex(data[3])+":"+hex(data[4]))
        print("- C3:Time Stamp = " + hex(data[5])+":"+hex(data[6])+":"+hex(data[7])+":"+hex(data[8])+":"+hex(data[9])+":"+hex(data[10])+":"+hex(data[11]))

if __name__ == '__main__':
    print("Start")
    print("Connecting Wait...")
    try:
        peripheral = btle.Peripheral()
        peripheral.connect(BLE_ADDRESS)
    except:
        print("connect Error!")
        sys.exit(0)

    print("Connected!")
    peripheral.withDelegate(MyDelegate())

    # Enable Indicate
    peripheral.writeCharacteristic(0x13, b'\x02\x00', True)

    # 通知を待機する
    print("Indicate Wait...")
    try:
        TIMEOUT = 3.0
        while True:
            if peripheral.waitForNotifications(TIMEOUT):
                # handleNotification()が呼び出された
                continue

            # handleNotification()がTIMEOUT秒だけ待っても呼び出されなかった
            print("wait...")
    except:
        # 切断されるとここにくる
        print("except!")

    print("end")
```

`peripheral.withDelegate(MyDelegate())`でイベントハンドラを登録して、`peripheral.writeCharacteristic(0x13, b'\x02\x00', True)`しているところがポイントです。

**ハンドル0x13のキャラクタリスティックに0200を設定するとIndicateが始まる**ということは[前回の説明](https://qiita.com/gebo/items/67aca91d07e3d7fccc85#gatttool)の通りです。データを受信すると`handleNotification()`イベントが発生します。受信したデータがdataに詰まっています。 

**注意**  
0x13というハンドル値はデバイスによって違うかもしれない(未確認)のでgatttoolでハンドル値を確認して自分のデバイスの値を指定してください。

```bash
pi@raspberrypi:~/work/git/BLEThermometer/src $ python3 bluepygatt.py
Start
Connecting Wait...
Connected!
Indicate Wait...
Handle = 0x12
- Flags = 0x6
- C1:Temperature Measurement Value(Celsius) = 0x73:0x1:0x0:0xff
- C3:Time Stamp = 0xe4:0x7:0x5:0x4:0xa:0x7:0x2f
wait...
wait...
except!
end
```

この実行ログで  

- 体温 = 0x73:0x1:0x0:0xff
- タイムスタンプ = xe4:0x7:0x5:0x4:0xa:0x7:0x2f

が取れたということがわかります。



# 受信データのパース

## 測定値のパース
先ほど「体温 = 0x73:0x1:0x0:0xff」ということがわかりましたが、この4byteのデータは**IEEE 11073 32bit float**形式のバイナリです。  
pythonでIEEE 11073 32bit floatのバイナリをfloat型変数に変換する簡単な方法が見つかりませんでした。仕方がないので自作しました。

```python
import numpy as np

def to_float_from_11073_32bit_float(data):
    tmp = int.from_bytes(data,'little')
    uint32val = np.array([tmp],dtype=np.uint32)

    # 仮数部を求める(0-24bit)
    tmp = bin(uint32val[0] & 0xffffff)
    mantissa = int(tmp,0)

    # 指数部を求める(25-32bit)
    tmp = int(data[3])
    tmp2 = np.array([tmp],dtype=np.byte)
    exponent = int(tmp2[0])

    # 実数を計算
    ret = round(mantissa * pow(10,exponent),1)
    return ret

# 37.1
temp = to_float_from_11073_32bit_float(b'\x73\x01\x00\xff')
print("temp = " + str(temp) + " C")
```

実行します。

```bash
$ python3 to_float_from_11073_32bit_float.py 
temp = 37.1 C
```

`0x73:0x1:0x0:0xff` が **37.1** となりました。ベリーグッドです。



## タイムスタンプのパース
タイムスタンプは7byteです。[Temperature Measurement C3 の形式](https://qiita.com/gebo/items/67aca91d07e3d7fccc85#temperature-measurement)です。
```python
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

# 2020/5/4 10:07:47
date_time = to_date_time(b'\xe4\x07\x05\x04\x0a\x07\x2f')
print("date_time = " + date_time)
```

実行します。

```bash
$ python3 to_date_time.py 
date_time = 2020/5/4 10:7:47
```



ここまでで前回gatttoolでやったことと同じことをbulepyでできるようになりました。



# LINEで通知する

そういえば、測定結果をLINEで通知する必要がありました。LINE通知はLINE Notifyを使えば簡単です。

以下の記事を参考にしてLINE通知を実装します。

- [ラズパイとMAMORIOとLINEで出退勤を記録する仕組みを作る](https://qiita.com/gebo/items/4fa5a3d0866bce6cfae2)

このソースに書いてあるTokenは無効なので発行して有効なものを使いましょう。

```python
import requests

# LINE通知する
def send_notify(access_token,comment):
        if( len(access_token) <= 0 ):
                return

        url = "https://notify-api.line.me/api/notify"
        headers = {'Authorization': 'Bearer ' + access_token}
        message = comment
        payload = {'message': message}
        print(message)
        requests.post(url, headers=headers, params=payload,)

send_notify("token xxx","comment")
```

実行します。

```bash
$ python3 sendline.py 
comment
```

キタ。

<img src="/Users/suzuki/Documents/GitHub/BLEThermometer/doc/img/IMG_6943.png" alt="IMG_6943" style="zoom:33%;" />



# 本番

ここからが本番です。ここまで調べてきたことを順番にやっていけばいいだけなので簡単です。

<img src="/Users/suzuki/Documents/GitHub/BLEThermometer/doc/img/memo_04.png" alt="memo_04" style="zoom:50%;" />



pythonのソースコード、ちょっと長いです。

```python
# このpyを実行するにはsudo権限が必要です。
# 権限がたりないとscanner.scan()でエラーになります。
from bluepy import btle
import sys
import time
import to_float_from_11073_32bit_float as tofl
import to_date_time as todt
import sendline as line

# define
SERVICE_UUID="00001809-0000-1000-8000-00805f9b34fb"

# global
BLE_ADDRESS="xx:xx:xx:xx:xx:xx"
TOKEN = "this is token"

def scan():
    try:
        scanner = btle.Scanner(0)
        devices = scanner.scan(3.0)

        for device in devices:
            print(f'SCAN BLE_ADDR：{device.addr}')

            if(device.addr.lower()==BLE_ADDRESS.lower()):
                print("Find!")
                return True
    except:
        print("scan Error!")
        return False
    print("---")
    return False

class MyDelegate(btle.DefaultDelegate):
    def __init__(self):
        btle.DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
        print("Indicate Handle = " + hex(cHandle))
        print("Flags = " + hex(data[0]))
        print("C1:Temperature Measurement Value(Celsius) = " + hex(data[1])+":"+hex(data[2])+":"+hex(data[3])+":"+hex(data[4]))
        print("C3:Time Stamp = " + hex(data[5])+":"+hex(data[6])+":"+hex(data[7])+":"+hex(data[8])+":"+hex(data[9])+":"+hex(data[10])+":"+hex(data[11]))

        temp = tofl.to_float_from_11073_32bit_float(data[1:5])
        print("temp = " + str(temp))
        timestamp = todt.to_date_time(data[5:12])
        print("timestamp = " + timestamp)
        line.send_notify(TOKEN,str(temp)+" C "+timestamp)

def main():
    #
    # Scan
    #
    print("<Scan Start>")
    while True:
        scanresult = scan()
        if( scanresult==True):
            break
        time.sleep(3)
    print("Scan End")


    #
    # Connect
    #
    print("Connect Start")
    try:
        peripheral = btle.Peripheral()
        peripheral.connect(BLE_ADDRESS)
    except:
        print("connect Error!")
        sys.exit(0)

    print("Connected!")
    service = peripheral.getServiceByUUID(SERVICE_UUID)
    peripheral.withDelegate(MyDelegate())

    # Enable Indicate
    peripheral.writeCharacteristic(0x0013, b'\x02\x00', True)

    # 通知を待機する
    print("Indicate Wait...")
    try:
        TIMEOUT = 3.0
        while True:
            if peripheral.waitForNotifications(TIMEOUT):
                # handleNotification()が呼び出された
                continue

            # handleNotification()がTIMEOUT秒だけ待っても呼び出されなかった
            print("wait...")
    except:
        print("except!")

    print("<end>")

if __name__ == '__main__':
    print(sys.argv[0])
    #global TOKEN
    TOKEN = sys.argv[1]
    print("token = " + TOKEN)

    #gloval BLE_ADDRESS
    BLE_ADDRESS = sys.argv[2]
    print("BLE device = " + BLE_ADDRESS)

    while True:
        main()
        time.sleep(3)
```

pyを実行するとスキャンが始まるので体温を計測します。計測が完了すると自動的に受信して体温とタイムスタンプ（計測日時）をLINEに通知します。

```bash
$ sudo python3 bluepythermo.py [token] 18:93:D7:76:C9:B8
bluepythermo.py
token = [token]
BLE device = 18:93:D7:76:C9:B8
<Scan Start>
SCAN BLE_ADDR：18:93:d7:76:c9:b8
Find!
Scan End
Connect Start
Connected!
Indicate Wait...
Indicate Handle = 0x12
Flags = 0x6
C1:Temperature Measurement Value(Celsius) = 0x72:0x1:0x0:0xff
C3:Time Stamp = 0xe4:0x7:0x5:0x4:0xa:0x16:0x1c
temp = 37.0
timestamp = 2020/5/4 10:22:28
37.0 C 2020/5/4 10:22:28
wait...
wait...
except!
<end>
```

ちゃんとLINEに通知がきました。

<img src="/Users/suzuki/Documents/GitHub/BLEThermometer/doc/img/IMG_6944.png" alt="IMG_6944" style="zoom:33%;" />

部屋にラズパイを置いてpyを実行させておくとスキャン→LINE通知を繰り返す想定どおりの動作をします。体温計とラズパイを設置すれば遠く離れた人の体温も通知できるので生存確認にも使える。

**これで体温のロギングは間違いない！**



# おつかれさまでした

体温計もラズパイも今なかなか買えないんだよなぁ・・・


