import qrcode
from io import BytesIO
from django.core.files import File
import re

def generate_qr_code(userevent_id):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    data = f"user_id:{userevent_id}"
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')

    # Save the QR code to a file or return as a response
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return File(buffer)



def normalize_code(raw_title: str) -> str:
    """
    Normalize title to generate a unique code:
    - Remove all non-alphanumeric characters
    - Remove spaces, dashes, underscores, etc.
    - Convert to uppercase
    """
    alphanum_only = re.sub(r"[^a-zA-Z0-9]", "", raw_title)
    return alphanum_only.upper()
