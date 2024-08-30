import RPi.GPIO as GPIO
import time
import requests
import spidev  # Required for interfacing with ADC
import math  # For temperature calculation

# Set up GPIO mode to use Broadcom (BCM) pin numbering
GPIO.setmode(GPIO.BCM)

# Define GPIO pin numbers for the IR sensor and Tilt-switch
IR_PIN = 17  # IR sensor pin, adjust based on your wiring
TILT_PIN = 18  # Tilt-switch pin, adjust based on your wiring

# Setup GPIO pins as input
GPIO.setup(IR_PIN, GPIO.IN)  # Set IR sensor pin as input
GPIO.setup(TILT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Set Tilt-switch pin as input with pull-up resistor

# Setup SPI for ADC communication (e.g., MCP3008)
spi = spidev.SpiDev()  # Create an SPI object
spi.open(0, 0)  # Open SPI bus 0, device 0
spi.max_speed_hz = 1350000  # Set SPI speed to 1.35 MHz

# Define the URL to send the sensor data and the room name
SENSOR_URL = "https://ssod.ademartutor.com/sensor"  # URL to send POST requests
ROOM_NAME = "Room1"  # Replace with the actual room name

# Initialize a variable to track if presence is detected
presence_detected = False

# Function to read data from the ADC channel (connected to the thermistor)
def read_adc(channel):
    adc = spi.xfer2([1, (8 + channel) << 4, 0])  # Send SPI command to read from the specified channel
    data = ((adc[1] & 3) << 8) + adc[2]  # Combine the two bytes of data received from the ADC
    return data

# Function to convert the ADC value to temperature in Celsius
def convert_to_temperature(adc_value):
    # Calculate the resistance of the thermistor based on the ADC value
    resistance = (1023 / adc_value) - 1
    resistance = 10000 / resistance  # Assume a 10k ohm resistor

    # Convert the resistance to temperature using the Steinhart-Hart equation
    temperature_c = (1 / (0.001129148 + (0.000234125 * (math.log(resistance))) + (0.0000000876741 * (math.log(resistance))**3))) - 273.15
    return temperature_c

# Callback function for the IR sensor
def infrared_callback(channel):
    global presence_detected
    if GPIO.input(IR_PIN) == GPIO.LOW:  # If the IR sensor detects an obstacle
        print("Obstacle detected by IR Sensor.")
        presence_detected = True  # Update presence status to True
    else:
        print("No obstacle detected by IR Sensor.")
        presence_detected = False  # Update presence status to False

# Callback function for the Tilt-switch
def tilt_callback(channel):
    global presence_detected
    time.sleep(1)  # Small delay to account for door movement
    if GPIO.input(IR_PIN) == GPIO.LOW:  # Check if the IR sensor detects an obstacle after door movement
        print("Door moved and obstacle detected, someone likely entered the room.")
        presence_detected = True  # Update presence status to True
    else:
        print("Door moved but no obstacle detected, someone likely left the room.")
        presence_detected = False  # Update presence status to False

# Setup GPIO event detection for the IR sensor and Tilt-switch
GPIO.add_event_detect(IR_PIN, GPIO.BOTH, callback=infrared_callback)  # Detect both rising and falling edges on IR_PIN
GPIO.add_event_detect(TILT_PIN, GPIO.BOTH, callback=tilt_callback)  # Detect both rising and falling edges on TILT_PIN

# Function to send presence update to the server
def send_presence_update():
    adc_value = read_adc(0)  # Read the ADC value from channel 0 (where the thermistor is connected)
    temperature = convert_to_temperature(adc_value)  # Convert ADC value to temperature
    
    # Prepare the data to send as JSON
    data = {
        'presence_detected': presence_detected,  # Current presence status
        'room_name': ROOM_NAME,  # Name of the room
        'temperature': temperature  # Temperature in the room
    }
    # Send the data as a POST request to the server
    requests.post(SENSOR_URL, json=data)
    print(f"Presence update sent: {data}")

# Main loop to periodically send presence updates
try:
    while True:
        send_presence_update()  # Send presence update
        time.sleep(10)  # Wait 10 seconds before sending the next update
except KeyboardInterrupt:
    GPIO.cleanup()  # Clean up GPIO settings on exit (e.g., Ctrl+C)
