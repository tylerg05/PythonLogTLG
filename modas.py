from gpiozero import MotionSensor, LED, Button
from picamera import PiCamera
from time import sleep
import datetime
import random
import requests
import json

class Modas:
	def _init_(self):
		self.camera = PiCamera()
		self.camera.resolution = (800,600)
		self.green = LED(24)
		self.red = LED(23)
		self.button = Button(8)
		self.pir = Button(25)

		self.button.when_released = self.toggle

		self.armed = False
		self.disarm_system()
	
	def init_alert(self):
		self.green.off()
		self.red.blink(on_time=.25, off_time=.25, n=None, background=True)
		print("motion detected")
		self.log()
		sleep(2)

	def log(self):
		t = datetime.datetime.now()
		t_json = "{0}-{1}-{2}T{3}:{4}:{5}".format(t.strftime("%Y"), t.strftime("%m"), t.strftime("%d"), t.strftime("%H), t.strftime("%M), t.strftime("%S))
		randomNum = random.randint(1, 3)
		url = 'https://modas-jsg.azurewebsites.net/api/event/'
		headers = { 'Content-Type': 'application/json'}
		payload = { 'timestamp: t_json, 'flagged': False, 'locationId': randomNum }
		r = requests.post(url, headers=headers, data = json.dumps(payload))
		print(r.status_code)
		print(r.json())

		payload_formatted = t_json + "," + "False" + "," + str(randomNum) + "," + str(r.status_code)
		today = datetime.datetime.today()
		today = today.strftime("%Y-%m-%d")
		filename = today + ".log"
		f = open(filename, "a")
		f.write(payload_formatted)
		f.close()

	def reset(self):
		self.red.off()
		self.green.on()

	def toggle(self):
		self.armed = not self.armed
		if self.armed:
			self.arm_system()
		else:
			self.disarm_system()

	def arm_system(self):
		print("System armed in 3 seconds")
		self.red.off()
		self.green.blink(on_time=.25, off_time=.25, n=6, background=False)
		self.pir.when_pressed = self.init_alert
		self.pir.when_released = self.reset
		self.green.on()
		print("System armed")

	def disarm_system(self):
		self.pir.when_pressed = None
		self.pir.when_released = None
		self.red.on()
		self.green.off()
		print("System disarmed")

m = Modas()

try:
	while True:
		sleep(.001)
except KeyboardInterrupt:
	if m.armed:
		m.disarm_system()
	