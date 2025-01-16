import sys
import os
import time

from kortex_api.autogen.client_stubs.BaseClientRpc import BaseClient
from kortex_api.autogen.messages import Base_pb2
from move_to_x_y import move_to_cartesian_position
from arm import move_arm_to_chess_pos2



def pick_chess_piece(base, target_z):
    # Move the arm to the target z-coordinate (keeping x and y fixed)
    current_pose = base.GetMeasuredCartesianPose()  # Get current pose
    current_x, current_y, current_z = current_pose.x, current_pose.y, current_pose.z
    
    open_gripper(base)
    
    print(f"Moving to target z-coordinate {target_z} while keeping x and y fixed...")
    # move_arm_to_chess_pos2(base,chessboard_pos,target_z)
    move_to_cartesian_position(base,current_x, current_y, target_z)
    time.sleep(1)

    # Close the gripper to pick the piece
    print("Closing gripper to pick the chess piece...")
    close_gripper(base)

    # Return to the original z-coordinate
    print("Returning to original z-coordinate...")
    move_to_cartesian_position(base,current_x, current_y, current_z)
    # move_arm_to_chess_pos2(base,chessboard_pos,current_z)
    time.sleep(1)

def place_chess_piece(base, target_z):
    # Move the arm to the target z-coordinate (keeping x and y fixed)
    current_pose = base.GetMeasuredCartesianPose()  # Get current pose
    current_x, current_y, current_z = current_pose.x, current_pose.y, current_pose.z

    print(f"Moving to target z-coordinate {target_z} while keeping x and y fixed...")
    move_to_cartesian_position(base,current_x, current_y, target_z)
    # move_arm_to_chess_pos2(base,chessboard_pos,target_z)
    time.sleep(1)

    # Open the gripper to release the piece
    print("Opening gripper to release the chess piece...")
    open_gripper(base)

    # Return to the original z-coordinate
    print("Returning to original z-coordinate...")
    # move_arm_to_chess_pos2(base,chessboard_pos,current_z)
    move_to_cartesian_position(base,current_x, current_y, current_z)
    time.sleep(1)

def close_gripper(base):
    # Function to close the gripper
    gripper_command = Base_pb2.GripperCommand()
    finger = gripper_command.gripper.finger.add()
    gripper_command.mode = Base_pb2.GRIPPER_POSITION
    finger.finger_identifier = 1
    finger.value = 0.7
    base.SendGripperCommand(gripper_command)
    finger.value = 0.88
    base.SendGripperCommand(gripper_command)
    time.sleep(1)

def open_gripper(base):
    # Function to open the gripper
    gripper_command = Base_pb2.GripperCommand()
    finger = gripper_command.gripper.finger.add()
    gripper_command.mode = Base_pb2.GRIPPER_SPEED
    finger.value = 0.1  # Full open
    base.SendGripperCommand(gripper_command)
    gripper_request = Base_pb2.GripperRequest()

    # Wait for reported position to be opened
    gripper_request.mode = Base_pb2.GRIPPER_POSITION
    while True:
        gripper_measure = base.GetMeasuredGripperMovement(gripper_request)
        if len (gripper_measure.finger):
            print("Current position is : {0}".format(gripper_measure.finger[0].value))
            if gripper_measure.finger[0].value < 0.68:
                break
        else: # Else, no finger present in answer, end loop
            break


# def main():
#     # Import the utilities helper module
#     import argparse
#     sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
#     import utilities

#     # Parse arguments
#     parser = argparse.ArgumentParser()
#     args = utilities.parseConnectionArguments(parser)

#     # Create connection to the device and get the router
#     with utilities.DeviceConnection.createTcpConnection(args) as router:
#         example = Gripper(router)
#         move_arm_to_chess_pos2(example.base,"d4")
#         example.pick_chess_piece(target_z=0.049)  # Example pick
#         time.sleep(2)
#         move_arm_to_chess_pos2(example.base,"d8")
#         example.place_chess_piece(target_z=0.049)  # Example place


# if __name__ == "__main__":
#     main()
