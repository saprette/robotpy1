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

#define IN_1  16            // L9110S B-1A motors Left       GPIO16
#define IN_2  17            // L9110S B-1B motors Left       GPIO17
#define IN_3  18            // L9110S A-1A motors Right      GPIO18
#define IN_4  12            // L9110S A-2A motors Right      GPIO19

# Pin definition for Servo
# A servo is controlled by PWM, typically at 50Hz
servo_pwm = machine.PWM(machine.Pin(5), freq=50)

# Motor speed (0-65535). 51200 is ~80% speed.
speed_car = 51200

def servo_turn(angle):
    """
    Turns the servo to a specific angle.
    Angle should be between 25 and 140.
    - 25: Turn far right
    - 90: Center
    - 140: Turn far left
    The duty cycle values (26-128) are calibrated for a standard SG90 servo
    based on the 700-2400us pulse width from the C++ code.
    """
    if 25 <= angle <= 140:
        print(f"Turning servo to {angle} degrees")
        # Map angle (0-180) to duty cycle (26-128 for ESP8266)
        duty = int(26 + (angle / 180) * (128 - 26))
        servo_pwm.duty_u16(duty)
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

def get_distance_wide():
    servo_turn(90)
    time.sleep_ms(300)
    distance_90 = get_distance()

    servo_turn(25)
    time.sleep_ms(300)
    distance_25 = get_distance()

    servo_turn(140)
    time.sleep_ms(300)
    distance_140 = get_distance()

    return min(distance_90, distance_25, distance_140)


def left_motor_forward():
    pwm1.duty_u16(0)
    pwm2.duty_u16(speed_car)


def left_motor_backward():
    pwm1.duty_u16(speed_car)
    pwm2.duty_u16(0)


def right_motor_forward():
    pwm3.duty_u16(speed_car)
    pwm4.duty_u16(0)


def right_motor_backward():
    pwm3.duty_u16(0)
    pwm4.duty_u16(speed_car)


def forward():
    right_motor_forward()
    left_motor_forward()


def backward():
    right_motor_backward()
    left_motor_backward()


def turn_right():
    left_motor_forward()
    right_motor_backward()


def turn_left():
    left_motor_backward()
    right_motor_forward()


def stop():
    pwm1.duty_u16(0)
    pwm2.duty_u16(0)
    pwm3.duty_u16(0)
    pwm4.duty_u16(0)
