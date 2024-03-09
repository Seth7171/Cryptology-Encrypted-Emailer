import asyncio
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton
from PyQt6.QtCore import Qt, QObject, pyqtSignal, pyqtSlot, QThread
from BlowFish import blowfish
import base64
import websockets
from EccElGamal.elgamal_class import ElgamalEncryption
from rabin.rabin_class import SignatureScheme
import env
import json


class WebSocketWorker(QObject):
    finished = pyqtSignal()
    messageReceived = pyqtSignal(str)

    @pyqtSlot(str)
    async def send_message(self, message):
        uri = "ws://localhost:6789"
        async with websockets.connect(uri) as websocket:
            # Ensure the message is in a string format
            if isinstance(message, bytes):
                message = message.decode()
            elif not isinstance(message, str):
                message = str(message)
            await websocket.send(message)
            if env.debug:
                print(f"> {message}")

            greeting = await websocket.recv()
            print(f"< {greeting}")
            self.messageReceived.emit(greeting)
        self.finished.emit()


def digital_signature(rabin_signature, msg):
    print(f"Signing with rabin: {msg}")
    # Sign the message
    signature = rabin_signature.get_signature(msg)
    if env.debug:
        print(f"Signature: (U, x) = {signature}")
    return signature


def encrypt_key(ecc):
    print("Encrypting blowfish key with el-gamal")
    if env.debug:
        print("Original key: ", blowfish.key_as_int())
    C1x, C1y, C2x, C2y = ecc.encrypt(blowfish.key_as_int())
    if env.debug:
        print(C1x, C1y, C2x, C2y)
        print("Decrypted key:", ecc.decrypt(C1x, C1y, C2x, C2y))
    return C1x, C1y, C2x, C2y


class EmailSenderGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.rabin_public_key = None
        self.elgamal_encrypted_key = None
        self.rabin_signed_elgamal_key = None
        self.rabin_signer = SignatureScheme()
        self.elgamal_encrypter = ElgamalEncryption()
        self.email = "lior.jigalo@google.com"
        self.credentials_thread = QThread()
        self.email_thread = QThread()
        self.setupWorkerAndThread()
        self.initUI()

    def setupWorkerAndThread(self):
        self.worker = WebSocketWorker()
        self.worker.moveToThread(self.email_thread)

        self.worker.finished.connect(self.email_thread.quit)
        self.worker.messageReceived.connect(self.onMessageReceived)
        self.email_thread.started.connect(self.triggerSendMessage)
        self.credentials_thread.started.connect(self.send_credentials)

    def triggerSendMessage(self):
        # Ensure this method correctly triggers sending the encrypted message
        message = {
            "from": self.email,
            "subject": self.subjectLineEdit.text(),
            "message": self.bodyTextEdit.toPlainText()
        }
        json_message = json.dumps(message)

        encrypted_message = blowfish.encrypt_text_with_blowfish(json_message)
        elgamal_encrypted_message = self.elgamal_encrypter.encrypt(self.string_to_int_representation(encrypted_message))

        digitally_signed_message = digital_signature(self.rabin_signer, str(elgamal_encrypted_message[0]) + ";"
                                                                      + str(elgamal_encrypted_message[1]) + ";"
                                                                      + str(elgamal_encrypted_message[2]) + ";"
                                                                      + str(elgamal_encrypted_message[3]))

        header = {
            "type": "email",
            "to": self.toLineEdit.text(),
            "msg": elgamal_encrypted_message,
            "dig_sign": digitally_signed_message
        }
        json_message = json.dumps(header)
        asyncio.run(self.worker.send_message(json_message))

    def send_credentials(self):
        # Assuming self.rabin_public_key is a tuple and self.rabin_signed_elgamal_key is a list of tuples/signatures
        credentials = {
            "type": "creds",
            "from": self.email,
            "rabin_public_key": self.rabin_public_key,
            "rabin_signed_public_elgamal_key": self.rabin_signed_elgamal_key
        }
        credentials_json = json.dumps(credentials)
        asyncio.run(self.worker.send_message(credentials_json))

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
        self.sendButton.clicked.connect(self.send_email)
        self.sendButton.setFixedWidth(200)

        # encryption setup
        blowfish.init()
        self.elgamal_encrypted_key = encrypt_key(self.elgamal_encrypter)

        self.rabin_signed_elgamal_key = [digital_signature(self.rabin_signer, str(self.elgamal_encrypted_key[0])),
                                         digital_signature(self.rabin_signer, str(self.elgamal_encrypted_key[1])),
                                         digital_signature(self.rabin_signer, str(self.elgamal_encrypted_key[2])),
                                         digital_signature(self.rabin_signer, str(self.elgamal_encrypted_key[3]))]
        if env.debug:
            print(self.rabin_signed_elgamal_key)

        self.rabin_public_key = self.rabin_signer.get_public_key()

        if not self.credentials_thread.isRunning():
            self.credentials_thread.start()

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

    def string_to_int_representation(self, input_string):
        return int(''.join(f"{ord(c):03}" for c in input_string))

    def send_email(self):
        print("Starting email sending process...")
        if not self.email_thread.isRunning():
            self.email_thread.start()

    def onMessageReceived(self, encoded_message):
        try:
            data = json.loads(encoded_message)
            if "status" in data:
                message_status = data["status"]
                if message_status == "Received":
                    return

            if "type" in data:
                message_type = data["type"]
                print(f"Message type: {message_type}")
                self.log_emitter.logMessage.emit(f"Message type: {message_type}")
                # Add your logic here based on the message type
                if message_type == "creds":
                    pass

                if message_type == "email":
                    pass
            else:
                print("Message does not contain a 'type' field.")
                self.log_emitter.logMessage.emit("Message does not contain a 'type' field.")

            # Decode the message from Base64
            message = base64.b64decode(encoded_message)
            decrypted = blowfish.decrypt_text_with_blowfish(message)
            if env.debug:
                print("Decrypted:", decrypted)
        except Exception as e:
            print(f"Error processing received message: {e}")

        except json.JSONDecodeError:
            print("Received message is not in valid JSON format.")
            self.log_emitter.logMessage.emit("Received message is not in valid JSON format.")



def main():
    app = QApplication(sys.argv)
    # Simulate some load time
    # app.processEvents()
    window = EmailSenderGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
