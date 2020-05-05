# はじめに
コロナ禍ということで、毎日体温測っています。
体温をいちいちメモるのは面倒だっていうのと、GWひたすら暇である、ということで、体温計をハックした試みをしてみました。


:o:以下のことが書いてあります:o:	
- ラズパイでのgatttoolの使い方
- ラズパイでpythonでBLEすること
- GATTのHealth Thermometerサービスのこと

:x:以下のことは書いていません:x:	
- そもそも、BLEとは何か、GATTとは何か、などの基本的なこと



# どんなもの？
**体温を測ったらLINEに通知します。**
<img src="/Users/suzuki/Documents/GitHub/BLEThermometer/doc/img/memo_01.png" alt="memo_01" style="zoom:30%;" />



**体温計→BLE→ラズパイ →WebAPI→LINE→スマホと測定値を送信します。**
<img src="/Users/suzuki/Documents/GitHub/BLEThermometer/doc/img/memo_02.png" alt="memo_02" style="zoom:40%;" />



**体温計とスマホが物理的に離れていても通知が飛ぶので、別の場所にいる人や実家のおばあちゃんの体温をリモートで把握することなんかもできるかと思います。**
<img src="/Users/suzuki/Documents/GitHub/BLEThermometer/doc/img/memo_03.png" alt="memo_03" style="zoom:40%;" />


# 環境

- ラズパイ:[Raspberry Pi 3 Model b+](https://www.amazon.co.jp/RS%E3%82%B3%E3%83%B3%E3%83%9D%E3%83%BC%E3%83%8D%E3%83%B3%E3%83%88Raspberry-Pi-3-B-%E3%83%9E%E3%82%B6%E3%83%BC%E3%83%9C%E3%83%BC%E3%83%89/dp/B07BFH96M3)
  - ラズパイのOS:[Raspbian Buster with desktop 4.19](https://www.raspberrypi.org/downloads/raspbian/)	
  - Python 3.7.3
  - blueman stable,now 2.0.8-1+b2 armhf
  - [bluepy 1.3.0]() 
- [A&D Bluetooth内蔵 体温計 UT-201BLE](https://www.amazon.co.jp/A-D-Bluetooth%E5%86%85%E8%94%B5-%E4%BD%93%E6%B8%A9%E8%A8%88-UT-201BLE/dp/B00ZQMNV94)

  

##### ここまでセットアップした状態から始めます

- Wifi接続済み
- Google日本語入力「Mozc」インストール済み
	- 参考:[Raspberry Pi3の日本語入力を有効にする](https://qiita.com/Higemal/items/6cde9d6b40cbe9f0e97f)



# 体温計について

体温計は[A&D Bluetooth内蔵 体温計 UT-201BLE](https://www.amazon.co.jp/A-D-Bluetooth%E5%86%85%E8%94%B5-%E4%BD%93%E6%B8%A9%E8%A8%88-UT-201BLE/dp/B00ZQMNV94)を使います。

この体温計はBLEの**GATT(Generic attribute profile)**という世界標準規格のインタフェース仕様を実装しています。

以下のサイトでインタフェースが公開されています。

- [GATT](https://www.bluetooth.com/ja-jp/specifications/gatt/)
- [GATT Services](https://www.bluetooth.com/specifications/gatt/services/)
- [GATT Characteristics](https://www.bluetooth.com/specifications/gatt/characteristics/)
- [Health Thermometer](https://www.bluetooth.com/xml-viewer/?src=https://www.bluetooth.com/wp-content/uploads/Sitecore-Media-Library/Gatt/Xml/Services/org.bluetooth.service.health_thermometer.xml)
- [Temperature Measurement](https://www.bluetooth.com/xml-viewer/?src=https://www.bluetooth.com/wp-content/uploads/Sitecore-Media-Library/Gatt/Xml/Characteristics/org.bluetooth.characteristic.temperature_measurement.xml)



操作手順は以下のとおりです。

- ホストと体温計をペアリングする。
  - 最初の１回だけやればOK。
- 体温を測り終えると自動的にホストに測定値を送信する。
  - 一定時間送信をトライして送信できなければ次回の送信時にまとめて送ります。
  - 時計を内蔵しているので測定時間も送ります。

今回の場合、ホストはラズパイです。



# 体温計とラズパイをペアリングする

体温計とラズパイをペアリングします。

①まずはbluemanを入れます。

```bash
$ sudo apt-get install blueman
$ reboot
```

②再起動すると、アイコンが増えているのでここからペアリングします。

<img src="/Users/suzuki/Documents/GitHub/BLEThermometer/doc/img/192_168_11_13__raspberrypi__-_VNC_Viewer.png" alt="192_168_11_13__raspberrypi__-_VNC_Viewer" style="zoom:40%;" />

③「新しいデバイスを設定」からウィザードでペアリングします。

<img src="/Users/suzuki/Documents/GitHub/BLEThermometer/doc/img/192_168_11_13__raspberrypi__-_VNC_Viewer-2.png" alt="192_168_11_13__raspberrypi__-_VNC_Viewer-2" style="zoom:40%;" />

④ペアリング成功すると、デバイスの左上に鍵のようなマークが表示されます。これでOK。

<img src="/Users/suzuki/Documents/GitHub/BLEThermometer/doc/img/192_168_11_13__raspberrypi__-_VNC_Viewer-3.png" alt="192_168_11_13__raspberrypi__-_VNC_Viewer-3" style="zoom:50%;" />



**ここが結局謎だったのですが、ペアリングが失敗します。何度もやってやっとペアリングできました。私の環境だけかもしれません。ペアリングして④のように鍵マークがつく状態になっていないと、この後の作業のどこかで変なエラーになるので注意です。**



# BLEの確認

さっそくプログラム、ではなく、勉強も兼ねて手軽にできることから確認していきます。



### hcitool

まずは体温計が発信しているアドバイスパケットをスキャンしてみましょう。
**hcitool**というのがありまして、これを使うとBLEデバイスのアドバタイズパケットをスキャンすることができます。

以下のコマンドを実行します。

```bash
$ sudo hcitool lescan
```

コマンドを実行すると近くでアドバタイジングしているBLEデバイスがスキャンされます。
この状態で体温計をペアリングモードにしてみるとアドバイスパケットを確認できるかと思います。
私の体温計のBLEアドレスは`18:93:D7:76:C9:B8`でした。

```bash
$ sudo hcitool lescan
LE Scan ...
5A:60:E6:D4:EF:94 (unknown)
5F:C1:20:2B:BE:60 (unknown)
5F:C1:20:2B:BE:60 AQtGSk1xNFF0YQ
18:93:D7:76:C9:B8 A&D_UT201BLE_76C9B8 ←これ！
```



### gatttool

次に**gatttool**で体温計に接続してみます。
gatttoolはGATTでBLEデバイスとお話しするツールです。
-bでBLEアドレスを指定して実行します。

```bash
$ gatttool -b xx:xx:xx:xx:xx:xx -I
```

-Iで実行すると対話モードでコマンド入力待ちになります。
`connect`コマンドで接続します。
すかさず体温を測り体温計を送信モードにします。
体温計と接続すると**Connection successful**となります。

ちなみに体温計の送信モードは１分ほどで強制終了してしまうので切れたらまた体温を計って送信モードにしましょう。これが地味にめんどくさいのですがデバイスの仕様なので仕方がない...

```bash
$ gatttool -b 18:93:D7:76:C9:B8 -I
[18:93:D7:76:C9:B8][LE]> connect
Attempting to connect to 18:93:D7:76:C9:B8
Connection successful
```

接続したら`primary`コマンドで体温計が持っているサービスのUUIDを見てみます。

```bash
[18:93:D7:76:C9:B8][LE]> primary
attr handle: 0x0001, end grp handle: 0x000b uuid: 00001800-0000-1000-8000-00805f9b34fb
attr handle: 0x000c, end grp handle: 0x000f uuid: 00001801-0000-1000-8000-00805f9b34fb
attr handle: 0x0010, end grp handle: 0x0017 uuid: 00001809-0000-1000-8000-00805f9b34fb
attr handle: 0x0018, end grp handle: 0x0028 uuid: 0000180a-0000-1000-8000-00805f9b34fb
attr handle: 0x0029, end grp handle: 0x002b uuid: 0000180f-0000-1000-8000-00805f9b34fb
attr handle: 0x002c, end grp handle: 0xffff uuid: 233bf000-5a34-1b6d-975c-000d5690abe4
```

これらのUUIDは何なのか、[GATTのサイト](https://www.bluetooth.com/ja-jp/specifications/gatt/services/)をみると、なんとなくわかります。

| handle              | UUID                                     | Name                   |
| ------------------- | ---------------------------------------- | ---------------------- |
| 0x0001 - 0x000b     | 00001800-0000-1000-8000-00805f9b34fb     | Generic Access         |
| 0x000c - 0x000f     | 00001801-0000-1000-8000-00805f9b34fb     | Generic Attribute      |
| **0x0010 - 0x0017** | **00001809-0000-1000-8000-00805f9b34fb** | **Health Thermometer** |
| 0x0018 - 0x0028     | 0000180a-0000-1000-8000-00805f9b34fb     | Device Information     |
| 0x0029 - 0x002b     | 0000180f-0000-1000-8000-00805f9b34fb     | Battery Service        |
| 0x002c - 0xffff     | 233bf000-5a34-1b6d-975c-000d5690abe4     | 不明                   |

重要なのは**1809**の**Health Thermometerサービス**です。

Health Thermometerサービスのキャラクタリスティックを確認するには`char-desc`コマンドです。

`char-desc`にはHealth Thermometerサービスのハンドル（attire handleとgrp handle値）を指定します。

またUUIDがずらずらとでてきます。

```bash
[18:93:D7:76:C9:B8][LE]> char-desc 0x0010 0x0017
handle: 0x0010, uuid: 00002800-0000-1000-8000-00805f9b34fb
handle: 0x0011, uuid: 00002803-0000-1000-8000-00805f9b34fb
handle: 0x0012, uuid: 00002a1c-0000-1000-8000-00805f9b34fb
handle: 0x0013, uuid: 00002902-0000-1000-8000-00805f9b34fb
handle: 0x0014, uuid: 00002803-0000-1000-8000-00805f9b34fb
handle: 0x0015, uuid: 00002a1d-0000-1000-8000-00805f9b34fb
handle: 0x0016, uuid: 00002803-0000-1000-8000-00805f9b34fb
handle: 0x0017, uuid: 00002a08-0000-1000-8000-00805f9b34fb
```

[GATTのサイト](https://www.bluetooth.com/specifications/gatt/characteristics/)で確認します。

| handle     | UUID                                     | Name                        |
| ---------- | ---------------------------------------- | --------------------------- |
| 0x0010     | 00002800-0000-1000-8000-00805f9b34fb     | Primary Service             |
| 0x0011     | 00002803-0000-1000-8000-00805f9b34fb     | Characteristic Declaration  |
| **0x0012** | **00002a1c-0000-1000-8000-00805f9b34fb** | **Temperature Measurement** |
| **0x0013** | **00002902-0000-1000-8000-00805f9b34fb** | **Descriptor**              |
| 0x0014     | 00002803-0000-1000-8000-00805f9b34fb     | Characteristic Declaration  |
| 0x0015     | 00002a1d-0000-1000-8000-00805f9b34fb     | Temperature Type            |
| 0x0016     | 00002803-0000-1000-8000-00805f9b34fb     | Characteristic Declaration  |
| 0x0017     | 00002a08-0000-1000-8000-00805f9b34fb     | Date Time                   |

ここで大事なのが以下の2つです。

- **2a1c - Temperature Measurement**
  - 測定結果のキャラクタリスティックです。Indicateタイプで、つまり、データを送信してくるタイプです。
- **2902 - Descriptor**
  - ディスクリプタというもので、2a1cの追加属性です。具体的にはIndicateをONにしてデータ送信開始するかどうかのフラグを持っています。
  - 設定をReadしたり、Writeして設定変更したりできます。



要するに、**Descriptorに「送信開始」と設定するとTemperature Measurementからデータが送信されてくる**、ということです。

やってみましょう。

まずはDescriptorの設定値をReadしてみます。キャラクタリスティックの値をReadするのは`char-read-hnd`コマンドです。引数にDescriptorのHandle値を指定します。

```bash
[18:93:D7:76:C9:B8][LE]> char-read-hnd 0x0013
Characteristic value/descriptor: 00 00 
```

**00 00** という値が取れています。これはIndicateがOFFの状態、という意味です。

Descriptorの値は

- **0100**　→　Notifyを有効にする
- **0200**　→　Indicateを有効にする

という意味です。Temperature MeasurementがIndicateというのはGATT仕様で決まっているので、**0200**にすればOKです。

設定値のWriteは`char-write-req`と叩きます。引数にDescriptorのHandle値と設定値**0200**を指定します。

```bash
[18:93:D7:76:C9:B8][LE]> char-write-req 0x0013 0200
Characteristic value was written successfully
Indication   handle = 0x0012 value: 06 73 01 00 ff e4 07 05 02 0a 28 13 02 
```

うまくいくとIndicateが始まり、handle=0x0012からデータが流れてきます。

handle=0x0012とは**2a1c - Temperature Measurement**のことです。



gatttoolの話が長くなってしまったのでまとめます。

```bash
# gatttoolの起動
$ gatttool -b xx:xx:xx:xx:xx:xx -I

# デバイスと接続
$ connect

# サービスUUID一覧取得
$ primary

# キャラクタリスティック一覧取得
$ char-desc 開始handle 終了handle

# キャラクタリスティックの値をReadする
$ char-read-hnd handle

# キャラクタリスティックの値をWriteする
$ char-write-req handle data
```



体温を測り終わったら以下のコマンドで測定値がGETできます。

```bash
$ gatttool -b 18:93:D7:76:C9:B8 -I
> connect
> char-write-req 0x0013 0200
```



# 測定値データのフォーマット

体温計からはこんなデータが贈られてきましたが、これは一体何なのでしょうか？

```bash
06 73 01 00 ff e4 07 05 02 0a 28 13 02
```

データのフォーマットはここに書いてあります。

[Temperature Measurement](https://www.bluetooth.com/xml-viewer/?src=https://www.bluetooth.com/wp-content/uploads/Sitecore-Media-Library/Gatt/Xml/Characteristics/org.bluetooth.characteristic.temperature_measurement.xml)

めちゃくちゃわかりにくいので書き直します。

| byte | name  |                                                              |
| ---- | ----- | ------------------------------------------------------------ |
| 1    | Flags | データの構造を示すフラグ<br />bit 0 - Temperature Units Flag: 0 = C1有 C2無 , 1 = C1無 C2有<br />bit 1 - Time Stamp Flag : 0 = C3無 , 1 = C3有<br />bit 2 - Temperature Type Flag : 0 = C4無 , 1 = C4有<br />bit 3-7 : 未使用 |
| 4    | C1    | Temperature Measurement Value (Celsius) - 測定値 摂氏<br />IEEE 11073 32bit float形式 |
| 4    | C2    | Temperature Measurement Value (Fahrenheit) - 測定値 華氏<br />IEEE 11073 32bit float形式 |
| 7    | C3    | Time Stamp 測定日時<br />- yyyy 2byte ushort<br/>\- mm 1byte<br/>\- dd 1byte<br/>\- hh 1byte<br/>\- mm 1byte<br/>\- ss 1byte |
| 1    | C4    | Temperature Type 温度タイプ<br />[参照](https://www.bluetooth.com/xml-viewer/?src=https://www.bluetooth.com/wp-content/uploads/Sitecore-Media-Library/Gatt/Xml/Characteristics/org.bluetooth.characteristic.temperature_type.xml) |

受信したデータをパースしてみます。

| byte  | data                 | パース結果                                                   |
| ----- | -------------------- | ------------------------------------------------------------ |
| Flags | 06                   | 0000-0110<br />bit 0 = 0 : C1有 C2無<br />bit 1 = 1 : C3有<br />bit 2 = 1 : C4有 |
| C1    | 73 01 00 ff          | 36.1                                                         |
| C3    | e4 07 05 02 0a 28 13 | 2020/5/2 10:40:19                                            |
| C4    | 02                   | Body (general)                                               |

C1は4byteのデータで**IEEE 11073 32bit float**形式です。この形式の詳しい説明は以下のサイトが参考になります。

- [JavaScriptでバイナリデータを扱ってみる~IEEE-754とIEEE-11073の浮動小数点~(2/3)](https://qiita.com/megadreams14/items/1c88e71d87970bc8ab90)
- [WindowsデスクトップアプリでBLEのGATTで体温計と血圧計と通信する]([https://qiita.com/gebo/items/41da7474936845d77d06#4temperature-measurement%E3%81%AE%E3%82%A4%E3%83%99%E3%83%B3%E3%83%88%E3%81%A7%E4%BD%93%E6%B8%A9%E6%B8%AC%E5%AE%9A%E5%80%A4%E3%82%92%E5%8F%96%E5%BE%97](https://qiita.com/gebo/items/41da7474936845d77d06#4temperature-measurementのイベントで体温測定値を取得))
- [to_float_from_11073_32bit_float.py](https://github.com/gebogebogebo/BLEThermometer/blob/master/src/to_float_from_11073_32bit_float.py)



結果

- 体温＝36.1℃
- 測定日時＝2020/5/2 10:40:19

というデータであることがわかりました。体温と測定した日時がちゃんと取れています。いい感じです。



# おつかれさまでした

キリがいいので今回はここまで。

#2に続く



