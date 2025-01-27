import speech_recognition as sr
from gtts import gTTS

import chess
import chess.engine
from ollama import chat, ChatResponse
import time
import threading

import cv2
from rf2 import chessboard_to_matrix
from move_to_x_y import move_to_cartesian_position as move_arm_to_position
from photo import capture_image_from_realsense
from chess_board_extract import extract_chessboard
from return_move import find_chess_move

import sys
import os
from kortex_api.autogen.client_stubs.BaseClientRpc import BaseClient
from kortex_api.autogen.messages import Base_pb2
from arm import move_arm_to_chess_pos2,get_real_world_coordinates
import utilities
import argparse
from pick_and_place import pick_chess_piece,place_chess_piece,close_gripper

# Stockfish Path Configuration
STOCKFISH_PATH = "/usr/games/stockfish"

# Initialize Chess Engine
board = chess.Board()
engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)

# Separate Game History Lists
human_moves = []
ai_moves = []
game_history = []

# Shared State for Communication
lock = threading.Lock()
human_move_detected = threading.Event()
# Event to signal when input is needed in detect_and_process_human_move
input_event = threading.Event()

# Create an event to signal when arm is running
is_ai_moving = threading.Event()

piece_count=32
castling_availability=True
home_x, home_y, home_z = 0.13, -0.069, 0.1
bucket_coordinates_x, bucket_coordinates_y = 0.258, 0.292

snap="chess_board_snap.jpg"
extracted_board="extracted_chessboard.jpg"
extracted_board_with_no_border="extracted_chessboard_no_border.jpg"
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



# Function to recognize speech
def listen_to_user():
    recognizer = sr.Recognizer()

    # Use the microphone to capture the user's speech
    with sr.Microphone() as source:
        print("Listening... Please say something.")
        recognizer.adjust_for_ambient_noise(source)  # Adjusts for ambient noise
        audio = recognizer.listen(source)

    # Recognize the speech using Google Speech Recognition
    try:
        print("Recognizing... Please wait.")
        user_input = recognizer.recognize_google(audio)
        print(f"You said: {user_input}")
        return user_input
    except sr.UnknownValueError:
        print("Sorry, I could not understand the audio.")
        return None
    except sr.RequestError:
        print("Sorry, the service is unavailable.")
        return None

# Function to convert text to speech using gTTS
def convert_to_speech(text):
    if text:
        tts = gTTS(text=text, lang='en')
        tts.save("response.mp3")  # Save the audio to a file
        os.system("mpg321 response.mp3")
        # playsound("response.mp3")  # Play the audio file

#  compare the two lists and check if all numbers greater than 5(which means black positions) are in the same positions in both lists
def check_black_positions(prev_board, new_board):
    print(prev_board)
    print(new_board)
    # Iterate through each row and column
    for i in range(len(prev_board)):
        for j in range(len(prev_board[i])):
            # Check if both lists have numbers > 6 in the same position
            if (prev_board[i][j] > 5) or (new_board[i][j] > 5 ):
                # if human player replaced the piece with his piece then ignore checking
                if(new_board[i][j]<6):
                    continue
                if prev_board[i][j] != new_board[i][j]:
                    return False
    return True

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

def get_best_move(fen: str) -> str:
    global board
    """Get the best move from Stockfish."""
    with engine.analysis(board) as analysis:
        best_move = engine.play(board, chess.engine.Limit(time=0.1))
    return best_move.move


def generate_llm_response(prompt: str) -> str:
    """Send a prompt to the LLM using Ollama and get a response."""
    response: ChatResponse = chat(model="mistral", messages=[
        {"role": "user", "content": prompt}
    ])
    return response.message.content  # Return the LLM's response


def process_human_move(move: str):
    global board
    """Process and validate a human chess move."""
    global human_move_detected
    if board.is_legal(move):
        with lock:
            board.push(move)
            human_moves.append(str(move))  # Record human move in history
            game_history.append(f"Human: {str(move)}")  # Combined history
            print(f"Human moved: {str(move)}")
        human_move_detected.set()  # Notify the AI to make its move
    else:
        print("Illegal move. Try again.")


def ai_make_move(base):
    """AI calculates and makes its move."""
    global board, human_move_detected

    while not board.is_game_over():
        # Wait for human move to be detected
        human_move_detected.wait()
        human_move_detected.clear()

        # AI calculates and plays its move
        with lock:
            best_move = get_best_move(board.fen())
            # board.push(chess.Move.from_uci(best_move))
            # ai_moves.append(best_move)  # Record AI move in history
            # game_history.append(f"AI: {best_move}")  # Combined history
            # print(f"AI moved: {best_move}")

            # Notify robotic arm to execute the move
            update_physical_board(best_move, base)
        


def update_physical_board(ai_move: str, base):
    global board, is_ai_moving, piece_count, bucket_coordinates_x, bucket_coordinates_y, snap, extracted_board, img_board, prev_board
    
    is_ai_moving.set()

    """Send AI's move to the robotic arm."""
    print(f"Robotic arm executing move: {ai_move.uci()}")
    
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
        if board.is_en_passant(ai_move):
            captured_square = chess.square(chess.square_file(ai_move.to_square), chess.square_rank(ai_move.from_square))   
        else:
            captured_square = ai_move.to_square
        captured_square = chess.square_name(captured_square)

        print(f"The AI move captures a piece on {captured_square}.")

        # Move the arm to the captured piece's position (captured_square)
        # move_arm_to_chess_pos2(base,base_square)
        # move_arm_to_position(base, home_x, home_y, home_z) # home pose
        # time.sleep(1)
        _,_,target_z = get_real_world_coordinates(captured_square)
        move_arm_to_chess_pos2(base, captured_square)
        time.sleep(3)
        pick_chess_piece(base,target_z) 

        # Move the arm to the bucket (replace with actual bucket coordinates)
        # bucket_coordinates = 'h1'  # Example bucket position (change as needed)
        move_arm_to_position(base,bucket_coordinates_x,bucket_coordinates_y)
        time.sleep(3)
        place_chess_piece(base,target_z=0.14)  # Example place
        # check arm did the move
        capture_image_from_realsense(snap) # taking the snap
        img_board=extract_chessboard(snap)
        cv2.imwrite(extracted_board, img_board)
        _,count=chessboard_to_matrix(extracted_board)
        while count!=piece_count:
            if(count-1==piece_count):
                print(f"please help me to capture the piece: {captured_square}")
            print(piece_count)
            capture_image_from_realsense(snap) # taking the snap
            img_board=extract_chessboard(snap)
            cv2.imwrite(extracted_board, img_board)
            current_board,count=chessboard_to_matrix(extracted_board)


    # Perform the AI's move    

    _,_,target_z = get_real_world_coordinates(source_pos)
    print(target_z)
    move_arm_to_chess_pos2(base,source_pos)
    time.sleep(3)
    pick_chess_piece(base,target_z)  # Example pick

    move_arm_to_chess_pos2(base,target_pos)
    time.sleep(3)
    place_chess_piece(base,target_z)  # Example place

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

        _,_,target_z = get_real_world_coordinates(rook_source_pos)
        print(target_z)
        move_arm_to_chess_pos2(base,rook_source_pos)
        time.sleep(3)
        pick_chess_piece(base,target_z)  # pick

        move_arm_to_chess_pos2(base,rook_target_pos)
        time.sleep(3)
        place_chess_piece(base,target_z)  # place
        
    move_arm_to_position(base, home_x, home_y, home_z) # home pose before taking the snap of the chess board
    time.sleep(3)

    # AI calculates and plays its move
    board.push(ai_move)
    ai_moves.append(str(ai_move))  # Record AI move in history
    game_history.append(f"AI: {str(ai_move)}")  # Combined history
    print(f"AI moved: {str(ai_move)}")

    # Convert the board to a matrix
    prev_board = board_to_matrix(board)

    # check arm did the move
    capture_image_from_realsense(snap) # taking the snap
    img_board=extract_chessboard(snap)
    cv2.imwrite(extracted_board, img_board)
    current_board,count=chessboard_to_matrix(extracted_board)
    print(current_board)
    while count!=piece_count and count!=piece_count-1:
        print(piece_count)
        capture_image_from_realsense(snap) # taking the snap
        img_board=extract_chessboard(snap)
        cv2.imwrite(extracted_board, img_board)
        current_board,count=chessboard_to_matrix(extracted_board)
    
    arm_move_state=check_black_positions(prev_board,current_board)
    print("Arm movement state: "+str(arm_move_state))
    # quit()
    while (arm_move_state==False):
        print(f"Can you please fix my move to: {ai_move}")
        time.sleep(2)
        # check arm did the move
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
        arm_move_state = check_black_positions(prev_board,current_board)
    
    is_ai_moving.clear()  # Reset the flag after AI completes its move
    print("AI move complete.")
    # quit()


def continuous_chat_and_moves():
    global board
    """Main loop for interacting with the human player."""
    print("You can make a move (in UCI notation) or ask a question!")
    while not board.is_game_over():
        if input_event.is_set():
            print("Waiting for human move input...")
            input_event.wait()  # Wait for input from human move detection before continuing
        else:
            # Regular interaction loop
            # user_input = input("Your input (Detected move or question): ").strip()
            user_input = listen_to_user()

        # Generate LLM response for a question
        with lock:
            print(board.fen())
            print(game_history)
            prompt = f"""
            You are a chess playing robot
            Current chessboard configuration (FEN): {board.fen()}
            Game History: {game_history}
            Human question: {user_input}
            Respond briefly in one or two sentences appropriately based on the game context and the question.
            """
        response = generate_llm_response(prompt)
        print(f"AI: {response}")
        convert_to_speech(response)

def detect_and_process_human_move(base):
    
    # global human_move_detected, prev_board
    global board, is_ai_moving, prev_board, piece_count, castling_availability, home_x, home_y, home_z, snap, extracted_board, img_board
    
    while not board.is_game_over():
        # Check if AI is currently making a move
        if is_ai_moving.is_set():
            print("AI is currently making a move. Waiting for AI to complete...")
            time.sleep(1)
            is_ai_moving.wait()
            continue
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
        # Check if they are the same
        if prev_board == current_board:
            print("Player's turn")
            continue # Exit the function if no move is detected


        human_move,castling_availability=find_chess_move(prev_board,current_board,castling_availability)
        
        if human_move==None:
            print("Move did not Capture. Try again")
            continue # Exit the function if move detection failed
        
        print(f"Human move detected: {human_move}")
        print(f"Castling availability updated: {castling_availability}")

        # Attempt to parse and validate the human move
        try:
            human_move_prueba = chess.Move.from_uci(human_move)

            if human_move_prueba in board.legal_moves:
                if board.is_capture(human_move_prueba):
                    piece_count -= 1
                    print("Capture move detected by human.")
                process_human_move(human_move_prueba)
            elif chess.Move.from_uci(human_move + "q") in board.legal_moves:
                # Handle pawn promotion
                while True:
                    input_event.set()  # Signal that input is needed
                    # promotion_piece = input("Pawn promotion! Choose a piece (q, r, b, n): ").lower()
                    convert_to_speech("Pawn promotion! Choose a piece (q, r, b, n): ")
                    promotion_piece=listen_to_user()
                    if promotion_piece in ["q", "r", "b", "n"]:
                        break
                    else:
                        print("Invalid input. Choose q (queen), r (rook), b (bishop), or n (knight).")
                
                input_event.clear()  # Reset the event after processing the input
                human_move += promotion_piece
                human_move_prueba = chess.Move.from_uci(human_move)

                if human_move_prueba in board.legal_moves:
                    if board.is_capture(human_move_prueba):
                        piece_count -= 1
                        print("Capture move detected by human.")
                    print(f"Pawn promoted to: {promotion_piece}")
                    process_human_move(human_move_prueba)
                else:
                    print("Illegal move with promotion. Please try again.")
                    continue
            else:
                print("Illegal move. Please try again.")
                continue
        except ValueError:
            print("Invalid UCI format. Please try again.")
            continue


# Run the System
def main():
    print("Welcome to Chess with Embodied AI!")
    print("Type your moves in UCI notation (e.g., e2e4) or ask me a question!")
    print("The AI will respond to your inputs and make moves using a robotic arm.")
    print("Let's play!")

    # convert_to_speech("Welcome to Chess with Embodied AI! Type your moves in UCI notation (e.g., e2e4) or ask me a question! The AI will respond to your inputs and make moves using a robotic arm.")
    convert_to_speech("Let's play!")


    # convert_to_speech
    # Parse arguments
    parser = argparse.ArgumentParser()
    args = utilities.parseConnectionArguments(parser)
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

    # Create connection to the device and get the router
    with utilities.DeviceConnection.createTcpConnection(args) as router:
        base = BaseClient(router)

        move_arm_to_position(base, home_x, home_y, home_z) # home pose before taking the snap of the chess board
        close_gripper(base)
        time.sleep(3)

        # Simulate human move detection in a separate thread
        threading.Thread(target=detect_and_process_human_move, args=(base,), daemon=True).start()
        
        # Start AI move thread
        threading.Thread(target=ai_make_move, args=(base,), daemon=True).start()

        # Run the interactive chat and move processing loop
        # threading.Thread(target=continuous_chat_and_moves, daemon=True).start()
        continuous_chat_and_moves()

        # Game Over
        print("Game over!")
        print(f"Result: {board.result()}")


if __name__ == "__main__":
    main()
