import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv("/home/buddhi/Projects/chess_robot/.env")

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

FEN_FILE_PATH = "/home/buddhi/Projects/chess_robot/current_fen.txt"  # Change this to your actual FEN file path

class FENFileHandler(FileSystemEventHandler):
    def __init__(self, llm_response_callback):
        self.llm_response_callback = llm_response_callback

    def on_modified(self, event):
        if event.src_path == FEN_FILE_PATH:
            with open(FEN_FILE_PATH, "r") as file:
                fen_data = file.read().strip()
                print(f"Detected FEN Update: {fen_data}")
                response = self.query_llm(fen_data)
                self.llm_response_callback(response)

    def query_llm(self, fen):
        # Example OpenAI API call (change this as needed)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": f"Analyze this FEN: {fen}"}]
        )
        return response.choices[0].message.content

def start_fen_listener():
    event_handler = FENFileHandler(llm_response_callback=print)
    observer = Observer()
    observer.schedule(event_handler, path=os.path.dirname(FEN_FILE_PATH), recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)  # Keep the thread alive
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    start_fen_listener()
