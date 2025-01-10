import cv2
import matplotlib.pyplot as plt
import numpy as np

# Load the image
image_path = "/home/buddhi/Projects/chess_robot/extracted_chessboard.jpg"  # Replace with the path to your image
image = cv2.imread(image_path)


# Convert the image to the HSV color space to extract green regions
hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# Define the wider range of green color in HSV
lower_green1 = np.array([30, 40, 40])  # Lower bound for green (first range)
upper_green1 = np.array([60, 255, 255]) # Upper bound for first range of green

lower_green2 = np.array([60, 80, 50])  # Lower bound for second range of green
upper_green2 = np.array([80, 255, 255]) # Upper bound for second range of green

# Create masks for the different green ranges in the image
mask1 = cv2.inRange(hsv_image, lower_green1, upper_green1)
mask2 = cv2.inRange(hsv_image, lower_green2, upper_green2)

# Combine all masks into one mask (OR operation)
green_mask = cv2.bitwise_or(mask1, mask2)

# Create an output image with all regions set to white
output_image = np.ones_like(image) * 255

# Set the green regions to black (where the mask is 255, i.e., the green region)
output_image[green_mask == 255] = [0, 0, 0]

# Convert the output image to grayscale (black for green and white for others)
output_gray = cv2.cvtColor(output_image, cv2.COLOR_BGR2GRAY)

cv2.imshow("Detected Green Rectangles", output_gray)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Detect ArUco markers in the grayscale image
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
aruco_params = cv2.aruco.DetectorParameters()

# Detect the markers in the image
detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)

# Detect markers in the binary image (now black and white)
corners, ids, rejected = detector.detectMarkers(output_gray)

# Draw detected markers on the original image
if ids is not None:
    print(f"Detected marker IDs: {ids.flatten()}")
    detected_image = cv2.aruco.drawDetectedMarkers(image.copy(), corners, ids)
else:
    print("No markers detected.")
    detected_image = image

# Display the result
plt.imshow(cv2.cvtColor(detected_image, cv2.COLOR_BGR2RGB))
plt.axis('off')
plt.title("Wider Green Regions and Detected ArUco Markers")
plt.show()
