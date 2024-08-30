# Detection Logic with Tilt-Switch and IR Obstacle Avoidance Sensor

## Entry Detection:
- When the Tilt-Switch triggers (indicating the door has moved), check the status of the IR Obstacle Avoidance Sensor.
- If the IR sensor detects an obstacle shortly after the door opens, it's likely that someone has entered the room.

## Presence Monitoring:
- Continuously monitor the IR Obstacle Avoidance Sensor to see if it consistently detects an obstacle. If it does, it suggests that someone is still in the room.
  
## Exit Detection:
- When the Tilt-Switch triggers again (indicating the door has moved), check the status of the IR sensor.
- If the IR sensor no longer detects an obstacle shortly after the door closes, it's likely that the person has left the room.
