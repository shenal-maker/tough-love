"""Check what's actually in your Cyberwave environment"""
import cyberwave as cw
from dotenv import load_dotenv
load_dotenv()

print("Checking your Cyberwave environment...")
print()

client = cw.Cyberwave()

# List environments
print("Your environments:")
try:
    envs = client.environments.list()
    for env in envs:
        print(f"  - Name: {env.name if hasattr(env, 'name') else 'N/A'}")
        print(f"    ID: {env.uuid if hasattr(env, 'uuid') else env}")
        print()
except Exception as e:
    print(f"  Error: {e}")
    print()

# Try to connect and get info
print("Connecting to environment f3016ce0-620b-466f-81bd-7d75e7bf46e0...")
try:
    robot = cw.twin("the-robot-studio/so101", environment="f3016ce0-620b-466f-81bd-7d75e7bf46e0")
    print("✓ Connection successful!")
    print()
    
    print("Robot info:")
    print(f"  Type: {type(robot)}")
    print(f"  Has joints: {hasattr(robot, 'joints')}")
    
    if hasattr(robot, 'joints'):
        print(f"  Joints object: {robot.joints}")
    
    print()
    print("CRITICAL: Go to this URL in your browser:")
    print("https://cyberwave.com/environments/f3016ce0-620b-466f-81bd-7d75e7bf46e0")
    print()
    print("Look for:")
    print("  - A 3D viewer showing a robotic arm")
    print("  - A 'Play' or 'Start' button")
    print("  - An asset list showing 'SO-101' or similar")
    print()
    print("If you see NOTHING or a blank environment:")
    print("  → The environment might be empty")
    print("  → You may need to add the SO-101 asset in the UI")
    
except Exception as e:
    print(f"✗ Connection failed: {e}")
    import traceback
    traceback.print_exc()
