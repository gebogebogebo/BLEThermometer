from bluepy import btle
scanner = btle.Scanner(0) 
devices = scanner.scan(3.0) 
for device in devices:
  print(f'BLE Address：{device.addr}')
  for (adTypeCode, description, valueText) in device.getScanData():
    print(f'- {description}：{valueText}')
