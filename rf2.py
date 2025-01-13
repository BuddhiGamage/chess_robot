import cv2
import numpy as np

def preprocess_image(img):
    
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
            cv2.THRESH_BINARY,333,40)
    
    # sharpen_kernel = np.array([[-1result,-1,-1], [-1,9,-1], [-1,-1,-1]])
    # sharpen = cv2.filter2D(binary, -1, sharpen_kernel)
    # thresh = cv2.threshold(sharpen,220, 255,cv2.THRESH_BINARY)[1]
    # kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3))
    # opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=3)
    # result = cv2.dilate(opening, kernel, iterations=3)


    return binary

def chessboard_to_matrix(image_path):
    """
    Converts a chessboard image with letters to an 8x8 matrix.

    Args:
        image_path: Path to the chessboard image.

    Returns:
        An 8x8 NumPy array representing the chessboard, 
        where '1' represents empty squares and letters represent 
        squares with corresponding letters.
    """

    # Load the image in grayscale
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        
    # Copy of the image for drawing bounding boxes
    image_with_boxes = img.copy()

    # Preprocess the image
    # preprocessed_image = preprocess_image(img)

    # cv2.imshow("Extracted Chessboard", preprocessed_image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()


    # Define the dictionary we used to generate the marker
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    aruco_params = cv2.aruco.DetectorParameters()

    # Detect the markers in the image
    detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)

    # Constants
    image_size = 1024  # Image dimensions (assume square image)  
    top_border = 38  # Top border width in pixels
    bottom_border = 38  # Bottom border width in pixels
    left_border = 37  # Left border width in pixels
    right_border = 35  # Right border width in pixels
    num_squares = 8  # Number of squares per row/column
    square_width = (image_size - left_border - right_border) // num_squares
    square_height = (image_size - top_border - bottom_border) // num_squares
    extra_boundary = 10  # Additional boundary in pixels
    # Resize the image to ensure it's 800x800
    # img = cv2.resize(img, (image_size, image_size))
    
    count =0

    # Create an empty 8x8 matrix
    matrix = np.zeros((8, 8), dtype=object)

    # Iterate through each square
    for row in range(num_squares):
        for col in range(num_squares):

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

            # Extract the ROI of the square
            roi = img[adjusted_start_y:adjusted_end_y, adjusted_start_x:adjusted_end_x]

            # cv2.imshow("Extracted Chessboard", roi)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()

            
            corners, ids, rejected = detector.detectMarkers(roi)

            # Draw detected markers on the image
            if ids is not None:
                matrix[row][col] = int(ids.flatten()[0])
                roi = cv2.aruco.drawDetectedMarkers(roi.copy(), corners, ids)
                count+=1
                # cv2.imshow("Extracted Chessboard", roi)
                # cv2.waitKey(0)
            else:
                matrix[row][col] = -1

            
            # cv2.imshow("Extracted Chessboard", roi)
            # cv2.waitKey(0)
            
            


    # # Display the final image with bounding boxes
    # cv2.imshow("Image with Bounding Boxes", image_with_boxes)
    # cv2.waitKey(0)  # Wait indefinitely until a key is pressed
    # cv2.destroyAllWindows()
    print(count)
    return matrix.tolist(), count

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
chessboard_matrix = chessboard_to_matrix(image_path)
print(chessboard_matrix)