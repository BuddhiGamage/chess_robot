import cv2
import numpy as np
from PIL import Image

def extract_chessboard(image_path):
    # Load the image
    image = cv2.imread(image_path)
    original = image.copy()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply GaussianBlur and Edge Detection
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)

    # Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)  # Sort by area

    # Look for the largest quadrilateral
    chessboard_contour = None
    for contour in contours:
        perimeter = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)  # Approximate contour
        if len(approx) == 4:  # Quadrilateral
            chessboard_contour = approx
            break

    if chessboard_contour is None:
        raise ValueError("Chessboard not found in the image.")

    # Apply perspective transformation
    points = chessboard_contour.reshape(4, 2)
    rect = order_points(points)

    # Define dimensions of the output chessboard image
    max_dim = 800  # Adjust this based on the desired size
    dst = np.array([
        [0, 0],
        [max_dim - 1, 0],
        [max_dim - 1, max_dim - 1],
        [0, max_dim - 1]
    ], dtype="float32")

    # Perspective transform
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(original, M, (max_dim, max_dim))

    return warped

def order_points(pts):
    # Order points: top-left, top-right, bottom-right, bottom-left
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]

    return rect


def remove_border_and_resize(image_path, border_width=40, output_size=(800, 800)):
    """
    Removes the border from the given image and resizes it to the specified output size.

    Args:
        image_path: Path to the image file.
        border_width: Width of the border to remove (in pixels).
        output_size: Tuple representing the desired output width and height.

    Returns:
        A new Image object with the border removed and resized.
    """

    try:
        img = Image.open(image_path)

        width, height = img.size

        # Calculate the new dimensions of the image without the border
        new_width = width - 2 * border_width
        new_height = height - 2 * border_width

        # Crop the image
        left = border_width
        top = border_width
        right = width - border_width
        bottom = height - border_width
        cropped_img = img.crop((left, top, right, bottom))

        # Resize the image
        resized_img = cropped_img.resize(output_size)

        return resized_img

    except FileNotFoundError:
        print(f"Error: Image file not found at '{image_path}'.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
# Usage
image_path = "/home/buddhi/Projects/chess_robot/output_image.png"  # Replace with your image path
try:
    chessboard = extract_chessboard(image_path)
    # cv2.imshow("Extracted Chessboard", chessboard)
    # cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Optionally save the extracted chessboard
    cv2.imwrite("extracted_chessboard.jpg", chessboard)
except ValueError as e:
    print("Error:", e)
