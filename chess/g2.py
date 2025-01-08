import chess
import chess.engine
import chess.svg

def main():
    # Initialize the chess board
    board = chess.Board()
    board.clean_castling_rights()

    # Use the Stockfish engine for AI moves (make sure it's installed and available on your system)
    engine_path = "/usr/games/stockfish"  # Replace with the actual path to Stockfish
    with chess.engine.SimpleEngine.popen_uci(engine_path) as engine:
        print("Welcome to Chess! Enter your moves in UCI notation (e.g., e2e4). Type 'quit' to exit.")

        while not board.is_game_over():
            # Display the board
            print(board)

            # Get the human player's move
            human_move = input("Your move: ").strip()
            if human_move.lower() == "quit":
                print("Exiting the game. Goodbye!")
                break

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
            # print(result.move)
            board.push(result.move)

        # Display the game result
        print("Game over!")
        print("Result:", board.result())

if __name__ == "__main__":
    main()
