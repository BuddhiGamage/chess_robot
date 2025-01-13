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
from arm import move_arm_to_chess_pos2,get_real_world_coordinates
import utilities
import argparse
from pick_and_place import pick_chess_piece,place_chess_piece,close_gripper
from photo import capture_image_from_realsense
from chess_board_extract import extract_chessboard

from rf2 import chessboard_to_matrix
from return_move import find_chess_move


snap="chess_board_snap.jpg"
extracted_board="extracted_chessboard.jpg"
extracted_board_with_no_border="extracted_chessboard_no_border.jpg"
bucket_coordinates_x = 0.258
bucket_coordinates_y = 0.292

home_x=0.13
home_y=-0.069
home_z=0.1

# Parse arguments
parser = argparse.ArgumentParser()
args = utilities.parseConnectionArguments(parser)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# Initialize the chess board
board = chess.Board()
piece_count=32
castling_availability=True

prev_board = [
    [9, 7, 8, 10, 11, 8, 7, 9],
    [6, 6, 6, 6, 6, 6, 6, 6],
    [-1, -1, -1, -1, -1, -1, -1, -1],
    [-1, -1, -1, -1, -1, -1, -1, -1],
    [-1, -1, -1, -1, -1, -1, -1, -1],
    [-1, -1, -1, -1, -1, -1, -1, -1],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [3, 1, 2, 5, 4, 2, 1, 3]
]

# #test_board
# prev_board = [
#     [9, 7, 8, 10, 11, 8, 7, 9],
#     [6, 6, 6, 6, 6, 6, 6, 6],
#     [-1, -1, -1, -1, -1, -1, -1, -1],
#     [-1, -1, -1, -1, -1, -1, -1, -1],
#     [-1, -1, -1, -1, -1, -1, -1, -1],
#     [-1, -1, -1, -1, -1, -1, -1, -1],
#     [0, 0, 0, 0, 0, 0, 0, 0],
#     [3, -1, -1, -1, 4, 2, 1, 3]
# ]

# Use the Stockfish engine for AI moves (make sure it's installed and available on your system)
engine_path = "/usr/games/stockfish"  # Replace with the actual path to Stockfish


def board_to_matrix(board):
    # Map pieces to numeric values
    piece_to_value = {
        'p': 6, 'r': 9, 'n': 7, 'b': 8, 'q': 10, 'k': 11,  # Black pieces
        'P': 0, 'R': 3, 'N': 1, 'B': 2, 'Q': 5, 'K': 4,    # White pieces
        None: -1  # Empty squares
    }
    
    # Convert the board to a matrix
    matrix = []
    for square in chess.SQUARES:  # Loop through all squares (a1-h8)
        piece = board.piece_at(square)  # Get the piece on the square
        piece_symbol = piece.symbol() if piece else None  # Get piece symbol or None
        if square % 8 == 0:  # Start of a new row
            matrix.append([])  # Add a new row to the matrix
        matrix[-1].append(piece_to_value[piece_symbol])  # Add the value to the matrix
    
    # Reverse rows to place black pieces on top
    matrix.reverse()
    
    return matrix



# Create connection to the device and get the router
with utilities.DeviceConnection.createTcpConnection(args) as router:
    base = BaseClient(router)

    # with chess.engine.SimpleEngine.popen_uci(engine_path) as engine:
    engine = chess.engine.SimpleEngine.popen_uci(engine_path)
    print("Welcome to Chess! Enter your moves in UCI notation (e.g., e2e4). Type 'quit' to exit.")

    move_arm_to_position(base, home_x, home_y, home_z) # home pose before taking the snap of the chess board
    close_gripper(base)
    time.sleep(3)

    while not board.is_game_over():
        # Display the board
        print(board)

        # oppent will play as white and do the first move and press n.
        user_input = input("Press enter after move")

        # move_arm_to_chess_pos2(base,'e4')
        # time.sleep(1)

        # generate fen from the image
        move_arm_to_position(base, home_x, home_y, home_z) # home pose before taking the snap of the chess board
        time.sleep(3)
        capture_image_from_realsense(snap) # taking the snap

        img_board=extract_chessboard(snap)

        cv2.imwrite(extracted_board, img_board)

        current_board,count=chessboard_to_matrix(extracted_board)
        while count!=piece_count and count!=piece_count-1:
            print(piece_count)
            capture_image_from_realsense(snap) # taking the snap
            img_board=extract_chessboard(snap)
            cv2.imwrite(extracted_board, img_board)
            current_board,count=chessboard_to_matrix(extracted_board)

        # Get the human player's move
        print(prev_board)
        print(current_board)
        human_move,is_capture,castling_availability=find_chess_move(prev_board,current_board,castling_availability)
        
        print("human move: ", human_move)

        print('castling availability: '+str(castling_availability))

        
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
        
        if(is_capture):
            piece_count-=1
            print(is_capture)
            # print('quit in if')
            # quit()
        print(human_move)

        # Check if the game is over after the human move
        if board.is_game_over():
            break

        # Let the AI make its move
        print("AI is thinking...")
        result = engine.play(board, chess.engine.Limit(time=1.0))  # AI moves with a 1-second time limit
        
        # Extract the move details
        ai_move = result.move
        
        print("AI move:", result.move)
        
        # # Determine the given move is a castling move
        # black_kingside = chess.Move.from_uci("e8g8")  # Black kingside castling
        # black_queenside = chess.Move.from_uci("e8c8")  # Black queenside castling
        
        # ai_move = black_kingside

        # Check if the move is kingside or queenside castling
        if board.is_castling(ai_move):
            
            if board.is_kingside_castling(ai_move):
                # Rook's move: h8 -> f8
                rook_source_pos = 'h8'
                rook_target_pos = 'f8'
            elif board.is_queenside_castling(ai_move):
                # Rook's move: a8 -> d8
                rook_source_pos = 'a8'
                rook_target_pos = 'd8'
            
            # Perform the AI's move    
            move_arm_to_chess_pos2(base,'e4')

            time.sleep(1)
            _,_,target_z = get_real_world_coordinates(rook_source_pos)
            print(target_z)
            move_arm_to_chess_pos2(base,rook_source_pos)
            time.sleep(1)
            pick_chess_piece(base,target_z)  # pick

            move_arm_to_chess_pos2(base,'e4')
            
            time.sleep(1)
            move_arm_to_chess_pos2(base,rook_target_pos)
            time.sleep(1)
            place_chess_piece(base,target_z)  # place

            
        # Determine the source and target squares of the move
        source_square = ai_move.from_square  # Starting square index (0-63)
        target_square = ai_move.to_square    # Ending square index (0-63)

        # Convert to algebraic notation (e.g., 'e2', 'e4')
        source_pos = chess.square_name(source_square)  # e.g., 'e2'
        target_pos = chess.square_name(target_square)  # e.g., 'e4'

        # Check if the target square contains an opponent's piece (indicates a capture)
        # capture_move = chess.Move.from_uci(str(ai_move))  # check capturing 
        
        if board.is_capture(ai_move): 
            piece_count-=1   
            captured_square = chess.square_name(ai_move.to_square)

            print(f"The AI move captures a piece on {captured_square}.")

            # Move the arm to the captured piece's position (captured_square)
            move_arm_to_chess_pos2(base,'e4')
            # move_arm_to_position(base, home_x, home_y, home_z) # home pose
            time.sleep(1)
            _,_,target_z = get_real_world_coordinates(captured_square)
            move_arm_to_chess_pos2(base, captured_square)
            time.sleep(1)
            pick_chess_piece(base,target_z) 

            # Move the arm to the bucket (replace with actual bucket coordinates)
            # bucket_coordinates = 'h1'  # Example bucket position (change as needed)
            move_arm_to_position(base,bucket_coordinates_x,bucket_coordinates_y)
            time.sleep(2)
            place_chess_piece(base,target_z=0.1)  # Example place


        # Perform the AI's move    
        move_arm_to_chess_pos2(base,'e4')

        # move_arm_to_position(base, home_x, home_y, home_z) # home pose before taking the snap of the chess board
        time.sleep(1)
        _,_,target_z = get_real_world_coordinates(source_pos)
        print(target_z)
        move_arm_to_chess_pos2(base,source_pos)
        time.sleep(1)
        pick_chess_piece(base,target_z)  # Example pick

        move_arm_to_chess_pos2(base,'e4')
        # move_arm_to_position(base, home_x, home_y, home_z) # home pose before taking the snap of the chess board
        time.sleep(1)
        move_arm_to_chess_pos2(base,target_pos)
        time.sleep(1)
        place_chess_piece(base,target_z)  # Example place

        move_arm_to_position(base, home_x, home_y, home_z) # home pose before taking the snap of the chess board
        time.sleep(3)

        # Push the move on the board to update the state
        board.push(ai_move)

        # Convert the board to a matrix
        prev_board = board_to_matrix(board)

        
        

# Display the game result
print("Game over!")
print("Result:", board.result())

