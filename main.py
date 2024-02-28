import ctypes
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton, \
    QSplashScreen
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

# Load the shared library
cobra_lib = ctypes.CDLL('./cobraImplementation/libcobra128.so')

# Define the argument types for the setup, crypt, and decrypt functions
cobra_lib.setup.argtypes = [ctypes.POINTER(ctypes.c_ubyte * 72)]
cobra_lib.crypt.argtypes = [ctypes.POINTER(ctypes.c_uint32 * 4)]
cobra_lib.decrypt.argtypes = [ctypes.POINTER(ctypes.c_uint32 * 4)]


class EmailSenderGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Set the window properties
        self.setWindowTitle('Email Sender')
        self.setGeometry(100, 100, 400, 300)

        # Create a vertical layout for the main window
        mainLayout = QVBoxLayout()

        # Add widgets to the layout
        self.toLabel = QLabel('To:')
        self.toLineEdit = QLineEdit()
        self.subjectLabel = QLabel('Subject:')
        self.subjectLineEdit = QLineEdit()
        self.bodyLabel = QLabel('Body:')
        self.bodyTextEdit = QTextEdit()

        # Create a horizontal layout for the button
        buttonLayout = QHBoxLayout()
        self.sendButton = QPushButton('Send Email')
        self.sendButton.clicked.connect(self.sendEmail)
        self.sendButton.setFixedWidth(200)

        # Add stretch to both sides of the button to center it
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.sendButton)
        buttonLayout.addStretch()

        # Add widgets and layouts to the main layout
        mainLayout.addWidget(self.toLabel)
        mainLayout.addWidget(self.toLineEdit)
        mainLayout.addWidget(self.subjectLabel)
        mainLayout.addWidget(self.subjectLineEdit)
        mainLayout.addWidget(self.bodyLabel)
        mainLayout.addWidget(self.bodyTextEdit)
        mainLayout.addLayout(buttonLayout)  # Add the button layout

        # Set the layout on the application's window
        self.setLayout(mainLayout)

    def sendEmail(self):
        print("Starting email sending process...")

        # Dummy key for demonstration. Replace with your actual key material.
        key_material = (ctypes.c_ubyte * 72)(*([0] * 72))
        cobra_lib.setup(key_material)

        message_text = self.bodyTextEdit.toPlainText()
        message_bytes = message_text.encode('utf-8')

        # Pad the message_bytes to match the block size (16 bytes for Cobra128)
        pad_length = 16 - len(message_bytes) % 16
        padded_message = message_bytes + b'\x00' * pad_length
        print(f"Padded message bytes: {padded_message}")

        if len(padded_message) % 16 != 0:
            print("Message padding error.")
            return

        # Prepare the message block for encryption
        message_block = (ctypes.c_uint32 * 4)(
            int.from_bytes(padded_message[0:4], 'big'),
            int.from_bytes(padded_message[4:8], 'big'),
            int.from_bytes(padded_message[8:12], 'big'),
            int.from_bytes(padded_message[12:16], 'big'),
        )
        print(f"Message block (before encryption): {[hex(x) for x in message_block]}")

        # Encrypt the block
        cobra_lib.crypt(message_block)
        print(f"Encrypted message block: {[hex(x) for x in message_block]}")

        # Decrypt the block for demonstration
        cobra_lib.decrypt(message_block)
        decrypted_bytes = bytearray()
        for value in message_block:
            decrypted_bytes.extend(value.to_bytes(4, 'big'))
        decrypted_text = decrypted_bytes.rstrip(b'\x00').decode('utf-8')
        print(f"Decrypted text: {decrypted_text}")


def main():
    app = QApplication(sys.argv)

    # Assuming you have a splash image called "splash_image.png"
    splash_pix = QPixmap("splash/frame_00_delay-0.07s.gif")
    splash = QSplashScreen(splash_pix, Qt.WindowType.WindowStaysOnTopHint)
    splash.show()

    # Simulate some load time
    app.processEvents()

    window = EmailSenderGUI()
    window.show()

    splash.finish(window)
    sys.exit(app.exec())


if __name__ == '__main__':
    main()

# import ctypes
# import sys
# from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton, \
#     QSplashScreen
# from PyQt6.QtGui import QPixmap
# from PyQt6.QtCore import Qt
# cobra_lib = ctypes.CDLL('cobraImplementation/libcobra128.so')
#
#
# class EmailSenderGUI(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.initUI()
#
#     def initUI(self):
#         # Set the window properties
#         self.setWindowTitle('Email Sender')
#         self.setGeometry(100, 100, 400, 300)
#
#         # Create a vertical layout for the main window
#         mainLayout = QVBoxLayout()
#
#         # Add widgets to the layout
#         self.toLabel = QLabel('To:')
#         self.toLineEdit = QLineEdit()
#         self.subjectLabel = QLabel('Subject:')
#         self.subjectLineEdit = QLineEdit()
#         self.bodyLabel = QLabel('Body:')
#         self.bodyTextEdit = QTextEdit()
#
#         # Create a horizontal layout for the button
#         buttonLayout = QHBoxLayout()
#         self.sendButton = QPushButton('Send Email')
#         self.sendButton.clicked.connect(self.sendEmail)
#         self.sendButton.setFixedWidth(200)
#
#         # Add stretch to both sides of the button to center it
#         buttonLayout.addStretch()
#         buttonLayout.addWidget(self.sendButton)
#         buttonLayout.addStretch()
#
#         # Add widgets and layouts to the main layout
#         mainLayout.addWidget(self.toLabel)
#         mainLayout.addWidget(self.toLineEdit)
#         mainLayout.addWidget(self.subjectLabel)
#         mainLayout.addWidget(self.subjectLineEdit)
#         mainLayout.addWidget(self.bodyLabel)
#         mainLayout.addWidget(self.bodyTextEdit)
#         mainLayout.addLayout(buttonLayout)  # Add the button layout
#
#         # Set the layout on the application's window
#         self.setLayout(mainLayout)
#
#     def sendEmail(self):
#         # Implementation of email sending functionality
#         print("Sending Email...")
#         print(f"To: {self.toLineEdit.text()}")
#         print(f"Subject: {self.subjectLineEdit.text()}")
#         print(f"Body: {self.bodyTextEdit.toPlainText()}")
#
#
# def main():
#     app = QApplication(sys.argv)
#
#     # Assuming you have a splash image called "splash_image.png"
#     splash_pix = QPixmap("splash_image.png")
#     splash = QSplashScreen(splash_pix, Qt.WindowType.WindowStaysOnTopHint)
#     splash.show()
#
#     # Simulate some load time
#     app.processEvents()
#
#     window = EmailSenderGUI()
#     window.show()
#
#     splash.finish(window)
#     sys.exit(app.exec())
#
#
# if __name__ == '__main__':
#     main()