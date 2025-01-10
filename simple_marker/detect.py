import cv2
import numpy as np

# Load the image with the chess pieces and markers
image = cv2.imread('/home/buddhi/Projects/chess_robot/extracted_chessboard.jpg')

# Check if the image is loaded correctly
if image is None:
    raise ValueError("Image not found. Please check the file path.")

# Get the original image dimensions
original_height, original_width = image.shape[:2]

# Convert to HSV (Hue, Saturation, Value) color space for better color detection
hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# # Define the lower and upper bounds for red in HSV
# lower_red_1 = np.array([0, 150, 150])   # First range of red
# upper_red_1 = np.array([10, 255, 255])
# lower_red_2 = np.array([170, 150, 150]) # Second range of red
# upper_red_2 = np.array([180, 255, 255])

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

# Apply morphological operations to reduce noise
kernel = np.ones((5, 5), np.uint8)
mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)  # Close small gaps
mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)   # Remove small noise

# Optional: Display the mask for debugging
cv2.imshow("Red Mask", mask)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Find contours in the mask
contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Loop through each contour to process
for contour in contours:
    # Get the bounding box of the contour
    x, y, w, h = cv2.boundingRect(contour)

    # Dynamically filter out small contours based on image size
    if w > original_width * 0.01 and h > original_height * 0.01:  # Adjust threshold as needed
        # Draw a green bounding box around the red rectangle
        cv2.rectangle(image, (x - 10, y - 10), (x + w + 10, y + h + 10), (0, 255, 0), 3)

        # Get the rotated bounding box
        rect = cv2.minAreaRect(contour)
        box = cv2.boxPoints(rect)  # Get the four corners of the bounding box
        # box = np.int8(box)
        box = np.array(box).reshape((-1, 1, 2)).astype(np.int32)

        # Draw the rotated rectangle in red
        cv2.drawContours(image, [box], 0, (0, 0, 255), 2)

        # Get the rotation angle of the bounding box
        angle = rect[2]
        if angle < -45:
            angle += 90

        # Prepare text for rotation details
        rotation_text = f"Angle: {angle:.2f}°"
        box_text = f"Box: ({x}, {y}) - {w}x{h}"

        # Display rotation details on the image in blue
        cv2.putText(image, rotation_text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2, cv2.LINE_AA)
        cv2.putText(image, box_text, (x, y + h + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2, cv2.LINE_AA)

# Display the final image with detected rectangles and rotation details
cv2.imshow('Detected Red Rectangles', image)
cv2.waitKey(0)
cv2.destroyAllWindows()
