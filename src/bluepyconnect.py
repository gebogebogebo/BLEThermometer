from bluepy import btle

BLE_ADDRESS="18:93:D7:76:C9:B8"

peripheral = btle.Peripheral()
peripheral.connect(BLE_ADDRESS)

for service in peripheral.getServices():
    print(f'UUID：{service.uuid}')
    for characteristic in service.getCharacteristics():
        print(f'  UUID：{characteristic.uuid}')
        print(f'    ハンドル：{characteristic.getHandle()}')
        print(f'    プロパティ：{characteristic.propertiesToString()}')
