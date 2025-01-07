import pytesseract
import cv2

# Load the image
image_path = '/home/buddhi/Projects/chess_robot/extracted_chessboard.jpg'
# image_path = '/home/buddhi/Projects/chess_robot/output_image.png'
image = cv2.imread(image_path)

# Convert the image to grayscale (optional, but often helps with OCR)
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


th3 = cv2.adaptiveThreshold(gray_image,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
            cv2.THRESH_BINARY,33,25)

# Optional: Denoising the image
th3 = cv2.medianBlur(th3, 3)


# # Show the result
# cv2.imshow('Detected Letters', th3)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

# Use pytesseract to get the bounding boxes of each character
h, w, _ = image.shape
boxes = pytesseract.image_to_boxes(th3)

# Loop through the boxes and draw them on the image with the corresponding character
for b in boxes.splitlines():
    b = b.split()
    character = b[0]
    x, y, w_char, h_char = int(b[1]), int(b[2]), int(b[3]), int(b[4])
    
    # Draw rectangle around the character
    cv2.rectangle(image, (x, h - y), (w_char, h - h_char), (0, 255, 0), 2)
    
    # Put the character text on top of the bounding box
    cv2.putText(image, character, (x, h - y + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

# Show the image with bounding boxes and characters
cv2.imshow('Image with Bounding Boxes and Characters', image)
cv2.waitKey(0)
cv2.destroyAllWindows()
