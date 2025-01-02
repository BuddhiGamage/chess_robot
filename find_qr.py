import pyrealsense2 as rs
import numpy as np
import cv2
from pyzbar.pyzbar import decode

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

        # Decode QR codes
        qr_codes = decode(color_image)
        for qr in qr_codes:
            data = qr.data.decode('utf-8')
            points = qr.polygon
            if len(points) == 4:
                # Draw bounding box around the QR code
                pts = np.array([(point.x, point.y) for point in points], dtype=np.int32)
                cv2.polylines(color_image, [pts], True, (0, 255, 0), 2)

            # Display the detected QR code data
            cv2.putText(color_image, data, (qr.rect.left, qr.rect.top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            print(f"Detected: {data}")

        # Display the image
        cv2.imshow("RealSense QR Code Detection", color_image)

        # Exit on 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    # Stop the pipeline
    pipeline.stop()
    cv2.destroyAllWindows()
