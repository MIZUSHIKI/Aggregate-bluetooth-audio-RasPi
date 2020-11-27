#coding: utf-8

###
#
#  Bluetooth機器への操作プログラム (+ Raspberry Pi 物理ボタンで操作先変更)
#
###

import evdev
import subprocess
import threading
import RPi.GPIO as GPIO
import time
from time import sleep
import shutil

#
#  初期設定
#

#GPIO(物理ボタンを設置する場合)
# 【各環境で変更】
PIN_IN = 5  # GPIO.IN, pull_up_down=GPIO.PUD_DOWN
PIN_OUTs = [6, 13, 19, 26]  # GPIO.OUT
outIndex = 0
inflag = False
nagaosiCount = 0

#音声出力するデバイスの名前(出力側ヘッドホン)
#  (USB-DACにしてるからevdevで取得できるんだと思う)
# 【各環境で変更】
DEVICE_NAME = 'Creative Technology Ltd Creative BT-W3 Consumer Control'

#音声入力側のデバイス名
#  sudo apt-get install d-feet のアプリケーションで調べる
# 【各環境で変更】
hcis=[]
hcis.append("/org/bluez/hci0/dev_0C_DD_24_6A_B0_ED") # 0 : WinPC
hcis.append("/org/bluez/hci3/dev_A8_66_7F_35_20_E0") # 1 : MacPC
hcis.append("/org/bluez/hci2/dev_DC_52_85_BD_8B_DD") # 2 : iPhone
hcis.append("/org/bluez/hci1/dev_00_15_9E_40_01_9C") # 3 : TV(操作できない)

#Statusを確認する系が面倒臭そうなのでPlay,Pauseはフラグ管理してまずPauseから実行する
flgPlayPause = False

#device(evdev) 接続デバイス名 列挙
device = evdev.InputDevice('/dev/input/event0')
for i in range(20): #とりま20個まで調べてDEVICE_NAMEと一致するものをdeviceとする
	try:
		dev = evdev.InputDevice(f'/dev/input/event{i}')
		print(f'{i} : {dev}')
		if dev.name == DEVICE_NAME:
			print(f'【接続】{dev.name}')
			device = dev
	except:
		pass
#
#  モジュール
#
#####
# OpenJTalk + python で日本語テキストを発話
#  @kkoba84
#  https://qiita.com/kkoba84/items/b828229c374a249965a9
def jtalk(t):
	if not shutil.which('open_jtalk'):
		return
	open_jtalk=['open_jtalk']
	mech=['-x','/var/lib/mecab/dic/open-jtalk/naist-jdic']
	htsvoice=['-m','/usr/share/hts-voice/mei/mei_normal.htsvoice']
	speed=['-r','1.0']
	outwav=['-ow','open_jtalk.wav']
	cmd=open_jtalk+mech+htsvoice+speed+outwav
	c = subprocess.Popen(cmd,stdin=subprocess.PIPE)
	c.stdin.write(t.encode())
	c.stdin.close()
	c.wait()
	aplay = ['aplay','-q','open_jtalk.wav']
	subprocess.Popen(aplay)
#####

#
#  関数
#
def nextGPIO():
	global outIndex	
	global flgPlayPause
	print(f'd={outIndex}')
	#前のを消す
	GPIO.output(PIN_OUTs[outIndex],GPIO.LOW)
	outIndex += 1
	if outIndex >= len(PIN_OUTs):
		outIndex = 0
	print(f'r={outIndex}')
	#次のを点ける
	GPIO.output(PIN_OUTs[outIndex],GPIO.HIGH)
	#しゃべらせる
	if outIndex == 0:
		jtalk('いち')
	elif outIndex == 1:
		jtalk('にい')
	elif outIndex == 2:
		jtalk('さん')
	elif outIndex == 3:
		jtalk('よん')
	#PlayPauseフラグを初期化
	flgPlayPause = False

def player_controll(method):
	global outIndex
	global flgPlayPause
	if method == 'PlayPause':
		#テキトーなフラグ管理なので音が鳴ってなくてもPauseから発信してしまう
		sendMethod = 'Pause'
		if flgPlayPause:
			sendMethod = 'Play'
		flgPlayPause = not flgPlayPause
	else:
		sendMethod = method
	#dsub-send(コマンド実行)して一時停止、再生、次の曲、前の曲のBluetooth操作を行う
	args = ['dbus-send', '--system', '--print-reply', '--dest=org.bluez', hcis[outIndex], f'org.bluez.MediaControl1.{sendMethod}']
	subprocess.run(args)


def setup():
	#--evdev
	print(device)
	#--GPIO
	print('GPIO setup')	
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(PIN_IN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
	for out in PIN_OUTs:
		GPIO.setup(out,GPIO.OUT)
		#最初にLEDを全部消す
		GPIO.output(out,GPIO.LOW)
	#最初のLEDを点ける
	GPIO.output(PIN_OUTs[0],GPIO.HIGH)
	#--SubThread
	print('thread set')
	th = threading.Thread(target=btevent_read, daemon=True)
	th.start()
#
#  SubThread
#
def btevent_read():
	#イベントごとに処理
	maeTime = time.time()
	for event in device.async_read_loop():
		#print(event)
		if event.value == 1:
			if event.code == 164:
				print('1-click')
				#再生/停止
				player_controll('PlayPause')
			elif event.code == 163:
				print('2-click')
				#次の曲へ
				player_controll('Next')
				# 3→2-click の5連打でBT操作出力先を変更する
				if ( time.time() - maeTime ) < 1.5:
					nextGPIO()
			elif event.code == 165:
				print('3-click')
				#前の曲へ
				player_controll('Previous')
				#5連打検知用の時間を記憶
				maeTime = time.time()
#
#  MAIN
#
if __name__ == '__main__':
	setup()
	try:
		while True:
			#ボタンを押したり離したりしたときだけ
			if inflag != ( GPIO.input(PIN_IN) == GPIO.HIGH ):
				inflag = ( GPIO.input(PIN_IN) == GPIO.HIGH )
				#ボタンを押したときだけ
				if inflag:
					nextGPIO()
			#ボタンを押している間
			if inflag:
				if nagaosiCount % 100 == 0:
					print(f'ButtonDownCount={nagaosiCount}')
				nagaosiCount += 1
			else:
				nagaosiCount = 0
			#ボタンを押し続けて300カウント
			if nagaosiCount >= 300:
				print(f'ButtonDownCount={nagaosiCount}')
				#自己エラーで自壊させる
				raise ValueError('error!!')
			#print(GPIO.input(PIN_IN))
			sleep(0.01)
			
	except KeyboardInterrupt:
		pass
	finally:
		GPIO.cleanup() #終了処理
