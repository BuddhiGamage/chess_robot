import numpy as np
from move_to_x_y import move_to_cartesian_position
import utilities
from kortex_api.autogen.client_stubs.BaseClientRpc import BaseClient
from kortex_api.autogen.messages import Base_pb2
import cv2

# # Define the chessboard coordinates (0 to 7 for an 8x8 board)
# chessboard_coords = np.array([
#     [0, 0], [0, 7], [7, 0], [7, 7], [3, 3]  # A1, A8, H1, H8, D4
# ])

# # Define the corresponding real-world coordinates (in meters, replace with actual values)
# real_world_coords = np.array([
#     [0.147, 0.182], [0.496, 0.163], [0.13, -0.148], [0.469, -0.182], [0.284, 0.028]  # A1, A8, H1, H8, D4
# ])

# # Set up the system of equations to solve for the transformation matrix
# A = []
# B = []
# for i in range(5):
#     cx, cy = chessboard_coords[i]
#     rx, ry = real_world_coords[i]
#     A.append([cx, cy, 1, 0, 0, 0])
#     A.append([0, 0, 0, cx, cy, 1])
#     B.append(rx)
#     B.append(ry)

# A = np.array(A)
# B = np.array(B)

# # Solve for transformation parameters (a, b, c, d, tx, ty)
# params = np.linalg.lstsq(A, B, rcond=None)[0]
# a, b, c, d, tx, ty = params

# # Apply the transformation to all squares (0, 0) to (7, 7)
# board_coords = []
# for x in range(8):
#     for y in range(8):
#         real_x = a*x + b*y + tx
#         real_y = c*x + d*y + ty
#         board_coords.append([real_x, real_y])

# print("Real-world coordinates of all squares:")
# print(board_coords)

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


# Real-world coordinates of the reference positions
real_world_coords = np.array([
    [0.147, 0.182],  # A1
    [0.496, 0.163],  # A8
    [0.13, -0.148],  # H1
    [0.469, -0.182], # H8
])

# Logical positions on the chessboard (column, row)
logical_coords = np.array([
    [0, 0],  # A1
    [0, 7],  # A8
    [7, 0],  # H1
    [7, 7],  # H8
], dtype=np.float32)

# Compute the homography matrix
homography_matrix, _ = cv2.findHomography(logical_coords, real_world_coords)

# Function to calculate real-world coordinates for a given chess position
def get_real_world_coordinates(chess_position):
    # Convert chess position to logical grid coordinates
    file = ord(chess_position[0].upper()) - ord('A')  # File (column index)
    rank = int(chess_position[1]) - 1                # Rank (row index)
    logical_point = np.array([[file, rank]], dtype=np.float32)
    
    # Add a third coordinate for homogenous transformation
    logical_point = np.array([file, rank, 1.0]).reshape(-1, 1)
    
    # Transform to real-world coordinates
    real_point = np.dot(homography_matrix, logical_point)
    real_point /= real_point[2]  # Normalize by the third coordinate
    real_point=real_point.flatten()
    return float(real_point[0]), float(real_point[1])  # x, y in real-world coordinates

# # Define a function to convert chessboard notation to grid indices
# def chessboard_to_index(chessboard_pos):
#     """Convert chessboard notation (e.g., 'e4') to grid indices (row, column)."""
#     column_mapping = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
#     row_mapping = {'1': 7, '2': 6, '3': 5, '4': 4, '5': 3, '6': 2, '7': 1, '8': 0}
    
#     column = chessboard_pos[0].lower()  # 'e' from 'e4'
#     row = chessboard_pos[1]  # '4' from 'e4'
    
#     # Get the column and row indices
#     column_index = column_mapping[column]
#     row_index = row_mapping[row]
    
#     return row_index, column_index

# # Function to transform chessboard grid to real-world coordinates
# def chessboard_to_real_world(row, col):
#     """Convert chessboard grid (row, col) to real-world coordinates."""
#     real_x = a * col + b * row + tx
#     real_y = c * col + d * row + ty
#     return real_x, real_y

# Function to move the Kinova arm
def move_arm_to_chess_pos(chessboard_pos):
    """Move the Kinova arm to the given chessboard position (e.g., 'e4')."""
    # # Convert chessboard position (e.g., 'e4') to grid index (row, col)
    # row, col = chessboard_to_index(chessboard_pos)
    # print(row)
    # print(col)

    # Convert the grid index to real-world coordinates
    real_x, real_y = get_real_world_coordinates(chessboard_pos)
    
    print(real_x)

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
        move_to_cartesian_position(base, real_x, real_y,z=0.15)
    
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

move_arm_to_chess_pos('d1')