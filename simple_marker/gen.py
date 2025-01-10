import cv2
import numpy as np

# Define the size of the image (e.g., 100x100 pixels)
width, height = 100, 100

# Create a blank white image
image = np.ones((height, width, 3), dtype=np.uint8) * 255  # white background

# Define the color red (in BGR format)
red_color = (0, 0, 255)

# Define the position and size of the rectangle (x, y, width, height)
rect_x, rect_y, rect_w, rect_h = 15, 15, 70, 70

# Draw a filled red rectangle
cv2.rectangle(image, (rect_x, rect_y), (rect_x + rect_w, rect_y + rect_h), red_color, thickness=cv2.FILLED)

# Define the border color (black) and thickness (1px)
border_color = (0, 0, 0)  # black color
border_thickness = 1

# Draw a 1px border around the image
cv2.rectangle(image, (0, 0), (width-1, height-1), border_color, thickness=border_thickness)

# Save the image to a file
cv2.imwrite('red_rectangle_with_border.png', image)

# Display the image
cv2
