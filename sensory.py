import RPi.GPIO as GPIO
import time

# Setup GPIO
GPIO.setmode(GPIO.BCM)
IR_PIN = 17  # IR sensor pin, adjust to your wiring
TILT_PIN = 18  # Tilt-switch pin, adjust to your wiring

# Setup GPIO pins
GPIO.setup(IR_PIN, GPIO.IN)
GPIO.setup(TILT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Variable to track presence
presence_detected = False

def infrared_callback(channel):
    global presence_detected
    if GPIO.input(IR_PIN) == GPIO.LOW:
        print("Obstacle detected by IR Sensor.")
        presence_detected = True
    else:
        print("No obstacle detected by IR Sensor.")
        presence_detected = False

def tilt_callback(channel):
    global presence_detected
    time.sleep(1)  # Small delay to account for door movement
    if GPIO.input(IR_PIN) == GPIO.LOW:
        print("Door moved and obstacle detected, someone likely entered the room.")
        presence_detected = True
    else:
        print("Door moved but no obstacle detected, someone likely left the room.")
        presence_detected = False

# Setup event detection
GPIO.add_event_detect(IR_PIN, GPIO.BOTH, callback=infrared_callback)
GPIO.add_event_detect(TILT_PIN, GPIO.BOTH, callback=tilt_callback)

try:
    while True:
        if presence_detected:
            print("Someone is in the room.")
        else:
            print("The room is empty.")
        time.sleep(5)  # Check every 5 seconds
except KeyboardInterrupt:
    GPIO.cleanup()
