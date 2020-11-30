# Aggregate-bluetooth-audio-RasPi

Raspberry Piを使用して、複数のBluetoothオーディオを１つの無線ヘッドホンに送信する。  
この際にヘッドホン側から各オーディオ機器への再生/一時停止などの操作をできるようにしたものです。

- volume-watcher-InputDevices.py： 入力デバイスの音量変化を検知して各デバイス別に音量を調整する。
- AvrcpPlayControl-Button.py： 出力デバイス(ヘッドホン)のボタン押しを検知して、選択中の入力デバイスに向けて再生コントロール信号を送信する。
- start-aggregate-avrcp.sh： Raspberry Pi 起動時に自動でBluetooth接続とPythonプログラムの起動を行う。

導入方法は以下リンク先を参考にしてください。  
「複数のBluetoothオーディオを１つの無線ヘッドホンに送信」  
http://rori.suwa.pupu.jp/?eid=2

>volume-watcher-InputDevices.py は、[patriot1889](https://github.com/patriot1889)/[Bluez-AVRCP-Volume-Control](https://github.com/patriot1889/Bluez-AVRCP-Volume-Control) からの[Fork](https://github.com/MIZUSHIKI/Bluez-AVRCP-Volume-Control)です。 



↓ 4つの音声が１つのヘッドホンから流れています。  
[<img src="https://user-images.githubusercontent.com/33353602/100634320-807e9600-3372-11eb-8c5b-59b4ef03ce1b.png" width="315px">](https://www.youtube.com/watch?v=bvLdmLcHXDo)

↓ 操作中の様子  
[<img src="https://user-images.githubusercontent.com/33353602/100634158-47debc80-3372-11eb-929c-a2fe923a049b.png" width="315px">](https://www.youtube.com/watch?v=Qi2vA4gs8b0)
