import qrcode
from PIL import Image

# Define the chess pieces and their encodings
# Define the chess pieces and their encodings
chess_pieces = {
    "P": "White Pawn",
    "R": "White Rook",
    "N": "White Knight",
    "B": "White Bishop",
    "Q": "White Queen",
    "K": "White King",
    "F": "Black Pawn",
    "T": "Black Rook",
    "L": "Black Knight",
    "X": "Black Bishop",
    "E": "Black Queen",
    "M": "Black King"
}

# Target QR code size in mm
target_size_mm = 20
# Conversion factor: 1 mm = 3.78 pixels
pixels_per_mm = 3.78
target_size_px = int(target_size_mm * pixels_per_mm)

# Generate and save QR codes
for code, label in chess_pieces.items():
    # Create the QR code
    qr = qrcode.QRCode(
        version=1,  # Version 1: 21x21 matrix, sufficient for this use
        error_correction=qrcode.constants.ERROR_CORRECT_M,  # Medium error correction
        box_size=10,  # Adjust for scaling
        border=1  # Standard border
    )
    qr.add_data(code)  # Add the piece code as data
    qr.make(fit=True)

    # Create the image
    qr_img = qr.make_image(fill_color="black", back_color="white")

    # # Resize to the target size
    # qr_img = qr_img.resize((target_size_px, target_size_px))

    # Save the image
    file_name = f"qr_codes/{label}.png"
    qr_img.save(file_name)
    print(f"Saved QR code for {label} as {file_name}")
