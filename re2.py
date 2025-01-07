import cv2
import numpy as np
import pytesseract


# Preprocess the image
def preprocess_image(img,x,y):
    
   # Convert the image to an 8-bit unsigned integer type
    gray = np.uint8(img * 255)
    
    gray_inv = cv2.bitwise_not(gray)
#     # Apply histogram equalization to the image
#     gray = cv2.equalizeHist(gray)
    
#   # Apply binarization to the image
#     _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU) 
#  # Perform erosion and dilation to remove noise
#     kernel = np.ones((2,2), np.uint8)
#     binary = cv2.erode(binary, kernel, iterations=1)
#     binary = cv2.dilate(binary, kernel, iterations=1)

    binary = cv2.adaptiveThreshold(gray_inv,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
            cv2.THRESH_BINARY,x,y)
    
    return binary

def chessboard_to_matrix(img,i,j):
    """
    Converts a chessboard image with letters to an 8x8 matrix.

    Args:
        image_path: Path to the chessboard image.

    Returns:
        An 8x8 NumPy array representing the chessboard, 
        where '1' represents empty squares and letters represent 
        squares with corresponding letters.
    """
        
    # Copy of the image for drawing bounding boxes
    image_with_boxes = img.copy()


    # Preprocess the image
    preprocessed_image = preprocess_image(img,i,j)

    # cv2.imshow("Extracted Chessboard", preprocessed_image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # Constants
    image_size = 800  # Image dimensions (assume square image)  
    top_border = 38  # Top border width in pixels
    bottom_border = 38  # Bottom border width in pixels
    left_border = 37  # Left border width in pixels
    right_border = 35  # Right border width in pixels
    num_squares = 8  # Number of squares per row/column
    square_width = (image_size - left_border - right_border) // num_squares
    square_height = (image_size - top_border - bottom_border) // num_squares
    extra_boundary = 10  # Additional boundary in pixels
    # Resize the image to ensure it's 800x800
    img = cv2.resize(img, (image_size, image_size))
    

    # Create an empty 8x8 matrix
    matrix = np.zeros((8, 8), dtype=object)

    # Iterate through each square
    for row in range(num_squares):
        for col in range(num_squares):
            # # Calculate x and y coordinates of the square
            # x = col * square_size
            # y = row * square_size

            # Adjust coordinates for the top and bottom halves based on the borders
            if row < num_squares // 2:
                start_y = top_border + row * square_height
                end_y = start_y + square_height
            else:
                start_y = (image_size - bottom_border) - (num_squares - row) * square_height
                end_y = start_y + square_height

            # Adjust coordinates for the left and right halves based on the borders
            if col < num_squares // 2:
                start_x = left_border + col * square_width
                end_x = start_x + square_width
            else:
                start_x = (image_size - right_border) - (num_squares - col) * square_width
                end_x = start_x + square_width
                
            # Adjust the rectangle to include an additional pixel boundary
            adjusted_start_x = max(start_x - extra_boundary, 0)
            adjusted_start_y = max(start_y - extra_boundary, 0)
            adjusted_end_x = min(end_x + extra_boundary, image_size)
            adjusted_end_y = min(end_y + extra_boundary, image_size)
            
            # Draw a rectangle (bounding box) around the square on the image
            cv2.rectangle(image_with_boxes, (start_x, start_y), 
                        (end_x, end_y), (0, 255, 0), 2)

            # # Extract the ROI of the square
            roi = preprocessed_image[adjusted_start_y:adjusted_end_y, adjusted_start_x:adjusted_end_x]
            # roi = img[adjusted_start_y:adjusted_end_y, adjusted_start_x:adjusted_end_x]
            # roi = preprocessed_image[y:y+square_size, x:x+square_size]

            # Adjust the coordinates to crop 15 pixels from each side
            # roi = img[y+15:y+square_size-15, x+15:x+square_size-15]
            # roi = preprocessed_image[y+5:y+square_size-5, x+5:x+square_size-5]

            # Check if the ROI contains a letter
            # Extract the letter using pytesseract
            letter = pytesseract.image_to_string(roi, config='--psm 10 -c tessedit_char_whitelist=THXWMFRNBKQP')
            letter = letter.strip()
            # print(letter)
            # cv2.imshow("Extracted Chessboard", roi)
            # cv2.waitKey(0)

            # Add text to indicate the square's coordinates
            cv2.putText(
                image_with_boxes,
                # f"({row}, {col}): {letter}",
                f"{letter}",
                (start_x + 10, start_y + 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                1,
                cv2.LINE_AA
            )

            # Append detected letter or '1' for empty square
            if letter:
                matrix[row][col] = letter
            else:
                matrix[row][col] = 1
            


    # # Display the final image with bounding boxes
    # cv2.imshow("Image with Bounding Boxes", image_with_boxes)
    # cv2.waitKey(0)  # Wait indefinitely until a key is pressed
    # cv2.destroyAllWindows()
    return matrix

def convert_to_fen(board):
    # Mapping for black pieces to their FEN notation
    black_piece_map = {
        'F': 'p',  # Black Pawn
        'T': 'r',  # Black Rook
        'H': 'n',  # Black Knight
        'X': 'b',  # Black Bishop
        'W': 'q',  # Black Queen
        'M': 'k',  # Black King
        'O': 'Q'   # Black King
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

# # Example usage
image_path = '/home/buddhi/Projects/chess_robot/extracted_chessboard.jpg'

# Load the image in grayscale
img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

# Example board
array = [
    [1, 1, 1, 1, 1, 1, 1, 'F'],
    [1, 1, 'H', 1, 'F', 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 'P', 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 'F', 1, 'P', 1, 1, 1],
    [1, 'F', 1, 'N', 1, 1, 1, 'X'],
    ['T', 1, 1, 1, 1, 1, 1, 1]
]
for x in range (3,100,2):
    for y in range(1,100):
         chessboard_matrix = chessboard_to_matrix(img,x,y)
         if np.array_equal(chessboard_matrix, array):
            print('Best x:{x} and y"{y}')
            break
print(chessboard_matrix)