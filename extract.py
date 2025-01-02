from PIL import Image

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

# Example usage:
image_path = "extracted_chessboard.jpg"  # Replace with the actual path
output_path = "extracted_chessboard_no_border.jpg"  # Replace with the desired output path

try:
    resized_image = remove_border_and_resize(image_path)

    if resized_image:
        resized_image.save(output_path)
        print(f"Cropped and resized image saved to '{output_path}'.")
except Exception as e:
    print(f"An error occurred: {e}")