#!/usr/bin/env python3
import PCF8591 as ADC
import RPi.GPIO as GPIO
import time
import requests
import json
from datetime import datetime, timezone


headers = {
	"X-API-KEY": "team-south-pole-2024-iot-project",
	"Content-Type": "application/json"
}


def send_sensor_reading(reading):
	url = "http://3.27.174.228/backend/api/reading/create/"
	headers = {
		"X-API-KEY": "team-south-pole-2024-iot-project",
		"Content-Type": "application/json"
	}
	
	# Get current time in UTC and format it
	current_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

	data = {
		"room_name": "WZ320",
		"sensor_name": "Photoresistor",
		"reading": reading,
		"datetime_recorded_by_sensor": current_time
	}
	
	response = requests.post(url, headers=headers, data=json.dumps(data))
	print ('Light value: ', reading)
	print ('Sent data to server: ', response)
	
def send_empty_occupancy_detection():
	data = { 
		"presence_detected": False,
		"room_name": "WZ320",
		"temperature": "16",
		"sensor_name": "Photoresistor"
	}
	requests.post("http://3.27.174.228/backend/api/sensor", headers=headers, json=data)
	print ('Light dim detected at value: ', ADC.read(0))


def setup():
	ADC.setup(0x48)


def loop():
	status = 1
	while True:
		send_sensor_reading(ADC.read(0))
		if ADC.read(0) > 80:
			time.sleep(10)
			if ADC.read(0) > 80:
				send_empty_occupancy_detection()
				send_sensor_reading(ADC.read(0))
		time.sleep(30)

if __name__ == '__main__':
	try:
		setup()
		loop()
	except KeyboardInterrupt: 
		pass	
