from robot_lib import *
import time

print("Testing turn function. 10 seconds between tests.")

# Test 1: Turn 90 degrees right
print("\nTest 1: Turning 90 degrees right at 40% speed.")
turn(90)
time.sleep(5)

# Test 2: Turn 90 degrees left
print("\nTest 2: Turning 90 degrees left at 40% speed.")
turn(-90)
time.sleep(5)

# Test 3: Turn 180 degrees right
print("\nTest 3: Turning 180 degrees right at 60% speed.")
turn(180)
time.sleep(5    )

print("\nTurn test finished.")
stop()