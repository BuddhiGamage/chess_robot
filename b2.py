import cv2
import numpy as np

# Load the image
image = cv2.imread('/home/buddhi/Projects/chess_robot/extracted_chessboard.jpg')

# Convert to grayscale
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

gray_inv = cv2.bitwise_not(gray)

# Apply binary thresholding (you can try different thresholding techniques)
_, binary_image = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY_INV)


# Apply binary thresholding (you can try different thresholding techniques)
_, inverted_binary_image = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY)

# Otsu's thresholding after Gaussian filtering
blur = cv2.GaussianBlur(gray,(5,5),0)
ret3,oth = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

th3 = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
            cv2.THRESH_BINARY,15,40)

# Optional: Denoising the image
th3 = cv2.medianBlur(th3, 3)

# # Invert the binary image (black becomes white, white becomes black)
# inverted_binary_image = cv2.bitwise_not(binary_image)


# Optional: Denoising the image
binary_image = cv2.medianBlur(binary_image, 3)

# Show the result
cv2.imshow('Detected Letters', th3)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Optional: Denoising the image
inverted_binary_image = cv2.medianBlur(inverted_binary_image, 3)

# Remove 40 pixels from all four sides
height, width = inverted_binary_image.shape[:2]
image_cropped = inverted_binary_image[40:height-40, 40:width-40]

# Add a white border of 40 pixels to the cropped image
inverted_binary_image = cv2.copyMakeBorder(image_cropped, 40, 40, 40, 40, cv2.BORDER_CONSTANT, value=(0, 0, 0))



# Find contours
contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Find contours
contours_inv, _ = cv2.findContours(inverted_binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Iterate over contours and draw bounding boxes
for contour in contours:
    # Get bounding box for each contour
    x, y, w, h = cv2.boundingRect(contour)
    
    # Filter out small contours (you can adjust this threshold based on your image)
    if w >5 and h > 5:  # Threshold for bounding box size
        # Draw a rectangle around each detected letter
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

# # Iterate over contours and draw bounding boxes
# for contour in contours_inv:
#     # Get bounding box for each contour
#     x, y, w, h = cv2.boundingRect(contour)
    
#     # Filter out small contours (you can adjust this threshold based on your image)
#     if w > 10 and h > 10:  # Threshold for bounding box size
#         # Draw a rectangle around each detected letter
#         cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

# Show the result
# cv2.imshow('Detected Letters', image)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
