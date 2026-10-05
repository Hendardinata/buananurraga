import io
import base64
import qrcode
from PIL import Image

class QRGenerator:
    """
    Generator for scannable, high-contrast QR Codes
    for official Buana Nurraga KTA verification.
    """

    @staticmethod
    def generate_base64(data_url: str, box_size: int = 8, border: int = 2) -> str:
        """
        Generates a PNG QR Code as a base64 data URI string.
        """
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=box_size,
            border=border,
        )
        qr.add_data(data_url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{encoded}"

    @staticmethod
    def generate_pil_image(data_url: str, box_size: int = 10, border: int = 2) -> Image.Image:
        """
        Generates a PIL Image object of the QR code.
        """
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=box_size,
            border=border,
        )
        qr.add_data(data_url)
        qr.make(fit=True)
        return qr.make_image(fill_color="black", back_color="white").convert("RGB")
