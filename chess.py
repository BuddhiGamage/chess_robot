
from stockfish import Stockfish
import sys
import os
import time
import cv2

from kortex_api.autogen.client_stubs.BaseClientRpc import BaseClient
from kortex_api.autogen.messages import Base_pb2
from move_to_x_y import move_to_cartesian_position as move_arm_to_position
from arm import move_arm_to_chess_pos2
import utilities
import argparse
from pick_and_place import Gripper
from photo import capture_image_from_realsense
from chess_board_extract import extract_chessboard,remove_border_and_resize

from return_fen import convert_to_fen, chessboard_to_matrix
from return_move import get_move


snap="chess_board_snap.jpg"
extracted_board="extracted_chessboard.jpg"
extracted_board_with_no_border="extracted_chessboard_no_border.jpg"


# Parse arguments
parser = argparse.ArgumentParser()
args = utilities.parseConnectionArguments(parser)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# initialize the fen using stockfish
# Initialize the Stockfish engine
stockfish = Stockfish()

stockfish.set_position([])

# Set the skill level (1-20, default is 20)
stockfish.set_skill_level(10)

ini_board = [
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0],  # initial position
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1]
]

prev_board = ini_board
# Create connection to the device and get the router
with utilities.DeviceConnection.createTcpConnection(args) as router:
    gripper = Gripper(router)

    # oppent will play as white and do the first move and press n.
    user_input = input("Press 'n' to proceed:")

    if user_input=='n':

        # generate fen from the image
        move_arm_to_position(gripper.base, 0.077,0.127, 0.15) # home pose before taking the snap of the chess board

        capture_image_from_realsense(snap) # taking the snap

        board=extract_chessboard(snap)

        cv2.imwrite(extracted_board, board)

        matrix=chessboard_to_matrix(extracted_board)
        current_board=get_current_board()
        prev=convert_to_fen(matrix)
        previous_fen=stockfish.get_fen_position()
        
        print(current_fen)
        print(matrix)
        print(previous_fen)

        move=get_move(prev_board,current_board)

        prev_board=get_current_board()

        # update the move
        stockfish.make_moves_from_current_position([move])
        
        # Get the best move from the current position
        best_move = stockfish.get_best_move()
        # best_move = 'g8f6'
        print("Best move:", best_move)


        pick = best_move[:2]  # First half
        place = best_move[2:]  # Second half
        
        move_arm_to_chess_pos2(gripper.base,'e4')
        move_arm_to_chess_pos2(gripper.base,pick)
        gripper.pick_chess_piece(target_z=0.049)  # Example pick
        time.sleep(2)
        move_arm_to_chess_pos2(gripper.base,'e4')
        move_arm_to_chess_pos2(gripper.base,place)
        gripper.place_chess_piece(target_z=0.049)  # Example place

    # # Set the initial position (FEN string) or start with a new game
    # stockfish.set_position(["e2e4", "e7e5", "g1f3", "b8c6"])

    # # Get the best move from the current position
    # best_move = stockfish.get_best_move()
    # print("Best move:", best_move)

    # # Evaluate the current position
    # evaluation = stockfish.get_evaluation()
    # print("Evaluation:", evaluation)

    # # Send the best move to Stockfish and update the position
    # stockfish.make_moves_from_current_position([best_move])

    # # Get the updated board state
    # print("Updated board:", stockfish.get_board_visual())



# loop


    # identify the move oppenet move

    # update the stockfish fen

    # predict the best move

    # do the move

    # wait for the opponent move

    # if checkmate or quit end.
