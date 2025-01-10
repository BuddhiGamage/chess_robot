import cv2
import matplotlib.pyplot as plt
import numpy as np

# Load the image
image_path = "/home/buddhi/Projects/chess_robot/aruco/Screenshot from 2025-01-09 12-32-33.png"  # Replace with the path to your image
image = cv2.imread(image_path)

# Resize the image to ensure it's 800x800
image = cv2.resize(image, (100, 100))

# Convert the image to the HSV color space to extract red regions
hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# Define the range of red color in HSV
lower_red = np.array([0, 120, 70])   # Lower bound of red color
upper_red = np.array([10, 255, 255]) # Upper bound for one range of red
lower_red2 = np.array([170, 120, 70])  # Another range of red for hues close to 180
upper_red2 = np.array([180, 255, 255])

# Create a mask for red areas in the image
mask1 = cv2.inRange(hsv_image, lower_red, upper_red)
mask2 = cv2.inRange(hsv_image, lower_red2, upper_red2)
red_mask = cv2.bitwise_or(mask1, mask2)

# Create an output image with all regions set to white
output_image = np.ones_like(image) * 255

# Set the red regions to black (where the mask is 255, i.e., the red region)
output_image[red_mask == 255] = [0, 0, 0]

# Convert the output image to grayscale (black for red and white for others)
output_gray = cv2.cvtColor(output_image, cv2.COLOR_BGR2GRAY)


cv2.imshow("Detected Red Rectangles", output_gray)
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
plt.title("Red Regions to Black and Detected ArUco Markers")
plt.show()
