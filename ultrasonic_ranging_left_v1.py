#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time
import requests
import json
from datetime import datetime, timezone

TRIG = 13
ECHO = 16

headers = {
	"X-API-KEY": "",
	"Content-Type": "application/json"
}

def send_sensor_reading(reading):
    url = "http://3.27.174.228/backend/api/reading/create/"
    headers = {
        "X-API-KEY": "t",
        "Content-Type": "application/json"
    }
    
    # Get current time in UTC and format it
    current_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    data = {
        "room_name": "WZ320",
        "sensor_name": "Ultrasonic Ranging (left side of room)",
        "reading": reading,
        "datetime_recorded_by_sensor": current_time
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes
        print('Sent data to server:', response)
    except requests.exceptions.RequestException as e:
        print(f'Error sending data to server: {e}')
    
    print('Distance value:', reading)

def setup():
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(TRIG, GPIO.OUT)
	GPIO.setup(ECHO, GPIO.IN)

def distance():
	GPIO.output(TRIG, 0)
	time.sleep(0.25)

	GPIO.output(TRIG, 1)
	time.sleep(0.5)
	GPIO.output(TRIG, 0)

	
	while GPIO.input(ECHO) == 0:
		a = 0
	time1 = time.time()
	while GPIO.input(ECHO) == 1:
		a = 1
	time2 = time.time()

	during = time2 - time1
	return during * 340 / 2 * 100

def send_presence_detected(distance):
    data = {
        'presence_detected': True,
        'room_name': "WZ320",
        'temperature': "16",
        'sensor_name': 'Ultrasonic Ranging (left side of room)'
    }
    
    try:
        response = requests.post("http://3.27.174.228/backend/api/sensor", headers=headers, json=data)
        response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes
        print(f'Presence data sent to server: {response}')
    except requests.exceptions.RequestException as e:
        print(f'Error sending presence data to server: {e}')
    
    print(f'Presence Detected at {distance}cm')

# In the loop function, replace the existing code with:
def loop():
    while True:
        dis = distance()
        send_sensor_reading(dis)
        if dis < 300 or dis > 1000:
            send_presence_detected(dis)
        time.sleep(30)

def destroy():
	GPIO.cleanup()

if __name__ == "__main__":
	setup()
	try:
		loop()
	except KeyboardInterrupt:
		destroy()
