# from photo import capture_image_from_realsense
# from xai import next_move

from stockfish import Stockfish

# Initialize the Stockfish engine
stockfish = Stockfish()



# Set the skill level (1-20, default is 20)
stockfish.set_skill_level(10)

# Set the initial position (FEN string) or start with a new game
stockfish.set_position(["e2e4", "e7e5", "g1f3", "b8c6"])

# Get the best move from the current position
best_move = stockfish.get_best_move()
print("Best move:", best_move)

# Evaluate the current position
evaluation = stockfish.get_evaluation()
print("Evaluation:", evaluation)

# Send the best move to Stockfish and update the position
stockfish.make_moves_from_current_position([best_move])

# Get the updated board state
print("Updated board:", stockfish.get_board_visual())