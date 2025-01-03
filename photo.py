import pyrealsense2 as rs
import numpy as np
import cv2

def capture_image_from_realsense(output_filename="captured_image.png"):
    try:
        # Configure depth and color streams
        pipeline = rs.pipeline()
        config = rs.config()
        # config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 15)

        # Start streaming
        pipeline.start(config)

        print("Waiting for a frame...")
        # Wait for a coherent pair of frames: depth and color
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()

        if not color_frame:
            print("No color frame detected.")
            return

        # Convert image to numpy array
        color_image = np.asanyarray(color_frame.get_data())

        # Save the captured image
        cv2.imwrite(output_filename, color_image)
        print(f"Image saved as {output_filename}")

        # # Display the captured image
        # cv2.imshow("Captured Image", color_image)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Stop streaming
        pipeline.stop()

# Call the function to capture an image
capture_image_from_realsense("output_image.png")
