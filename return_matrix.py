import cv2
import numpy as np
import pytesseract

# Load the chessboard image
image_path = '/home/buddhi/Projects/chess_robot/extracted_chessboard_no_border.jpg'
image = cv2.imread(image_path)

# Convert the image to grayscale
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Apply adaptive thresholding to enhance the grid
thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

# Find contours to detect the board
contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Assume the largest contour is the chessboard
contours = sorted(contours, key=cv2.contourArea, reverse=True)
chessboard_contour = contours[0]

# Get the bounding box of the chessboard
x, y, w, h = cv2.boundingRect(chessboard_contour)
chessboard = image[y:y+h, x:x+w]

# Resize the cropped chessboard to ensure consistent cell size
chessboard = cv2.resize(chessboard, (800, 800))

# Calculate the size of each square
square_size = chessboard.shape[0] // 8

# Initialize the matrix
matrix = []

# Loop through each square
for row in range(8):
    matrix_row = []
    for col in range(8):
        # Extract each square
        square = chessboard[row * square_size:(row + 1) * square_size, col * square_size:(col + 1) * square_size]

        # Preprocess the square for OCR
        square_gray = cv2.cvtColor(square, cv2.COLOR_BGR2GRAY)
        square_blur = cv2.GaussianBlur(square_gray, (3, 3), 0)  # Reduce noise
        _, square_thresh = cv2.threshold(square_blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Debug: Save or display each square
        # cv2.imshow(f"Square [{row}, {col}]", square_thresh)
        # cv2.waitKey(0)

        # Use pytesseract to recognize text
        letter = pytesseract.image_to_string(square_thresh, config='--psm 10 -c tessedit_char_whitelist=RNBKQP')
        letter = letter.strip()

        # Append detected letter or '1' for empty square
        if letter:
            matrix_row.append(letter)
        else:
            matrix_row.append('1')
    matrix.append(matrix_row)

# Print the resulting matrix
for row in matrix:
    print(row)

# Optionally, display the processed chessboard
cv2.imshow('Chessboard', chessboard)
cv2.waitKey(0)
cv2.destroyAllWindows()
