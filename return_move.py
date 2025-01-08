def get_move(previous_state, current_state):
    # Define the board columns and rows
    columns = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    rows = ['1', '2', '3', '4', '5', '6', '7', '8']  # Bottom to top

    # Find the source and destination positions
    source = None
    destination = None

    for i in range(8):
        for j in range(8):
            if previous_state[i][j] == 1 and current_state[i][j] == 0:
                # Piece moved from (i, j)
                source = columns[j] + rows[7 - i]  # Flip row index
            elif previous_state[i][j] == 0 and current_state[i][j] == 1:
                # Piece moved to (i, j)
                destination = columns[j] + rows[7 - i]  # Flip row index

    if source and destination:
        return f'{source}{destination}'
    else:
        return "No move detected"

# Example matrices
previous_state = [
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0],  # initial position
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1]
]

current_state = [
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 1],  # Piece removed from d2
    [0, 0, 0, 0, 0, 0, 0, 0],  # Piece added to d4
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 1, 0, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1]
]

# Get the move
move = get_move(previous_state, current_state)
print(move)
