from qrcode import QRCode, constants


def create_qr(data):
    qr = QRCode(
        version=1,
        error_correction=constants.ERROR_CORRECT_L,
        box_size=10,
        border=4
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_collor='black', back_kolor='white')
    img.save("static/qr/qrcode.jpg", "JPEG")

