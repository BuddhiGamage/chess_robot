import time
import threading
import chess
import csv
from ollama import chat, ChatResponse
import os
import speech_recognition as sr
from gtts import gTTS
import playsound

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
def generate_llm_response(prompt: str) -> str:
    """Send a prompt to the LLM using Ollama and get a response."""
    # response: ChatResponse = chat(model="phi3", messages=[
    response: ChatResponse = chat(model="mistral", messages=[
        {"role": "user", "content": prompt}
    ])
    return response.message.content  # Return the LLM's response


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

# Main loop to interact with the robot
def talk_with_robot():
    board = chess.Board()

    while True:
        # Read the current FEN and game history
        fen = read_fen()
        game_history = read_game_history()

        # Update the board state if the FEN is valid
        if fen:
            try:
                board.set_fen(fen)
            except ValueError:
                print("Invalid FEN. Skipping update.")

        # Prompt the user for a question
        # user_input = input("Human: ")
        user_input = listen_to_user()
        print("Human: "+ user_input)
        
        # Generate LLM response for the question
        with lock:
            print(board.fen())
            print(game_history)
            prompt = f"""
            You are a chess-playing robot.
            Current chessboard configuration (FEN): {board.fen()}
            Game History: {game_history}
            Human question: {user_input}
            Respond appropriately based on the game context and the question.
            Respond briefly in one or two sentences
            """
            response = generate_llm_response(prompt)

        # Display and speak the response
        print(f"AI: {response}")
        convert_to_speech(response)

        # Delay to simulate processing
        time.sleep(1)

# Start the program
if __name__ == "__main__":
    talk_with_robot()
