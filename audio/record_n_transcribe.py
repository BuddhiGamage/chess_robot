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
import re
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import random
import threading

# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, '/home/buddhi/Projects/chess_robot/CoSMIC/src')

from opensi_cosmic import OpenSICoSMIC

# Load environment variables from .env file
load_dotenv("/home/buddhi/Projects/chess_robot/.env")
FEN_FILE_PATH = "/home/buddhi/Projects/chess_robot/current_fen.txt"
moves_csv_path = "/home/buddhi/Projects/chess_robot/moves.csv"
message_file_path = "/home/buddhi/Projects/chess_robot/message.txt"

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
        self.fen_file_path = FEN_FILE_PATH
        self.moves_csv_path = moves_csv_path
        self.cosmic_config_path = '/home/buddhi/Projects/cosmic/CoSMIC/scripts/configs/config.yaml'
        self.opensi_cosmic = OpenSICoSMIC(config_path=self.cosmic_config_path)
        self.system_prompt = f'''
            You are an AI chess-playing robot created at the University of Canberra with Collaborative Robotics Lab and OpenSI.
            You have eyes to identify the chess board and a physical arm to make moves.
            You are playing as black.
            A Human player is playing as white.
            Respond appropriately to the human question based on the game context, information above and the question.
            Respond briefly in one or two sentences.
        '''
        self.messages = [{"role": "system", "content": self.system_prompt}]
        self.callback=print
        observer = Observer()
        self.old_fen=''
        self.lock = threading.Lock()

        # Set up file system observers
        observer = Observer()

        #  FEN file handler
        self.fen_handler = FileSystemEventHandler()
        self.fen_handler.on_modified = self.on_fen_modified
        observer.schedule(self.fen_handler, path=os.path.dirname(self.fen_file_path), recursive=False)

        self.msg_handler = FileSystemEventHandler()
        self.msg_handler.on_modified = self.on_message_modified
        observer.schedule(self.moves_handler, path=os.path.dirname(self.moves_csv_path), recursive=False)

        # def on_modified(event):
        #     self.handle_fen_update(event, self.callback)

        # event_handler = FileSystemEventHandler()
        # event_handler.on_modified = on_modified
        # observer.schedule(event_handler, path=os.path.dirname(FEN_FILE_PATH), recursive=False)
        
        observer.start()
    
    def on_fen_modified(self, event):
        self.handle_fen_update(event, self.callback)

    def on_message_modified(self, event):
        self.handle_message_update(event, self.callback)

    def handle_fen_update(self, event, callback):
        """
        Handles the event when the FEN file is modified.
        Reads the new FEN and gets a response from LLM.
        """
        if event.src_path == FEN_FILE_PATH:
            with open(FEN_FILE_PATH, "r") as file:
                fen_data = file.read().strip()

                if (fen_data!=self.old_fen):
                    print(f"Detected FEN Update: {fen_data}")

                    game_history = self.read_game_history()

                    print(game_history)

                    prompt=f"""
                    Current chessboard configuration (FEN): {fen_data}
                    Game History: {game_history}.
                    Based on the last move from game history give a response.
                    """
                    
                    if random.random() < 1:  # 20% probability
                        response = self.generate_llm_response(prompt,role="intution")
                        callback(response)

                        try:
                            self.convert_to_speech(response)
                        except AssertionError:
                            print('Nothing from LLM')
                        with self.lock:
                            self.messages = self.summarize_messages()
                    self.old_fen=fen_data

    def handle_message_update(self, event, callback):
        if event.src_path == message_file_path:
            with open(message_file_path, "r") as file:
                msg_data = file.read().strip()
                
                game_history = self.read_game_history()
                fen = self.read_fen()

                prompt=f"""
                    Current chessboard configuration (FEN): {fen}
                    Game History: {game_history}.
                    message: {msg_data}.
                    ask the message content from human player appropriately.
                    """
                response = self.generate_llm_response(prompt,role="intution")
                callback(response)

                try:
                    self.convert_to_speech(response)
                except AssertionError:
                    print('Nothing from LLM')
                with self.lock:
                    self.messages = self.summarize_messages()

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
        return game_history[-10:]

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

    def summarize_messages(self):
        """Summarizes all but the last five messages to keep context compact."""
        if len(self.messages) <= 6:  # If messages are already few, no need to summarize
            return self.messages  # Keep all except system prompt

        system_prompt = self.messages[0]  # Retain system prompt
        old_messages = self.messages[1:-5]  # Messages to summarize (excluding system prompt and last 5)
        last_five = self.messages[-5:]  # Retain last 5 messages
        
        # summary_prompt = "Summarize the following conversation briefly:\n" + "\n".join(
        #     f"{msg['role']}: {msg['content']}" for msg in old_messages
        # )

        summary_prompt = f"Summarize the conversation below while retaining the essence of the system prompt:\n\n"
        summary_prompt += f"System Prompt: {system_prompt['content']}\n\n"
        summary_prompt += "\n".join(f"{msg['role']}: {msg['content']}" for msg in old_messages)

        summary_prompt = [{"role": "assistant", "content": f"[Summary]: {summary_prompt}"}]
        # Generate summary using LLM or a placeholder function
        # summary_response = self.generate_summary(summary_prompt)
        summary_response = client.chat.completions.create(model="gpt-4o",
            temperature=0.5,
            messages=summary_prompt,
            )

        summarized_message = {"role": "assistant", "content": f"[Summary]: {summary_response}"}
        summary_response = summary_response.choices[0].message.content.split("[Response]:")
        
        return [system_prompt, summarized_message] + last_five  # Keep system prompt, summary, and last 5 messages

    # Mock function to generate LLM response (replace with actual implementation)
    def generate_llm_response(self, prompt: str,role="user",use_cosmic=False) -> str:
        """Send a prompt to the LLM using gpt4o and get a response."""

        with self.lock:
            if(role=="user"):
                self.messages.append({ "role": "user", "content": prompt})
            elif(role=="intution"):
                self.messages.append({ "role": "assistant", "content": "[Intution]: "+prompt})
            
            print(self.messages)


            # response = client.chat.completions.create(model="gpt-4o",
            # temperature=0.5,
            # messages=self.messages,
            # )
            # response = response.choices[0].message.content.split("[Response]:")[-1]
            if (use_cosmic):
                # Construct a full query including message history
                full_prompt = "\n".join([msg["content"] for msg in self.messages])
                response = self.get_cosmic_response(full_prompt)
            else:
                response = self.get_gpt_response()
            self.messages.append({ "role": "assistant", "content": "[Response]: "+response})
            
            return response
    
    def get_gpt_response(self):
        response = client.chat.completions.create(model="gpt-4o",
            temperature=0.5,
            messages=self.messages,
            )
        response = response.choices[0].message.content.split("[Response]:")[-1]
        return response
    
    def get_cosmic_response(self, prompt):
        answer, _, _ = self.opensi_cosmic(prompt)
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
            
            prompt = f"""
            Current chessboard configuration (FEN): {board.fen()}
            Game History: {game_history}.
            Who will play next: {next_play}.
            Predicted next best move for {next_play} player: {next_best_move}.
            Human question: {transcription}.
            """

            # prompt_cosmic = f"""
            # Game History: {game_history}.
            # Who will play next: {next_play}.
            # Human question: {transcription}.
            # Base on current FEN : {fen}""" 
            
            prompt_cosmic = f"""
            Game History: {game_history}.
            Answer Human question: {transcription}
            Based on current FEN : {fen}""" 

            # prompt_cosmic = \
            #     f"Game History: {game_history}.\n" \
            #     f"Who will play next: {next_play}.\n" \
            #     f"Human question: {transcription}.\n" \
            #     f"Current FEN: {fen}.\n"
            
            # response = self.generate_llm_response(prompt) # chatgpt 4o
            
            # CoSMIC implementation
            response = self.generate_llm_response(prompt_cosmic,use_cosmic=True)
            if "is one of" in response:
                moves = response.split("is one of ")
                response = re.sub(r'\[.*?\]', 'current FEN', moves[0])+' is one of '+moves[1]

            # Display and speak the response
            print(f"AI: {response}")
            try:
                self.convert_to_speech(response)
            except AssertionError:
                print('Nothing from LLM')
            
            with self.lock:
                self.messages = self.summarize_messages()
                # print(self.messages)
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