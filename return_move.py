def find_chess_move(initial_board, final_board):
    # Convert the board positions into chess notation (0-indexed to chess coordinates)
    def to_chess_notation(x, y):
        return chr(y + ord('a')) + str(8 - x)
    
    start_pos = None
    end_pos = None
    capture=False

    for i in range(8):
        for j in range(8):
            if initial_board[i][j] != final_board[i][j]:
                if final_board[i][j] != -1 and initial_board[i][j]==-1:  # Updated position
                    end_pos = (i, j)
                elif final_board[i][j] != -1 and initial_board[i][j]!=-1:
                    capture=True
                    end_pos = (i, j)

    print(end_pos)
    for i in range(8):
        for j in range(8):
            if initial_board[i][j] != final_board[i][j]:
                if final_board[i][j] == -1 and final_board[end_pos[0]][end_pos[1]]==initial_board[i][j]:  # Updated position
                    start_pos = (i, j)


    print(start_pos)
    # Convert to chess notation
    if start_pos and end_pos:
        start_square = to_chess_notation(start_pos[0], start_pos[1])
        end_square = to_chess_notation(end_pos[0], end_pos[1])
        return start_square + end_square,capture
    else:
        return None
    

# Example matrices
initial_matrix = [
    [1, 2, 3, 5, 4, 3, 2, 1],
    [0, 0, 0, -1, 0, 0, 0, 0],
    [-1, -1, -1, -1, -1, -1, -1, -1],
    [-1, -1, 0, 6, -1, -1, -1, -1],
    [-1, -1, -1, -1, -1, -1, -1, -1],
    [-1, -1, -1, -1, -1, -1, -1, -1],
    [6, 6, 6, 6, 6, 6, 6, 6],
    [7, 8, 9, 10, 11, 9, 8, 7]
]

final_matrix = [
    [1, 2, 3, 5, 4, 3, 2, 1],
    [0, 0, 0, -1, 0, 0, 0, 0],
    [-1, -1, 6, -1, -1, -1, -1, -1],
    [-1, -1, -1, -1, -1, -1, -1, -1],
    [-1, -1, -1, -1, -1, -1, -1, -1],
    [-1, -1, -1, -1, -1, -1, -1, -1],
    [6, 6, 6, 6, 6, 6, 6, 6],
    [7, 8, 9, 10, 11, 9, 8, 7]
]

# # Find the move
# move = find_chess_move(initial_matrix, final_matrix)
# print("The move is:", move)
