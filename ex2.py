import cv2
import numpy as np

def find_border_width_chessboard(image_path):
    # Load the image
    image = cv2.imread(image_path)

    # Convert to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur to reduce noise
    blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 0)

    # Perform edge detection using Canny
    edges = cv2.Canny(blurred_image, 100, 200)

    # Use Hough line transform to detect lines in the image
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=100, maxLineGap=10)

    if lines is not None:
        # Initialize variables to store the boundary lines
        left, right, top, bottom = float('inf'), -float('inf'), float('inf'), -float('inf')

        # Loop through the lines detected by Hough Transform
        for line in lines:
            x1, y1, x2, y2 = line[0]

            # Find the extreme points (left, right, top, bottom) of the lines
            left = min(left, x1, x2)
            right = max(right, x1, x2)
            top = min(top, y1, y2)
            bottom = max(bottom, y1, y2)

        # Calculate the border width by measuring the distance from image edges
        border_left = left
        border_right = image.shape[1] - right
        border_top = top
        border_bottom = image.shape[0] - bottom

        # The border width can be the minimum distance from any edge
        border_width = min(border_left, border_right, border_top, border_bottom)

        return border_width
    else:
        print("No lines detected!")
        return None

# Example usage:
image_path = '/home/buddhi/Projects/chess_robot/extracted_chessboard.jpg'
border_width = find_border_width_chessboard(image_path)

if border_width is not None:
    print(f"Border width: {border_width} pixels")
