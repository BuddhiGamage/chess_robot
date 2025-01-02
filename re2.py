import cv2
import numpy as np
import pytesseract


# Preprocess the image
def preprocess_image(img):
    
   # Convert the image to an 8-bit unsigned integer type
    gray = np.uint8(img * 255)
    
    # Apply histogram equalization to the image
    gray = cv2.equalizeHist(gray)
    
  # Apply binarization to the image
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU) 
 # Perform erosion and dilation to remove noise
    kernel = np.ones((2,2), np.uint8)
    binary = cv2.erode(binary, kernel, iterations=1)
    binary = cv2.dilate(binary, kernel, iterations=1)
    
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


    # Preprocess the image
    preprocessed_image = preprocess_image(img)

    # Define square size
    square_size = 100

    # Create an empty 8x8 matrix
    matrix = np.zeros((8, 8), dtype=object)

    # Iterate through each square
    for row in range(8):
        for col in range(8):
            # Calculate x and y coordinates of the square
            x = col * square_size
            y = row * square_size

            # # Extract the ROI of the square
            roi = img[y:y+square_size, x:x+square_size]

            # Adjust the coordinates to crop 20 pixels from each side
            # roi = img[y+20:y+square_size-20, x+20:x+square_size-20]
            cv2.imshow("Extracted Chessboard", roi)
            cv2.waitKey(0)

            # Check if the ROI contains a letter
            # Extract the letter using pytesseract
            letter = pytesseract.image_to_string(roi, config='--oem 1 --psm 10 -c tessedit_char_whitelist=TLXEMFRNBKQP')
            letter = letter.strip()
            print(letter)

            # Append detected letter or '1' for empty square
            if letter:
                matrix[row][col] = letter
            else:
                matrix[row][col] = 1
            



    return matrix

# Example usage
image_path = '/home/buddhi/Projects/chess_robot/extracted_chessboard_no_border.jpg'
chessboard_matrix = chessboard_to_matrix(image_path)
print(chessboard_matrix)