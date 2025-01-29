from pynput import keyboard
import pyaudio
import wave
from openai import OpenAI
from dotenv import load_dotenv
import os
import chess
import chess.engine
import csv
from gtts import gTTS
import sys

# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, '/home/buddhi/Projects/chess_robot/CoSMIC/src')

from opensi_cosmic import OpenSICoSMIC

# Load environment variables from .env file
load_dotenv("/home/buddhi/Projects/chess_robot/.env")

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class listener(keyboard.Listener):
    def __init__(self, recorder):
        super().__init__(on_press=self.on_press, on_release=self.on_release)
        self.recorder = recorder
    
    def on_press(self, key):
        if key is None:  # unknown event
            pass
        elif isinstance(key, keyboard.Key):  # special key event
            if key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
                self.recorder.start()
        elif isinstance(key, keyboard.KeyCode):  # alphanumeric key event
            if key.char == 'q':  # press q to quit
                if self.recorder.recording:
                    self.recorder.stop()
                return False  # this is how you stop the listener thread                                                  

    def on_release(self, key):
        if key is None:  # unknown event
            pass
        elif isinstance(key, keyboard.Key):  # special key event
            if key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
                self.recorder.stop()
        elif isinstance(key, keyboard.KeyCode):  # alphanumeric key event
            pass

class recorder:
    def __init__(self, 
                 wavfile, 
                 chunksize=8192, 
                 dataformat=pyaudio.paInt16, 
                 channels=2, 
                 rate=44100):
        self.filename = wavfile
        self.chunksize = chunksize
        self.dataformat = dataformat
        self.channels = channels
        self.rate = rate
        self.recording = False
        self.pa = pyaudio.PyAudio()
        # File paths for FEN and moves
        self.fen_file_path = "/home/buddhi/Projects/chess_robot/current_fen.txt"
        self.moves_csv_path = "/home/buddhi/Projects/chess_robot/moves.csv"
        self.cosmic_config_path = '/home/buddhi/Projects/cosmic/CoSMIC/scripts/configs/config.yaml'
        self.opensi_cosmic = OpenSICoSMIC(config_path=self.cosmic_config_path)
    
    # Function to load the current FEN from the file
    def read_fen(self):
        try:
            with open(self.fen_file_path, "r") as fen_file:
                return fen_file.read().strip()
        except FileNotFoundError:
            return ""

    # Function to load the game history from the CSV file
    def read_game_history(self):
        game_history = []
        try:
            with open(self.moves_csv_path, "r") as csv_file:
                csv_reader = csv.reader(csv_file)
                next(csv_reader)  # Skip the header row
                for row in csv_reader:
                    game_history.append({"turn": row[0], "type": row[1], "move": row[2]})
        except FileNotFoundError:
            pass
        return game_history

    def get_next_best_move(self, fen: str, stockfish_path: str = "/usr/games/stockfish") -> str:
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

    def get_next_turn(self, moves):
        """Determines the next turn number and the player who needs to play."""
        if not moves:
            return 1, 'Human'  # Default starting move

        next_turn = len(moves) + 1
        last_player = moves[-1]['type']
        next_player = 'Human' if last_player == 'AI' else 'AI'

        return next_turn, next_player

    # Mock function to generate LLM response (replace with actual implementation)
    def generate_llm_response(self, prompt: str) -> str:
        """Send a prompt to the LLM using Ollama and get a response."""
        board = chess.Board()

        # Read the current FEN and game history
        fen = self.read_fen()
        game_history = self.read_game_history()
        next_best_move= self.get_next_best_move(fen)
        _, next_play = self.get_next_turn(game_history)

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

        response = client.chat.completions.create(model="gpt-4o",
        temperature=0.5,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ])
        return response.choices[0].message.content
    
    def get_cosmic_response(self, promt):
        
        # Read the current FEN and game history
        fen = self.read_fen()
        eng = f". Always give short answers as a normal talking in one sentence. Current FEN : {fen}"
        # Run for each question/query, return the truncated response if applicable.
        answer, _, _ = self.opensi_cosmic(promt+eng)
        return answer


    # Function to convert text to speech using gTTS
    def convert_to_speech(self, text):
        if text:
            tts = gTTS(text=text, lang='en')
            tts.save("response.mp3")  # Save the audio to a file
            os.system("mpg321 --stereo response.mp3")
            # playsound("response.mp3")  # Play the audio file

    def start(self):
        if not self.recording:
            self.wf = wave.open(self.filename, 'wb')
            self.wf.setnchannels(self.channels)
            self.wf.setsampwidth(self.pa.get_sample_size(self.dataformat))
            self.wf.setframerate(self.rate)
            
            def callback(in_data, frame_count, time_info, status):
                # file write should be able to keep up with audio data stream (about 1378 Kbps)
                self.wf.writeframes(in_data) 
                return (in_data, pyaudio.paContinue)
            
            self.stream = self.pa.open(format=self.dataformat,
                                       channels=self.channels,
                                       rate=self.rate,
                                       input=True,
                                       stream_callback=callback)
            self.stream.start_stream()
            self.recording = True
            print('Recording started')

    def stop(self):
        if self.recording:         
            print('Recording finished')

            self.stream.stop_stream()
            self.stream.close()
            self.wf.close()

            self.recording = False

            # Transcribe the recorded audio using Whisper
            transcription = self.transcribe_audio(self.filename)
            print("Transcription:", transcription)

            prompt = f"""
            Respond appropriately to the human question based on the game context, information above and the question.
            Respond briefly in one sentence.
            Human question: {transcription}.
            """
            # response = self.generate_llm_response(prompt)
            response = self.get_cosmic_response(prompt)

            # Display and speak the response
            print(f"AI: {response}")
            self.convert_to_speech(response)

    def transcribe_audio(self, audio_file):
        """
        Sends the audio file to OpenAI's Whisper API for transcription.
        """
        try:
            with open(audio_file, "rb") as file:
                response = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=file
                )
                transcription = response.text
                return transcription
        
        except Exception as e:
            print(f"Error during transcription: {e}")
            return None
    

if __name__ == '__main__':
    r = recorder("mic.wav")
    l = listener(r)
    print('Press Alt key to start recording and release to stop. Press "q" to quit.')
    l.start()  # keyboard listener is a thread so we start it here
    l.join()  # wait for the thread to terminate so the program doesn't instantly close