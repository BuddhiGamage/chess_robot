def convert_to_fen(board):
    # Mapping for black pieces to their FEN notation
    black_piece_map = {
        'F': 'p',  # Black Pawn
        'T': 'r',  # Black Rook
        'L': 'n',  # Black Knight
        'X': 'b',  # Black Bishop
        'E': 'q',  # Black Queen
        'M': 'k'   # Black King
    }
    
    fen_rows = []
    
    for row in board:
        fen_row = ""
        empty_count = 0
        
        for cell in row:
            if isinstance(cell, int) and cell == 1:
                # Increment empty square count
                empty_count += 1
            else:
                # Append empty square count if any
                if empty_count > 0:
                    fen_row += str(empty_count)
                    empty_count = 0
                
                # Convert black pieces to lowercase
                if cell in black_piece_map:
                    fen_row += black_piece_map[cell]
                else:
                    fen_row += cell
        
        # Append remaining empty square count if any
        if empty_count > 0:
            fen_row += str(empty_count)
        
        fen_rows.append(fen_row)
    
    # Join rows with '/'
    fen_notation = "/".join(fen_rows)
    return fen_notation

# Example board
board = [
    ['R', 'N', 1, 'Q', 'K', 'B', 'N', 'R'],
    ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 'P', 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1],
    ['F', 1, 'F', 'F', 'F', 'F', 'F', 1],
    [1, 'L', 'X', 'E', 1, 'X', 1, 1]
]

# Convert to FEN
fen = convert_to_fen(board)
print("FEN Notation:", fen)
