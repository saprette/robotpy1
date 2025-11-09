# robot_lib.py
import time

import machine

# Pin definitions for ultrasonic sensor
trig_pin = machine.Pin(10, machine.Pin.OUT)
echo_pin = machine.Pin(11, machine.Pin.IN)

# Pin definitions for L9110S motor driver
pwm1 = machine.PWM(machine.Pin(16), freq=1000)  # L9110S B-1A motors Left       GPIO16
pwm2 = machine.PWM(machine.Pin(17), freq=1000)  # L9110S B-1B motors Left       GPIO17
pwm3 = machine.PWM(machine.Pin(18), freq=1000)  # L9110S A-1A motors Right      GPIO18
pwm4 = machine.PWM(machine.Pin(19), freq=1000)  # L9110S A-2A motors Right      GPIO19

# define IN_1  16            // L9110S B-1A motors Left       GPIO16
# define IN_2  17            // L9110S B-1B motors Left       GPIO17
# define IN_3  18            // L9110S A-1A motors Right      GPIO18
# define IN_4  12            // L9110S A-2A motors Right      GPIO19

# Pin definition for Servo
# A servo is controlled by PWM, typically at 50Hz
servo_pwm = machine.PWM(machine.Pin(5), freq=50)

# Motor speed as a percentage (0-100).
speed_car = 30

# Minimum PWM duty cycle to start the motors (approx. 40% of max).
# This helps overcome static friction at low speed percentages.
MIN_DUTY_CYCLE = 25000
MAX_DUTY_CYCLE = 65535

# Initialize sensor pins with internal pull-down resistors
line_sensor_12 = machine.Pin(12, machine.Pin.IN, machine.Pin.PULL_DOWN)  # right edge
line_sensor_13 = machine.Pin(13, machine.Pin.IN, machine.Pin.PULL_DOWN)  # right
line_sensor_14 = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_DOWN)  # center
line_sensor_15 = machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_DOWN)  # left
line_sensor_20 = machine.Pin(20, machine.Pin.IN, machine.Pin.PULL_DOWN)  # left edge

class SensorPosition:
    RIGHT_EDGE = "RIGHT_EDGE"
    RIGHT = "RIGHT"
    CENTER = "CENTER"
    LEFT = "LEFT"
    LEFT_EDGE = "LEFT_EDGE"


sensors = {
    SensorPosition.RIGHT_EDGE: line_sensor_12,
    SensorPosition.RIGHT: line_sensor_13,
    SensorPosition.CENTER: line_sensor_14,
    SensorPosition.LEFT: line_sensor_15,
    SensorPosition.LEFT_EDGE: line_sensor_20
}


def read_line_sensors():
    """Reads the status of the line detector sensors and returns a dictionary."""
    status = {}
    for position, pin in sensors.items():
        # A black line is detected when the pin value is 1 (HIGH)
        status[position] = pin.value() == 0
    return status


def print_line_sensors(status):
    """Prints a graphical representation of the sensor status with a timestamp."""
    now = time.localtime()
    ms = time.ticks_ms() % 1000
    timestamp = f"{now[0]:04d}-{now[1]:02d}-{now[2]:02d} {now[3]:02d}:{now[4]:02d}:{now[5]:02d}.{ms // 10:02d}"

    positions = [SensorPosition.LEFT_EDGE, SensorPosition.LEFT, SensorPosition.CENTER, SensorPosition.RIGHT, SensorPosition.RIGHT_EDGE]
    graphical = " | ".join("X" if status.get(pos, False) else "O" for pos in positions)
    print(f"{timestamp} - Sensors: [{graphical}]")


def servo_turn(angle):
    """
    Turns the servo to a specific angle.
    Angle should be between 0 and 180.
    - 0: Turn far right
    - 90: Center
    - 180: Turn far left
    """
    if 0 <= angle <= 180:
        print(f"Turning servo to angle: {angle}")
        angle = angle + 10  # Calibration offset
        if angle > 180:
            angle = 180
        # The pulse width for an SG90 servo is typically 500us (0 deg) to 2500us (180 deg).
        # For a 50Hz frequency, the period is 20000us.
        # We map the angle to a duty cycle value for duty_u16 (0-65535).
        # 1638 is approx 1ms pulse, 8192 is approx 2ms pulse.
        # A common range is ~1000 to ~9000 for 0-180 degrees.
        # Let's use a calibrated range from 1350 (0 deg) to 8350 (180 deg).
        duty_u16 = int(1350 + (angle / 180) * (8350 - 1350))
        servo_pwm.duty_u16(duty_u16)
    else:
        print(f"Error: Angle {angle} must be between 0 and 180.")


def get_distance():
    """Measures distance using the ultrasonic sensor."""
    trig_pin.value(0)
    time.sleep_us(2)
    trig_pin.value(1)
    time.sleep_us(10)
    trig_pin.value(0)
    try:
        pulse_duration = machine.time_pulse_us(echo_pin, 1, 30000)
    except OSError:
        pulse_duration = 0
    distance = pulse_duration / 58.0
    print(f"Distance = {distance:.2f} cm")
    return distance

def _calculate_duty_cycle(speed):
    """
    Calculates the PWM duty cycle from a speed percentage (0-100).
    Maps the speed to a non-linear range to ensure motors turn at low speeds.
    """
    if speed <= 0:
        return 0
    # Clamp speed to 0-100
    speed = max(0, min(100, speed))
    # Map speed percentage [1-100] to PWM range [MIN_DUTY_CYCLE - MAX_DUTY_CYCLE]
    duty_range = MAX_DUTY_CYCLE - MIN_DUTY_CYCLE
    duty_value = int(MIN_DUTY_CYCLE + (speed / 100.0) * duty_range)

    print(f"Calculated duty cycle for speed {speed}%: {duty_value}")
    return duty_value

def left_motor_forward(speed=speed_car):
    """Sets the left motor to move forward at a given speed percentage."""
    duty_value = _calculate_duty_cycle(speed)
    pwm1.duty_u16(0)
    pwm2.duty_u16(duty_value)


def left_motor_backward(speed=speed_car):
    """Sets the left motor to move backward at a given speed percentage."""
    duty_value = _calculate_duty_cycle(speed)
    pwm1.duty_u16(duty_value)
    pwm2.duty_u16(0)


def right_motor_forward(speed=speed_car):
    """Sets the right motor to move forward at a given speed percentage."""
    duty_value = _calculate_duty_cycle(speed)
    pwm3.duty_u16(duty_value)
    pwm4.duty_u16(0)


def right_motor_backward(speed=speed_car):
    """Sets the right motor to move backward at a given speed percentage."""
    duty_value = _calculate_duty_cycle(speed)
    pwm3.duty_u16(0)
    pwm4.duty_u16(duty_value)


def forward(speed=speed_car):
    right_motor_forward(speed)
    left_motor_forward(speed)


def backward(speed=speed_car):
    right_motor_backward(speed)
    left_motor_backward(speed)


def turn_right(speed=speed_car):
    left_motor_forward(speed)
    right_motor_backward(speed)


def turn_left(speed=speed_car):
    left_motor_backward(speed)
    right_motor_forward(speed)


def turn(angle, speed=20):
    """
    Turns the robot by a specific angle using hardcoded speed and duration.
    - angle: An integer value (-90, 90, -180, 180).
    """
    if angle == 90:
        left_motor_forward(speed)
        right_motor_backward(speed)
        time.sleep_ms(350)
    elif angle == -90:
        left_motor_backward(speed)
        right_motor_forward(speed)
        time.sleep_ms(350)
    elif angle == 180:
        left_motor_forward(speed)
        right_motor_backward(speed)
        time.sleep_ms(700)
    elif angle == -180:
        left_motor_backward(speed)
        right_motor_forward(speed)
        time.sleep_ms(700)
    else:
        print(f"Error: Invalid angle {angle}. Must be -90, 90, -180, or 180.")
        return
    stop()


def stop():
    pwm1.duty_u16(0)
    pwm2.duty_u16(0)
    pwm3.duty_u16(0)
    pwm4.duty_u16(0)
