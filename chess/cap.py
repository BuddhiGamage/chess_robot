import chess

# Initialize a chess board
board = chess.Board()

# Set up a position with a potential capture
board.set_fen("r2qk2r/ppp3pp/3pB2B/2b1p3/4P3/3P3Q/PP3PPP/nN1K3R b kq - 0 11")

# Simulate a capturing move
# Move a white pawn and set up for a capture scenario
# board.push(move)  # Make the d2d4 move

# Now let's create a capture move
capture_move = chess.Move.from_uci("g7h6")  # Black pawn capturing white pawn
if capture_move in board.legal_moves:
    if board.is_capture(capture_move):
        print(f"The move {capture_move.uci()} captures a piece.")
        captured_square = capture_move.to_square
        print(captured_square)
        captured_piece = board.piece_at(captured_square)
        print(f"Captured piece {captured_piece.symbol()} on square {chess.square_name(captured_square)}.")
    else:
        print(f"The move {capture_move.uci()} does not capture a piece.")
else:
    print(f"The move {capture_move.uci()} is not legal.")
