import chess
import chess.engine
import chess.svg

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
from pick_and_place import pick_chess_piece,place_chess_piece
from photo import capture_image_from_realsense
from chess_board_extract import extract_chessboard

from rf2 import chessboard_to_matrix
from return_move import find_chess_move


snap="chess_board_snap.jpg"
extracted_board="extracted_chessboard.jpg"
extracted_board_with_no_border="extracted_chessboard_no_border.jpg"
bucket_coordinates_x = 0.157
bucket_coordinates_y = 0.319

# Parse arguments
parser = argparse.ArgumentParser()
args = utilities.parseConnectionArguments(parser)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# Initialize the chess board
board = chess.Board()
board.clean_castling_rights()
piece_count=32

prev_board = [
    [3, 1, 2, 3, 5, 2, 1, 3],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [-1, -1, -1, -1, -1, -1, -1, -1],
    [-1, -1, -1, -1, -1, -1, -1, -1],
    [-1, -1, -1, -1, -1, -1, -1, -1],
    [-1, -1, -1, -1, -1, -1, -1, -1],
    [6, 6, 6, 6, 6, 6, 6, 6],
    [9, 7, 8, 11, 10, 8, 7, 9]
]

# Use the Stockfish engine for AI moves (make sure it's installed and available on your system)
engine_path = "/usr/games/stockfish"  # Replace with the actual path to Stockfish

# Create connection to the device and get the router
with utilities.DeviceConnection.createTcpConnection(args) as router:
    base = BaseClient(router)

    # with chess.engine.SimpleEngine.popen_uci(engine_path) as engine:
    engine = chess.engine.SimpleEngine.popen_uci(engine_path)
    print("Welcome to Chess! Enter your moves in UCI notation (e.g., e2e4). Type 'quit' to exit.")

    while not board.is_game_over():
        # Display the board
        print(board)

        # oppent will play as white and do the first move and press n.
        user_input = input("Press enter after move")

        move_arm_to_chess_pos2(base,'e4')
        time.sleep(1)

        # generate fen from the image
        move_arm_to_position(base, 0.077,0.127, 0.15) # home pose before taking the snap of the chess board
        time.sleep(3)

        capture_image_from_realsense(snap) # taking the snap

        img_board=extract_chessboard(snap)

        cv2.imwrite(extracted_board, img_board)

        current_board,count=chessboard_to_matrix(extracted_board)
        while count!=piece_count:
            capture_image_from_realsense(snap) # taking the snap
            img_board=extract_chessboard(snap)
            cv2.imwrite(extracted_board, img_board)
            current_board,count=chessboard_to_matrix(extracted_board)

        # Get the human player's move
        human_move,is_capture=find_chess_move(prev_board,current_board)

        if(is_capture):
            piece_count-=1
        print(human_move)

        
        try:
            # Parse and apply the human player's move
            move = chess.Move.from_uci(human_move)
            if move in board.legal_moves:
                board.push(move)
            else:
                print("Illegal move. Try again.")
                continue
        except ValueError:
            print("Invalid UCI format. Try again.")
            continue

        # Check if the game is over after the human move
        if board.is_game_over():
            break

        # Let the AI make its move
        print("AI is thinking...")
        result = engine.play(board, chess.engine.Limit(time=1.0))  # AI moves with a 1-second time limit
        
        # Extract the move details
        ai_move = result.move
        print("AI move:", result.move)

        # Determine the source and target squares of the move
        source_square = ai_move.from_square  # Starting square index (0-63)
        target_square = ai_move.to_square    # Ending square index (0-63)

        # Convert to algebraic notation (e.g., 'e2', 'e4')
        source_pos = chess.square_name(source_square)  # e.g., 'e2'
        target_pos = chess.square_name(target_square)  # e.g., 'e4'

        # Check if the target square contains an opponent's piece (indicates a capture)
        capture_move = chess.Move.from_uci(ai_move)  # check capturing 
        
        if board.is_capture(capture_move): 
            piece_count-=1   
            captured_square = chess.square_name(capture_move.to_square)

            print(f"The AI move captures a piece on {captured_square}.")

            # Move the arm to the captured piece's position (captured_square)
            move_arm_to_chess_pos2(base,'e4')
            time.sleep(1)
            target_z = move_arm_to_chess_pos2(base, captured_square)
            time.sleep(1)
            pick_chess_piece(base,target_z) 

            # Move the arm to the bucket (replace with actual bucket coordinates)
            # bucket_coordinates = 'h1'  # Example bucket position (change as needed)
            move_arm_to_position(base,bucket_coordinates_x,bucket_coordinates_y)
            time.sleep(2)
            place_chess_piece(base,target_z=0.8)  # Example place


        # Perform the AI's move    
        move_arm_to_chess_pos2(base,'e4')
        time.sleep(1)
        target_z = move_arm_to_chess_pos2(base,source_pos)
        time.sleep(1)
        pick_chess_piece(target_z)  # Example pick

        move_arm_to_chess_pos2(base,'e4')
        time.sleep(1)
        move_arm_to_chess_pos2(base,target_pos)
        time.sleep(1)
        place_chess_piece(target_z)  # Example place

        # Push the move on the board to update the state
        board.push(ai_move)

    # Display the game result
    print("Game over!")
    print("Result:", board.result())

