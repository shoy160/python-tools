import qrcode

list = ("TC-S-WSJ0001", "TC-S-SP0001", "TC-S-SP0002", "TC-S-XCTCQ0001", "TC-S-DCTCQ0001", "TC-S-QXJ0001", "TC-S-SBJ0001", "TC-N-WSJ0001", "TC-N-SP0001", "TC-N-SP0002", "TC-N-XCTCQ0001", "TC-N-DCTCQ0001", "TC-N-QXJ0001", "TC-N-SBJ0001", "FM-E-WSJ0001", "FM-E-SP0001", "FM-E-SSL0001", "FM-E-XCTCQ0001", "FM-E-DCTCQ0001", "FM-E-QQJ0001", "FM-E-SBJ0001", "FM-W-WSJ0001", "FM-W-SP0001", "FM-W-SSL0001", "FM-W-XCTCQ0001", "FM-W-DCTCQ0001", "FM-W-QXJ0001", "FM-W-SBJ0001", "FJW-E-QXSBJ0001", "FJW-E-WSJ0001", "FJW-E-SP0001", "FJW-E-WHG0001", "FJW-E-XCTCQ0001", "FJW-E-DACTCQ002", "FJW-W-QXSBJ0001", "FJW-W-WSJ0001", "FJW-W-SP0001", "FJW-W-WHG0001", "FJW-W-XCTCQ0001", "FJW-W-DCTCQ", "QZ-S-WSJ0001", "QZ-S-SP0001", "QZ-S-XCTCQ0001", "QZ-S-DCTCQ0001", "QZ-S-QXJ0001", "QZ-S-SBJ0001", "QZ-N-WSJ0001", "QZ-N-SP001", "QZ-N-XCTCQ0001", "QZ-N-DCTCQ0001", "QZ-N-QXJ0001",
        "QZ-N-SBJ0001", "LD-S-WSJ0001", "LD-S-SP0001", "LD-S-SP0002", "LD-S-HYJ0001", "LD-S-XCTCQ0001", "LD-S-DCTCQ0001", "LD-S-QXSBJ0001", "LD-S-SSL0001", "LD-N-WSJ0001", "LD-N-SP0001", "LD-N-SP0002", "LD-N-HYJ0001", "LD-N-XCTCQ0001", "LD-N-DCTCQ0001", "LD-N-QXSBJ0001", "DT-S-WSJ0001", "DT-S-SP0001", "DT-S-XCTCQ0001", "DT-S-DCTCQ0001", "DT-S-QXJ0001", "DT-S-SBJ0001", "DT-N-WSJ0001", "DT-N-SP0001", "DT-N-XCTCQ0001", "DT-N-DCTCQ0001", "DT-N-QXJ0001", "DT-N-SBJ0001", "JY-E-WSJ0001", "JY-E-SP0001", "JY-E-SP0002", "JY-E-HYJ0001", "JY-E-QXSBJ0001", "JY-E-TCQ0001", "JY-W-WSJ0001", "JY-W-SP0001", "JY-W-SP01002", "JY-W-HYJ0001", "JY-W-HYJ0002", "JY-W-TCQ0001", "DC-S-WSJ0001", "DC-S-SP0001", "DC-S-SP0002", "DC-S-XCTCQ0001", "DC-S-DCTCQ0002", "DC-S-QXSBJ0001", "DC-N-WSJ0001", "DC-N-SP0001", "DC-N-SP0002", "DC-N-XCTCQ0001", "DC-N-DCTCQ0001", "DC-N-QXSBJ0001")


def make_code():
    for code in list:
        # img = qrcode.make(code)
        # img.show()
        qr = qrcode.QRCode(
            version=2, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4,)
        qr.add_data(code)
        qr.make(fit=True)
        img = qr.make_image()
        img.save("hainan/%s.jpg" % code)


if __name__ == "__main__":
    make_code()
