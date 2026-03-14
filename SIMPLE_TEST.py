"""
SIMPLEST POSSIBLE TEST - Just moves joint 1 back and forth
Watch at: https://cyberwave.com/environments/f3016ce0-620b-466f-81bd-7d75e7bf46e0
(MUST BE LOGGED IN!)
"""

import cyberwave as cw
import time
from dotenv import load_dotenv
load_dotenv()

print("="*60)
print("SIMPLE ROBOT TEST")
print("="*60)
print("\n1. Open browser: https://cyberwave.com")
print("2. LOG IN to your Cyberwave account")
print("3. Go to: https://cyberwave.com/environments/f3016ce0-620b-466f-81bd-7d75e7bf46e0")
print("4. Watch the 3D robot arm on screen")
print("\nStarting test in 3 seconds...")
time.sleep(3)

robot = cw.twin("the-robot-studio/so101", environment="f3016ce0-620b-466f-81bd-7d75e7bf46e0")
print("\n✓ Connected to Cyberwave!")

print("\nMoving base joint LEFT...")
robot.joints.set("1", 45, source_type='sim')
time.sleep(3)

print("Moving base joint RIGHT...")
robot.joints.set("1", -45, source_type='sim')
time.sleep(3)

print("Moving base joint CENTER...")
robot.joints.set("1", 0, source_type='sim')
time.sleep(2)

print("\n" + "="*60)
print("TEST COMPLETE!")
print("="*60)
print("\nDid you see the robot base rotate left, then right, then center?")
print("If YES - your project WORKS! Submit to Devpost NOW!")
print("If NO - make sure you're logged in to Cyberwave.com")
