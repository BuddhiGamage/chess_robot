import cv2
import numpy as np

# Load the image
image = cv2.imread('/home/buddhi/Projects/chess_robot/extracted_chessboard_no_border.jpg')

# Convert to grayscale
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Apply binary thresholding (you can try different thresholding techniques)
_, binary_image = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY_INV)

# Optional: Denoising the image
binary_image = cv2.medianBlur(binary_image, 3)

# Invert the binary image (black becomes white, white becomes black)
inverted_binary_image = cv2.bitwise_not(binary_image)

cv2.imshow('Inverted', inverted_binary_image)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Find contours
contours, _ = cv2.findContours(inverted_binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Iterate over contours and show each cropped contour one by one
for idx, contour in enumerate(contours):
    # Get bounding box for each contour
    x, y, w, h = cv2.boundingRect(contour)
    
    # Filter out small contours (you can adjust this threshold based on your image)
    if w > 10 and h > 10:  # Threshold for bounding box size
        # Crop the region inside the bounding box
        cropped_image = image[y:y + h, x:x + w]
        
        # Show the cropped region
        cv2.imshow(f"Cropped Contour {idx + 1}", cropped_image)
        
        # Wait for key press to move to the next contour
        cv2.waitKey(0)

# Close all windows after processing
cv2.destroyAllWindows()
