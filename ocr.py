import pyrealsense2 as rs
import numpy as np
import cv2
import pytesseract

# Configure Tesseract executable path (if needed)
# pytesseract.pytesseract.tesseract_cmd = r'<path_to_tesseract_executable>'

# Initialize RealSense pipeline
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 10)

# Start the camera
pipeline.start(config)

try:
    print("Press Ctrl+C to exit.")
    while True:
        # Capture frames from the RealSense camera
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        if not color_frame:
            continue

        # Convert RealSense frame to a NumPy array
        color_image = np.asanyarray(color_frame.get_data())

        # Convert image to grayscale for better OCR performance
        gray_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)

        # Perform OCR to get character-level bounding boxes
        h, w, _ = color_image.shape  # Image dimensions
        char_boxes = pytesseract.image_to_boxes(gray_image)

        # Draw bounding boxes around each character and print character data
        for box in char_boxes.splitlines():
            char, x1, y1, x2, y2, _ = box.split()
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

            # In Tesseract, origin (0,0) is bottom-left, so we need to adjust
            y1, y2 = h - y1, h - y2

            # Draw bounding box for the character
            cv2.rectangle(color_image, (x1, y2), (x2, y1), (0, 255, 0), 2)

            # Put the character above the box
            cv2.putText(color_image, char, (x1, y2 - 10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (0, 0, 255), 1)

            # Print the character to the terminal
            print(f"Character: {char}, Coordinates: ({x1}, {y2}), ({x2}, {y1})")

        # Display the image
        cv2.imshow("RealSense OCR Character Detection", color_image)

        # Exit on 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    # Stop the pipeline
    pipeline.stop()
    cv2.destroyAllWindows()
