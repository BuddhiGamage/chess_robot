import cv2
import numpy as np

# Load the image
image = cv2.imread('/home/buddhi/Projects/chess_robot/extracted_chessboard.jpg')

# Upsample the image if the resolution is too low
# Resize it to double the size (you can adjust the scale factor as needed)
image = cv2.resize(image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

# Convert the image to the HSV color space
hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# Define a wider range of green color in HSV
lower_green = np.array([30, 40, 40])  # Lower bound of green
upper_green = np.array([90, 255, 255])  # Upper bound of green

# Create a mask that captures all green objects
mask = cv2.inRange(hsv, lower_green, upper_green)

# Create an output image where green objects are black and all others are white
output = np.zeros_like(image)
output[mask != 0] = [0, 0, 0]  # Green objects will be black
output[mask == 0] = [255, 255, 255]  # Non-green objects will be white

# Show the output image
cv2.imshow('Green Objects in Black', output)
cv2.waitKey(0)
cv2.destroyAllWindows()
