"""Debug Cyberwave connection"""
import os
from dotenv import load_dotenv
load_dotenv()

import cyberwave as cw

print("API Key:", os.getenv("CYBERWAVE_API_KEY")[:20] + "...")

print("\nConnecting to Cyberwave...")
client = cw.Cyberwave()

print("\nListing your projects:")
try:
    projects = client.projects.list()
    for p in projects:
        print(f"  - {p.name} (ID: {p.id})")
except Exception as e:
    print(f"Error: {e}")

print("\nListing your environments:")
try:
    envs = client.environments.list()
    for e in envs:
        print(f"  - {e.name} (ID: {e.id})")
except Exception as e:
    print(f"Error: {e}")

print("\nTrying to connect to environment f3016ce0-620b-466f-81bd-7d75e7bf46e0...")
try:
    robot = cw.twin("the-robot-studio/so101", environment="f3016ce0-620b-466f-81bd-7d75e7bf46e0")
    print("✓ Connected to twin!")
    
    print("\nTesting simple movement...")
    robot.joints.set("1", 30)
    print("✓ Sent command: Joint 1 to 30 degrees")
    
    import time
    time.sleep(2)
    
    robot.joints.set("1", 0)
    print("✓ Sent command: Joint 1 back to 0")
    print("\nCheck your browser NOW - did joint 1 move left then back to center?")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
