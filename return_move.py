def to_chess_notation(x, y):
    return chr(y + ord('a')) + str(8 - x)

def detect_white_king_castling(initial_board, final_board):
    """
    Detect if the White King has castled (kingside or queenside).
    
    Args:
        initial_board (list of list): The initial 8x8 chessboard matrix.
        final_board (list of list): The final 8x8 chessboard matrix.
    
    Returns:
        str: The type of castling ("start coordinates, end coordinates, castling_availability) or "King did not castle".
    """
    # Check if the King is still in its starting position (e1)
    if initial_board[7][4] == 4 and final_board[7][4] != 4:
        # King moved, determine where it moved
        if final_board[7][6] == 4:  # King moved to g1
            return (7,4),(7,6),False
        elif final_board[7][2] == 4:  # King moved to c1
            return (7,4),(7,2),False
    else:
        return None,None,True
def find_chess_move(initial_board, final_board,castling_availability):
    # Convert the board positions into chess notation (0-indexed to chess coordinates)
    
    start_pos = None
    end_pos = None
    capture=False
    if (castling_availability):
        start_pos,end_pos,castling_availability=detect_white_king_castling(initial_board,final_board)
        if(castling_availability==False):
            start_square = to_chess_notation(start_pos[0], start_pos[1])
            end_square = to_chess_notation(end_pos[0], end_pos[1])
            return start_square+end_square,capture,castling_availability
    
    for i in range(8):
        for j in range(8):
            if initial_board[i][j] != final_board[i][j]:
                if final_board[i][j] != -1 and initial_board[i][j]==-1:  # Updated position
                    end_pos = (i, j)
                elif final_board[i][j] != -1 and initial_board[i][j]!=-1:
                    capture=True
                    end_pos = (i, j)

    print(to_chess_notation(end_pos[0], end_pos[1]))
    for i in range(8):
        for j in range(8):
            if initial_board[i][j] != final_board[i][j]:
                if final_board[i][j] == -1 and final_board[end_pos[0]][end_pos[1]]==initial_board[i][j]:  # Updated position
                    start_pos = (i, j)


    print(to_chess_notation(start_pos[0], start_pos[1]))
    # Convert to chess notation
    if start_pos and end_pos:
        start_square = to_chess_notation(start_pos[0], start_pos[1])
        end_square = to_chess_notation(end_pos[0], end_pos[1])
        return start_square + end_square,capture,castling_availability
    # else:
    #     return None
    

# # Example matrices
# initial_matrix = [
#     [9, 7, 8, 10, 11, 8, 7, 9],
#     [6, 6, 6, 6, 6, 6, 6, 6],
#     [-1, -1, -1, -1, -1, -1, -1, -1],
#     [-1, -1, -1, -1, -1, -1, -1, -1],
#     [-1, -1, -1, -1, -1, -1, -1, -1],
#     [-1, -1, -1, -1, -1, -1, -1, -1],
#     [0, 0, 0, 0, 0, 0, 0, 0],
#     [3, 1, 2, 5, 4, 2, 1, 3]
# ]

# final_matrix = [
#     [9, 7, 8, 10, 11, 8, 7, 9],
#     [6, 6, 6, 6, 6, 6, 6, 6],
#     [-1, -1, -1, -1, -1, -1, -1, -1],
#     [-1, -1, -1, -1, -1, -1, -1, -1],
#     [0, -1, -1, -1, -1, -1, -1, -1],
#     [-1, -1, -1, -1, -1, -1, -1, -1],
#     [-1, 0, 0, 0, 0, 0, 0, 0],
#     [3, 1, 2, 5, 4, 2, 1, 3]
# ]
# # Find the move
# move = find_chess_move(initial_matrix, final_matrix)
# print("The move is:", move)
