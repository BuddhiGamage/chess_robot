import cv2
import os
import numpy as np

# Define the dictionary we want to use (4x4 markers)
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)

# Directory to save the markers
output_dir = "aruco_markers"
os.makedirs(output_dir, exist_ok=True)

# Generate 12 markers with IDs from 0 to 11
num_markers = 12
marker_size = 200  # Size in pixels
white_boundary_size = 0  # White boundary size in pixels
black_border_size = 1  # Black border size in pixels

for marker_id in range(num_markers):
    # Generate the marker (black and white)
    marker_image = cv2.aruco.generateImageMarker(aruco_dict, marker_id, marker_size)
    
    # Convert the marker to red (change black regions to red)
    red_marker = np.zeros((marker_size, marker_size, 3), dtype=np.uint8)
    red_marker[marker_image == 0] = [0, 0, 255]  # Set black pixels to red
    red_marker[marker_image == 255] = [255, 255, 255]  # Set white pixels to white
    
    # Create a new image with a white boundary
    bordered_marker = np.ones((marker_size + 2 * white_boundary_size, marker_size + 2 * white_boundary_size, 3), dtype=np.uint8) * 255
    
    # Place the red marker on the new image (centered)
    bordered_marker[white_boundary_size:white_boundary_size + marker_size, white_boundary_size:white_boundary_size + marker_size] = red_marker
    
    # Add a black border around the white boundary
    final_marker = np.ones((bordered_marker.shape[0] + 2 * black_border_size, bordered_marker.shape[1] + 2 * black_border_size, 3), dtype=np.uint8) * 255
    final_marker[black_border_size:black_border_size + bordered_marker.shape[0], black_border_size:black_border_size + bordered_marker.shape[1]] = bordered_marker
    final_marker[0:black_border_size, :] = 0  # Top black border
    final_marker[-black_border_size:, :] = 0  # Bottom black border
    final_marker[:, 0:black_border_size] = 0  # Left black border
    final_marker[:, -black_border_size:] = 0  # Right black border

    # Save the marker with the boundaries as an image
    file_path = os.path.join(output_dir, f'marker_{marker_id}.png')
    cv2.imwrite(file_path, final_marker)

print(f"Generated {num_markers} red markers with a {white_boundary_size}px white boundary and a {black_border_size}px black border, and saved them in '{output_dir}' directory.")
