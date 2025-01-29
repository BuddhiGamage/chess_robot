import time
import threading
import csv
from ollama import chat, ChatResponse
import os
import speech_recognition as sr
from gtts import gTTS
import chess
import chess.engine
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI()  # For ChatGPT-4o


# File paths for FEN and moves
fen_file_path = "current_fen.txt"
moves_csv_path = "moves.csv"

# Thread lock for LLM requests
lock = threading.Lock()

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
        return ''
    except sr.RequestError:
        print("Sorry, the service is unavailable.")
        return ''

# Function to convert text to speech using gTTS
def convert_to_speech(text):
    if text:
        tts = gTTS(text=text, lang='en')
        tts.save("response.mp3")  # Save the audio to a file
        os.system("mpg321 --stereo response.mp3")
        # playsound("response.mp3")  # Play the audio file

# Mock function to generate LLM response (replace with actual implementation)
def generate_llm_response(prompt: str, use_chatgpt=False) -> str:
    """Send a prompt to the LLM using Ollama and get a response."""
    board = chess.Board()

    # Read the current FEN and game history
    fen = read_fen()
    game_history = read_game_history()
    next_best_move=get_next_best_move(fen)
    _, next_play = get_next_turn(game_history)

    # Update the board state if the FEN is valid
    if fen:
        try:
            board.set_fen(fen)
        except ValueError:
            print("Invalid FEN. Skipping update.")

    print(board.fen())
    print(game_history)
    print(next_play)
    print("Next best move: "+next_best_move)

    system_prompt = f'''
        You are an AI chess-playing robot.
        You have eyes to identify the chess board and a physical arm to make moves.
        You are playing as black.
        A Human player is playing as white.
        Current chessboard configuration (FEN): {board.fen()}
        Game History: {game_history}.
        Who will play next: {next_play}.
        Predicted next best move for {next_play} player: {next_best_move}.
    '''

    if use_chatgpt:
        response = client.chat.completions.create(model="gpt-4o",
        temperature=0.5,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ])
        return response.choices[0].message.content
    else:
        response: ChatResponse = chat(model="mistral", messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ])
        return response.message.content


# Function to load the current FEN from the file
def read_fen():
    try:
        with open(fen_file_path, "r") as fen_file:
            return fen_file.read().strip()
    except FileNotFoundError:
        return ""

# Function to load the game history from the CSV file
def read_game_history():
    game_history = []
    try:
        with open(moves_csv_path, "r") as csv_file:
            csv_reader = csv.reader(csv_file)
            next(csv_reader)  # Skip the header row
            for row in csv_reader:
                game_history.append({"turn": row[0], "type": row[1], "move": row[2]})
    except FileNotFoundError:
        pass
    return game_history

def get_next_best_move(fen: str, stockfish_path: str = "/usr/games/stockfish") -> str:
    """
    Get the next best move in a chess game using the Stockfish engine.
    
    Args:
        fen (str): The FEN (Forsyth-Edwards Notation) string representing the current board state.
        stockfish_path (str): Path to the Stockfish engine binary.
        
    Returns:
        str: The best move in standard algebraic notation (e.g., "e2e4").
    """
    try:
        # Initialize the chess engine
        with chess.engine.SimpleEngine.popen_uci(stockfish_path) as engine:
            # Create a board from the FEN string
            board = chess.Board(fen)

            # Analyze the position and get the best move
            result = engine.play(board, chess.engine.Limit(time=0.1))  # Limit analysis time to 1 second

            return result.move.uci()
    except Exception as e:
        return f"Error: {e}"

def get_next_turn(moves):
    """Determines the next turn number and the player who needs to play."""
    if not moves:
        return 1, 'Human'  # Default starting move

    next_turn = len(moves) + 1
    last_player = moves[-1]['type']
    next_player = 'Human' if last_player == 'AI' else 'AI'

    return next_turn, next_player

# Main loop to interact with the robot
def talk_with_robot(use_chatgpt=False):
    while True:

        # Prompt the user for a question
        user_input = input("Human: ")
        # user_input = listen_to_user()
        print("Human: "+ user_input)

        # Generate LLM response for the question
        with lock:

            prompt = f"""
            Respond appropriately to the human question based on the game context, information above and the question.
            Respond briefly in one sentence.
            Human question: {user_input}.
            """
            response = generate_llm_response(prompt,use_chatgpt)

        # Display and speak the response
        print(f"AI: {response}")
        convert_to_speech(response)

        # Delay to simulate processing
        time.sleep(1)

# Start the program
if __name__ == "__main__":
    use_chatgpt = True
    talk_with_robot(use_chatgpt)
