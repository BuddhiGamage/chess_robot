import cv2
import numpy as np

def chessboard_to_matrix(image_path):
    """
    Converts a chessboard image with red rectangles to an 8x8 matrix.
    The red rectangles are detected and used as markers.

    Args:
        image_path: Path to the chessboard image.

    Returns:
        An 8x8 NumPy array representing the chessboard, 
        where '1' represents the presence of a red rectangle and '0' represents no rectangle.
    """

    # Load the image in BGR
    img = cv2.imread(image_path)

    # Constants
    image_size = 800  # Image dimensions (assume square image)  
    top_border = 38
    bottom_border = 38
    left_border = 37
    right_border = 35
    num_squares = 8
    square_width = (image_size - left_border - right_border) // num_squares
    square_height = (image_size - top_border - bottom_border) // num_squares
    extra_boundary = 5  # Small additional boundary for ROI

    # Resize the image to ensure it's 800x800
    img = cv2.resize(img, (image_size, image_size))

    # Convert to HSV color space for better color detection
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Define the lower and upper bounds for red in HSV
    lower_red_1 = np.array([0, 124, 124])   # First range of red (broader lower bounds)
    upper_red_1 = np.array([10, 255, 255]) # Slightly extended upper hue for better coverage
    lower_red_2 = np.array([170, 124, 124]) # Second range of red (broader lower bounds)
    upper_red_2 = np.array([180, 255, 255]) # Maximum hue remains unchanged


    # Create masks for both red ranges
    mask1 = cv2.inRange(hsv, lower_red_1, upper_red_1)
    mask2 = cv2.inRange(hsv, lower_red_2, upper_red_2)

    # Combine the masks
    mask = cv2.bitwise_or(mask1, mask2)

    # Apply morphological operations to clean the mask
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)  # Close small gaps
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)   # Remove small noise
    
     # Optional: Display the mask for debugging
    cv2.imshow("Red Mask", mask)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Create an empty 8x8 matrix
    matrix = np.zeros((8, 8), dtype=int)

    # Iterate through each square on the chessboard
    for row in range(num_squares):
        for col in range(num_squares):
            start_y = top_border + row * square_height
            start_x = left_border + col * square_width
            end_y = start_y + square_height
            end_x = start_x + square_width

            # Expand ROI boundaries slightly
            adjusted_start_x = max(start_x - extra_boundary, 0)
            adjusted_start_y = max(start_y - extra_boundary, 0)
            adjusted_end_x = min(end_x + extra_boundary, image_size)
            adjusted_end_y = min(end_y + extra_boundary, image_size)

            # Extract the ROI from the mask
            roi = mask[adjusted_start_y:adjusted_end_y, adjusted_start_x:adjusted_end_x]

           

            # Find contours within the ROI
            contours, _ = cv2.findContours(roi, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Check for a red rectangle
            red_detected = False
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)

                # Filter contours based on size and aspect ratio
                if w > 10 and h > 10 and 0.8 <= w / h <= 1.2:  # Ensure rectangular shape
                    red_detected = True
                    break

            # Update the matrix based on detection
            matrix[row][col] = 1 if red_detected else 0

    return matrix

# Example usage
# image_path = '/home/buddhi/Projects/chess_robot/extracted_chessboard.jpg'
# chessboard_matrix = chessboard_to_matrix(image_path)
# print(chessboard_matrix)
