import sys
import os
import time

from kortex_api.autogen.client_stubs.BaseClientRpc import BaseClient
from kortex_api.autogen.messages import Base_pb2
from move_to_x_y import move_to_cartesian_position as move_arm_to_position
from arm import move_arm_to_chess_pos2

class GripperCommandExample:
    def __init__(self, router, proportional_gain=2.0):
        self.proportional_gain = proportional_gain
        self.router = router

        # Create base client using TCP router
        self.base = BaseClient(self.router)

    def ExampleSendGripperCommands(self):
        # Create the GripperCommand we will send
        gripper_command = Base_pb2.GripperCommand()
        finger = gripper_command.gripper.finger.add()

        # Close the gripper with position increments
        print("Performing gripper test in position...")
        gripper_command.mode = Base_pb2.GRIPPER_POSITION
        position = 0.00
        finger.finger_identifier = 1
        while position < 1.0:
            finger.value = position
            print("Going to position {:0.2f}...".format(finger.value))
            self.base.SendGripperCommand(gripper_command)
            position += 0.1
            time.sleep(1)

        # Set speed to open gripper
        print("Opening gripper using speed command...")
        gripper_command.mode = Base_pb2.GRIPPER_SPEED
        finger.value = 0.1
        self.base.SendGripperCommand(gripper_command)
        gripper_request = Base_pb2.GripperRequest()

        # Wait for reported position to be opened
        gripper_request.mode = Base_pb2.GRIPPER_POSITION
        while True:
            gripper_measure = self.base.GetMeasuredGripperMovement(gripper_request)
            if len(gripper_measure.finger):
                print("Current position is : {0}".format(gripper_measure.finger[0].value))
                if gripper_measure.finger[0].value < 0.01:
                    break
            else:  # Else, no finger present in answer, end loop
                break

        # Set speed to close gripper
        print("Closing gripper using speed command...")
        gripper_command.mode = Base_pb2.GRIPPER_SPEED
        finger.value = -0.1
        self.base.SendGripperCommand(gripper_command)

        # Wait for reported speed to be 0
        gripper_request.mode = Base_pb2.GRIPPER_SPEED
        while True:
            gripper_measure = self.base.GetMeasuredGripperMovement(gripper_request)
            if len(gripper_measure.finger):
                print("Current speed is : {0}".format(gripper_measure.finger[0].value))
                if gripper_measure.finger[0].value == 0.0:
                    break
            else:  # Else, no finger present in answer, end loop
                break

    def pick_chess_piece(self, target_z):
        # Move the arm to the target z-coordinate (keeping x and y fixed)
        current_pose = self.base.GetMeasuredCartesianPose()  # Get current pose
        current_x, current_y, current_z = current_pose.x, current_pose.y, current_pose.z
        
        self.open_gripper()
        
        print(f"Moving to target z-coordinate {target_z} while keeping x and y fixed...")
        move_arm_to_position(self.base,current_x, current_y, target_z)

        # Close the gripper to pick the piece
        print("Closing gripper to pick the chess piece...")
        self.close_gripper()

        # Return to the original z-coordinate
        print("Returning to original z-coordinate...")
        move_arm_to_position(self.base,current_x, current_y, current_z)

    def place_chess_piece(self, target_z):
        # Move the arm to the target z-coordinate (keeping x and y fixed)
        current_pose = self.base.GetMeasuredCartesianPose()  # Get current pose
        current_x, current_y, current_z = current_pose.x, current_pose.y, current_pose.z

        print(f"Moving to target z-coordinate {target_z} while keeping x and y fixed...")
        move_arm_to_position(self.base,current_x, current_y, target_z)

        # Open the gripper to release the piece
        print("Opening gripper to release the chess piece...")
        self.open_gripper()

        # Return to the original z-coordinate
        print("Returning to original z-coordinate...")
        move_arm_to_position(self.base,current_x, current_y, current_z)

    def close_gripper(self):
        # Function to close the gripper
        gripper_command = Base_pb2.GripperCommand()
        finger = gripper_command.gripper.finger.add()
        gripper_command.mode = Base_pb2.GRIPPER_POSITION
        finger.finger_identifier = 1
        finger.value = 0.7
        self.base.SendGripperCommand(gripper_command)
        finger.value = 0.88
        self.base.SendGripperCommand(gripper_command)
        time.sleep(1)

    def open_gripper(self):
        # Function to open the gripper
        gripper_command = Base_pb2.GripperCommand()
        finger = gripper_command.gripper.finger.add()
        gripper_command.mode = Base_pb2.GRIPPER_SPEED
        finger.value = 0.1  # Full open
        self.base.SendGripperCommand(gripper_command)
        gripper_request = Base_pb2.GripperRequest()

        # Wait for reported position to be opened
        gripper_request.mode = Base_pb2.GRIPPER_POSITION
        while True:
            gripper_measure = self.base.GetMeasuredGripperMovement(gripper_request)
            if len (gripper_measure.finger):
                print("Current position is : {0}".format(gripper_measure.finger[0].value))
                if gripper_measure.finger[0].value < 0.7:
                    break
            else: # Else, no finger present in answer, end loop
                break


def main():
    # Import the utilities helper module
    import argparse
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    import utilities

    # Parse arguments
    parser = argparse.ArgumentParser()
    args = utilities.parseConnectionArguments(parser)

    # Create connection to the device and get the router
    with utilities.DeviceConnection.createTcpConnection(args) as router:
        example = GripperCommandExample(router)
        move_arm_to_chess_pos2(example.base,"d4")
        example.pick_chess_piece(target_z=0.049)  # Example pick
        time.sleep(2)
        move_arm_to_chess_pos2(example.base,"d8")
        example.place_chess_piece(target_z=0.049)  # Example place


if __name__ == "__main__":
    main()
