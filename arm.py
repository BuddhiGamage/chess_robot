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
    [0.491, -0.225],  # A1
    [0.156, -0.198],  # A8
    [0.511, 0.117],  # H1
    [0.172, 0.139], # H8
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


# Function to move the Kinova arm
def move_arm_to_chess_pos1(chessboard_pos,z=0.2):
    """Move the Kinova arm to the given chessboard position (e.g., 'e4')."""

    # Convert the grid index to real-world coordinates
    real_x, real_y = get_real_world_coordinates(chessboard_pos)

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
def move_arm_to_chess_pos2(base,chessboard_pos,z=0.2):
    """Move the Kinova arm to the given chessboard position (e.g., 'e4')."""

    # Convert the grid index to real-world coordinates
    real_x, real_y = get_real_world_coordinates(chessboard_pos)

    # example_move_to_home_position(base)
    move_to_cartesian_position(base, real_x, real_y,z)    


move_arm_to_chess_pos1('b3',z=0.015)