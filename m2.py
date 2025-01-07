import cv2
import time

# Constants
image_path = "extracted_chessboard.jpg"  # Replace with your image file path
image_size = 800  # Image dimensions (assume square image)
border = 40  # Border width in pixels
num_squares = 8  # Number of squares per row/column
square_size = (image_size - 2 * border) // num_squares  # Size of each square
extra_boundary = 20  # Additional boundary in pixels

# Load the image
image = cv2.imread(image_path)

if image is None:
    print("Error: Image not found.")
    exit()

# Resize the image to ensure it's 800x800
image = cv2.resize(image, (image_size, image_size))

# Create a copy of the image to draw on
output_image = image.copy()

# Traverse and visualize each square
for row in range(num_squares):
    for col in range(num_squares):
        # Calculate the square's top-left and bottom-right corners
        start_x = border + col * square_size
        start_y = border + row * square_size
        end_x = start_x + square_size
        end_y = start_y + square_size

        # Adjust the rectangle to include an additional 20-pixel boundary
        adjusted_start_x = max(start_x - extra_boundary, 0)
        adjusted_start_y = max(start_y - extra_boundary, 0)
        adjusted_end_x = min(end_x + extra_boundary, image_size)
        adjusted_end_y = min(end_y + extra_boundary, image_size)
        
        # Draw a rectangle around the square with the additional boundary
        highlighted_image = output_image.copy()
        cv2.rectangle(
            highlighted_image,
            (adjusted_start_x, adjusted_start_y),
            (adjusted_end_x, adjusted_end_y),
            (0, 255, 0),  # Green color
            2
        )
        
        # Add text to indicate the square's coordinates
        cv2.putText(
            highlighted_image,
            f"({row}, {col})",
            (start_x + 10, start_y + 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            1,
            cv2.LINE_AA
        )

        # Display the image with the highlighted square
        cv2.imshow("Checkerboard Traversal", highlighted_image)
        cv2.waitKey(200)  # Pause for 200 ms to visualize each square

# Close the window after traversing all squares
cv2.destroyAllWindows()
