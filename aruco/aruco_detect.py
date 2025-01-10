import cv2
import matplotlib.pyplot as plt

# Load the image
# image_path = "/home/buddhi/Projects/chess_robot/extracted_chessboard.jpg"  # Replace with the path to your image
image_path = '/home/buddhi/Projects/chess_robot/output_image.png'
image = cv2.imread(image_path)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # Convert to grayscale

# Display the image with bounding boxes
cv2.imshow("Detected Red Rectangles", gray)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Define the dictionary we used to generate the marker
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
aruco_params = cv2.aruco.DetectorParameters()

# Detect the markers in the image
detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)
corners, ids, rejected = detector.detectMarkers(gray)

# Draw detected markers on the image
if ids is not None:
    print(f"Detected marker IDs: {ids.flatten()}")
    detected_image = cv2.aruco.drawDetectedMarkers(image.copy(), corners, ids)
else:
    print("No markers detected.")
    detected_image = image

# Display the result
plt.imshow(cv2.cvtColor(detected_image, cv2.COLOR_BGR2RGB))
plt.axis('off')
plt.title("Detected ArUco Markers")
plt.show()
