import numpy as np
from move_to_x_y import move_to_cartesian_position
import utilities
from kortex_api.autogen.client_stubs.BaseClientRpc import BaseClient
from kortex_api.autogen.messages import Base_pb2
import cv2
from move import example_move_to_home_position
import time

# Real-world coordinates of the reference positions
real_world_coords = np.array([
    [0.489, -0.188, 0.03],  # A1
    [0.175, -0.171, 0.025],  # A8
    [0.503, 0.133,  0.03],  # H1
    [0.183, 0.143,  0.025], # H8
])

# Logical positions on the chessboard (column, row)
logical_coords = np.array([
    [0, 0],  # A1
    [0, 7],  # A8
    [7, 0],  # H1
    [7, 7],  # H8
], dtype=np.float32)

# # Compute the homography matrix
# homography_matrix, _ = cv2.findHomography(logical_coords, real_world_coords)

# # Function to calculate real-world coordinates for a given chess position
# def get_real_world_coordinates(chess_position):
#     # Convert chess position to logical grid coordinates
#     file = ord(chess_position[0].upper()) - ord('A')  # File (column index)
#     rank = int(chess_position[1]) - 1                # Rank (row index)
#     logical_point = np.array([[file, rank]], dtype=np.float32)
    
#     # Add a third coordinate for homogenous transformation
#     logical_point = np.array([file, rank, 1.0]).reshape(-1, 1)
    
#     # Transform to real-world coordinates
#     real_point = np.dot(homography_matrix, logical_point)
#     real_point /= real_point[2]  # Normalize by the third coordinate
#     real_point=real_point.flatten()
#     return float(real_point[0]), float(real_point[1])  # x, y in real-world coordinates

# Compute the homography matrix for x and y coordinates only
homography_matrix, _ = cv2.findHomography(logical_coords, real_world_coords[:, :2])

# Function to calculate real-world coordinates for a given chess position
def get_real_world_coordinates(chess_position):
    # Convert chess position to logical grid coordinates
    file = ord(chess_position[0].upper()) - ord('A')  # File (column index)
    rank = int(chess_position[1]) - 1                # Rank (row index)
    logical_point = np.array([file, rank, 1.0]).reshape(-1, 1)  # Homogeneous coords
    
    # Transform to real-world x, y coordinates
    real_point = np.dot(homography_matrix, logical_point)
    real_point /= real_point[2]  # Normalize by the third coordinate (homogeneous scaling)
    real_point=real_point.flatten()
    real_x, real_y = real_point[0], real_point[1]
    
    # Compute z-coordinate by interpolation from reference points
    distances = np.linalg.norm(logical_coords - np.array([file, rank]), axis=1)
    closest_index = np.argmin(distances)
    real_z = real_world_coords[closest_index, 2]
    
    return float(real_x), float(real_y), float(real_z)  # x, y, z in real-world coordinates

# Function to move the Kinova arm
def move_arm_to_chess_pos1(chessboard_pos,z=0.1):
    """Move the Kinova arm to the given chessboard position (e.g., 'e4')."""

    # Convert the grid index to real-world coordinates
    real_x, real_y, real_z = get_real_world_coordinates(chessboard_pos)

    # Parse arguments
    args = utilities.parseConnectionArguments()
    
    # Create connection to the device and get the router
    with utilities.DeviceConnection.createTcpConnection(args) as router:
        # Create required services
        base = BaseClient(router)
        # move to middle(base)
        move_arm_to_chess_pos2(base,'e4')
        move_to_cartesian_position(base, real_x, real_y,z)

# Function to move the Kinova arm
def move_arm_to_chess_pos2(base,chessboard_pos,z=0.1):
    """Move the Kinova arm to the given chessboard position (e.g., 'e4')."""

    # Convert the grid index to real-world coordinates
    real_x, real_y, real_z = get_real_world_coordinates(chessboard_pos)

    # example_move_to_home_position(base)
    move_to_cartesian_position(base, real_x, real_y,z)
    # return  real_z  

# move_arm_to_chess_pos1('a8',z=0.005)

 # Parse arguments
# args = utilities.parseConnectionArguments()

# with utilities.DeviceConnection.createTcpConnection(args) as router:
#         # Create required services
#         base = BaseClient(router)
#         move_arm_to_chess_pos2(base,'e4')
#         move_arm_to_chess_pos2(base,'e8',z=0.1)
#         move_arm_to_chess_pos2(base,'e8',z=0.022)