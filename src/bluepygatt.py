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