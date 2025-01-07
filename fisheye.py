import cv2
import numpy as np

# Load the image
image = cv2.imread('output_image.png')

# Show the image and wait for user input to select corners
# You need to click on the four corners of the chessboard

def select_points(event, x, y, flags, param):
    global points
    if event == cv2.EVENT_LBUTTONDOWN:
        points.append((x, y))
        print(f"Point selected: ({x}, {y})")
        if len(points) == 4:
            cv2.destroyAllWindows()

# Initialize list to store points
points = []

# Display image and wait for clicks
cv2.imshow('Select Corners', image)
cv2.setMouseCallback('Select Corners', select_points)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Check if four points are selected
if len(points) != 4:
    raise ValueError("Please select exactly four points (corners).")

# Convert points to numpy array of float32 type
src_points = np.float32(points)

# Define the destination points (top-down view of chessboard)
# These will be the four corners of the chessboard in a rectangle
height, width = 800, 800  # Set this to the desired output size
dst_points = np.float32([[0, 0], [width, 0], [width, height], [0, height]])

# Calculate the homography matrix
matrix, _ = cv2.findHomography(src_points, dst_points)

# Apply the perspective transformation
warped_image = cv2.warpPerspective(image, matrix, (width, height))

# Save or display the corrected image
cv2.imwrite('corrected_chessboard.jpg', warped_image)
cv2.imshow('Corrected Chessboard', warped_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
