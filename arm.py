import numpy as np
from move_to_x_y import move_to_cartesian_position
import utilities
from kortex_api.autogen.client_stubs.BaseClientRpc import BaseClient
from kortex_api.autogen.messages import Base_pb2


# Define the chessboard coordinates (0 to 7 for an 8x8 board)
chessboard_coords = np.array([
    [0, 0], [0, 7], [7, 0], [7, 7], [3, 3]  # A1, A8, H1, H8, D4
])

# Define the corresponding real-world coordinates (in meters, replace with actual values)
real_world_coords = np.array([
    [0.147, 0.182], [0.496, 0.163], [0.13, -0.148], [0.469, -0.182], [0.284, 0.028]  # A1, A8, H1, H8, D4
])

# Set up the system of equations to solve for the transformation matrix
A = []
B = []
for i in range(5):
    cx, cy = chessboard_coords[i]
    rx, ry = real_world_coords[i]
    A.append([cx, cy, 1, 0, 0, 0])
    A.append([0, 0, 0, cx, cy, 1])
    B.append(rx)
    B.append(ry)

A = np.array(A)
B = np.array(B)

# Solve for transformation parameters (a, b, c, d, tx, ty)
params = np.linalg.lstsq(A, B, rcond=None)[0]
a, b, c, d, tx, ty = params

# Apply the transformation to all squares (0, 0) to (7, 7)
board_coords = []
for x in range(8):
    for y in range(8):
        real_x = a*x + b*y + tx
        real_y = c*x + d*y + ty
        board_coords.append([real_x, real_y])

print("Real-world coordinates of all squares:")
print(board_coords)

# import math
# from kortex_api import RobotServer, Session
# # from kortex_api.exceptions import *
# from kortex_api import types

# # Define the fixed Z-coordinate in meters
# Z_FIXED_METERS = 0.15  # Example Z value in meters (e.g., 0.15m)
# Z_FIXED = Z_FIXED_METERS * 1000  # Convert Z to millimeters

# # Initialize the Kortex API
# def initialize_kinova_arm():
#     try:
#         # Connect to the Kinova robot
#         robot = RobotServer("192.168.1.10")  # Replace with your robot's IP address
#         session = Session()
#         robot.start()
#         return robot, session
#     except Exception as e:
#         print("Error connecting to robot:", e)
#         return None, None

# Define a function to convert chessboard notation to grid indices
def chessboard_to_index(chessboard_pos):
    """Convert chessboard notation (e.g., 'e4') to grid indices (row, column)."""
    column_mapping = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
    row_mapping = {'1': 7, '2': 6, '3': 5, '4': 4, '5': 3, '6': 2, '7': 1, '8': 0}
    
    column = chessboard_pos[0].lower()  # 'e' from 'e4'
    row = chessboard_pos[1]  # '4' from 'e4'
    
    # Get the column and row indices
    column_index = column_mapping[column]
    row_index = row_mapping[row]
    
    return row_index, column_index

# Function to transform chessboard grid to real-world coordinates
def chessboard_to_real_world(row, col):
    """Convert chessboard grid (row, col) to real-world coordinates."""
    real_x = a * col + b * row + tx
    real_y = c * col + d * row + ty
    return real_x, real_y

# Function to move the Kinova arm
def move_arm_to_chess_pos(chessboard_pos):
    """Move the Kinova arm to the given chessboard position (e.g., 'e4')."""
    # Convert chessboard position (e.g., 'e4') to grid index (row, col)
    row, col = chessboard_to_index(chessboard_pos)
    
    # Convert the grid index to real-world coordinates
    real_x, real_y = chessboard_to_real_world(row, col)
    
    # # Convert to a Cartesian pose (X, Y, Z) and move the arm to the calculated position
    # target_pose = types.CartesianPose()
    # target_pose.x = real_x  # X in mm
    # target_pose.y = real_y  # Y in mm
    # target_pose.z = Z_FIXED  # Z in mm

    # Parse arguments
    args = utilities.parseConnectionArguments()
    
    # Create connection to the device and get the router
    with utilities.DeviceConnection.createTcpConnection(args) as router:
        # Create required services
        base = BaseClient(router)

        # Example core
        x = 0.147  # Replace with desired x-coordinate
        y = 0.182  # Replace with desired y-coordinate
        move_to_cartesian_position(base, real_x, real_y,z=0.01)
    
    # # Send the command to move the arm to the target pose
    # try:
    #     session.move_to_cartesian_pose(target_pose)
    #     print(f"Arm moved to chessboard position {chessboard_pos} -> Real-world coordinates: ({real_x}, {real_y}, {Z_FIXED})")
    # except Exception as e:
    #     print("Error moving arm:", e)

# # Example usage
# robot, session = initialize_kinova_arm()

# if robot and session:

    # move_arm_to_chess_pos(robot, session, "e4")  # Example to move to 'e4'

move_arm_to_chess_pos('a3')