import chess
import chess.engine
from ollama import chat, ChatResponse
import re
import time
import threading

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


def get_best_move(fen: str) -> str:
    """Get the best move from Stockfish."""
    with engine.analysis(board) as analysis:
        best_move = engine.play(board, chess.engine.Limit(time=1.0))
    return best_move.move.uci()


def generate_llm_response(prompt: str) -> str:
    """Send a prompt to the LLM using Ollama and get a response."""
    response: ChatResponse = chat(model="mistral", messages=[
        {"role": "user", "content": prompt}
    ])
    return response.message.content  # Return the LLM's response


def interpret_human_input(user_input: str) -> str:
    """Interpret whether the input is a chess move or a question."""
    move_pattern = r"^[a-h][1-8][a-h][1-8]$|^[a-h][1-8][a-h][1-8][qrbn]$"
    if re.match(move_pattern, user_input.lower()):
        return "move"
    return "question"


def process_human_move(move: str):
    """Process and validate a human chess move."""
    global human_move_detected
    if board.is_legal(chess.Move.from_uci(move)):
        with lock:
            board.push(chess.Move.from_uci(move))
            human_moves.append(move)  # Record human move in history
            game_history.append(f"Human: {move}")  # Combined history
            print(f"Human moved: {move}")
        human_move_detected.set()  # Notify the AI to make its move
    else:
        print("Illegal move. Try again.")


def ai_make_move():
    """AI calculates and makes its move."""
    global human_move_detected
    while not board.is_game_over():
        # Wait for human move to be detected
        human_move_detected.wait()
        human_move_detected.clear()

        # AI calculates and plays its move
        with lock:
            best_move = get_best_move(board.fen())
            board.push(chess.Move.from_uci(best_move))
            ai_moves.append(best_move)  # Record AI move in history
            game_history.append(f"AI: {best_move}")  # Combined history
            print(f"AI moved: {best_move}")

        # Notify robotic arm to execute the move
        update_physical_board(best_move)


def update_physical_board(move: str):
    """Send AI's move to the robotic arm."""
    print(f"Robotic arm executing move: {move}")


def continuous_chat_and_moves():
    """Main loop for interacting with the human player."""
    print("You can make a move (in UCI notation) or ask a question!")
    while not board.is_game_over():
        user_input = input("Your input: ").strip()

        # Determine if the input is a move or a question
        input_type = interpret_human_input(user_input)

        if input_type == "move":
            process_human_move(user_input)
        elif input_type == "question":
            # Generate LLM response for a question
            with lock:
                print(board.fen())
                print(game_history)
                prompt = f"""
                Current chessboard configuration (FEN): {board.fen()}
                Game History: {game_history}
                Human question: {user_input}
                Respond appropriately based on the game context and the question.
                """
            response = generate_llm_response(prompt)
            print(f"AI: {response}")
        else:
            print("Invalid input. Please enter a valid chess move or ask a question.")


# Run the System
def main():
    print("Welcome to Chess with Embodied AI!")
    print("Type your moves in UCI notation (e.g., e2e4) or ask me a question!")
    print("The AI will respond to your inputs and make moves using a robotic arm.")
    print("Let's play!")

    # Start AI move thread
    threading.Thread(target=ai_make_move, daemon=True).start()

    # Run the interactive chat and move processing loop
    continuous_chat_and_moves()

    # Game Over
    print("Game over!")
    print(f"Result: {board.result()}")


if __name__ == "__main__":
    main()
