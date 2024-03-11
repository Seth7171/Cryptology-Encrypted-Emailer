import base64
import json
import os
import shutil
import sys
import uuid
import random
import traceback

from PyQt6.QtCore import QThread, Qt, QObject, pyqtSignal
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton, \
    QListWidget, QListWidgetItem

import env
from BlowFish import blowfish
from EccElGamal.elgamal_class import ElgamalEncryption
from rabin.rabin_class import SignatureScheme


def save_message_to_json(message, file_path):
    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as file:
        json.dump(message, file, indent=4)


def digital_signature(rabin_signature, msg):
    print(f"Signing with rabin: {msg}")
    # Sign the message
    signature = rabin_signature.get_signature(msg)
    if env.debug:
        print(f"Signature: (U, x) = {signature}")
    return signature


def encrypt_key(ecc):
    print("Encrypting blowfish key with el-gamal")
    print("last email key: ", blowfish.key_as_int())
    C1x, C1y, C2x, C2y = ecc.encrypt(blowfish.key_as_int())
    if env.debug:
        print(C1x, C1y, C2x, C2y)
        print("Decrypted key:", ecc.decrypt(C1x, C1y, C2x, C2y))
    return C1x, C1y, C2x, C2y


class EmailWorker(QObject):
    finished = pyqtSignal()  # Signal to indicate the work is done

    def __init__(self, message_details, elgamal_decrypter, rabin_signer, user, toLineEdit):
        super().__init__()
        self.message = message_details
        self.elgamal_decrypter = elgamal_decrypter
        self.rabin_signer = rabin_signer
        self.user = user
        self.toLineEdit = toLineEdit

    def send_email(self):
        json_message = json.dumps(self.message)

        blowfish.init()
        elgamal_encrypted_blowfish_key = encrypt_key(self.elgamal_decrypter)

        digitally_signed_elgamal_key = digital_signature(self.rabin_signer,
                                                       str(elgamal_encrypted_blowfish_key[0]) + ";"
                                                     + str(elgamal_encrypted_blowfish_key[1]) + ";"
                                                     + str(elgamal_encrypted_blowfish_key[2]) + ";"
                                                     + str(elgamal_encrypted_blowfish_key[3]))

        encrypted_message = blowfish.encrypt_text_with_blowfish(json_message)

        digitally_signed_blowfish_message = digital_signature(self.rabin_signer, encrypted_message)

        header = {
            "from": self.user,
            "to": self.toLineEdit.text(),
            "elgamal_encrypted_blowfish_key": elgamal_encrypted_blowfish_key,
            "msg": encrypted_message,
            "dig_sign_elgamal_key": digitally_signed_elgamal_key,
            "dig_sign_blowfish_message": digitally_signed_blowfish_message
        }

        email_id = uuid.uuid4()
        email_file_path = f'resources/emails/{self.user}/email{str(email_id)[-4:]}.json'
        save_message_to_json(header, email_file_path)
        print("Email sent")

        # Simulate email sending logic
        print(f"Sending email to: {self.toLineEdit.text()}")

        # Emit the finished signal when done
        self.finished.emit()


class EmailSenderGUI(QWidget):
    def __init__(self):
        super().__init__()
        # Encryption data
        self.rabin_public_key = None
        self.rabin_signed_elgamal_key = None
        self.rabin_signer = SignatureScheme()
        self.rabin_verifier = SignatureScheme()
        self.elgamal_encrypter = None
        ###

        self.elgamal_decrypter = ElgamalEncryption()

        # Decryption data
        self.rabin_verification_public_key = None
        self.decryption_public_elgamal_key = None

        # Threads
        self.credentials_thread = QThread()
        self.email_thread = QThread()
        # self.setupWorkerAndThread()

        # Utility
        self.user = sys.argv[1] if len(sys.argv) > 1 else "default_user"
        self.initUI()
        self.load_emails()
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)

    # def setupWorkerAndThread(self):
    #     self.email_thread.started.connect(self.triggerSendMessage)
    #     self.credentials_thread.started.connect(self.send_credentials)

    # def triggerSendMessage(self):
    #     message = {
    #         "subject": self.subjectLineEdit.text(),
    #         "message": self.bodyTextEdit.toPlainText()
    #     }
    #
    #     json_message = json.dumps(message)
    #
    #     blowfish.init()
    #     self.load_other_user_credentials()
    #     elgamal_encrypted_blowfish_key = encrypt_key(self.elgamal_decrypter)
    #
    #     digitally_signed_elgamal_key = digital_signature(self.rabin_signer,
    #                                                    str(elgamal_encrypted_blowfish_key[0]) + ";"
    #                                                  + str(elgamal_encrypted_blowfish_key[1]) + ";"
    #                                                  + str(elgamal_encrypted_blowfish_key[2]) + ";"
    #                                                  + str(elgamal_encrypted_blowfish_key[3]))
    #
    #     encrypted_message = blowfish.encrypt_text_with_blowfish(json_message)
    #
    #     digitally_signed_blowfish_message = digital_signature(self.rabin_signer, encrypted_message)
    #
    #     header = {
    #         "from": self.user,
    #         "to": self.toLineEdit.text(),
    #         "elgamal_encrypted_blowfish_key": elgamal_encrypted_blowfish_key,
    #         "msg": encrypted_message,
    #         "dig_sign_elgamal_key": digitally_signed_elgamal_key,
    #         "dig_sign_blowfish_message": digitally_signed_blowfish_message
    #     }
    #
    #     email_id = uuid.uuid4()
    #     email_file_path = f'resources/emails/{self.user}/email{str(email_id)[-4:]}.json'
    #     save_message_to_json(header, email_file_path)
    #     print("Email sent")

    def send_credentials(self):
        credentials = {
            "from": self.user,
            "rabin_public_key": self.rabin_public_key,
            "public_elgamal_key": self.elgamal_decrypter.get_elgamal_key()
        }
        credentials_file_path = f'resources/creds/{self.user}/credentials.json'
        save_message_to_json(credentials, credentials_file_path)

    def initUI(self):
        # Set the window properties
        self.setWindowTitle(self.user)
        self.setGeometry(100, 100, 600, 500)

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
        self.sendButton.setFixedWidth(150)
        self.sendButton.setFixedHeight(40)
        # Add stretch to both sides of the button to center it
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.sendButton)
        buttonLayout.addStretch()

        # encryption setup
        if env.debug:
            print(self.rabin_signed_elgamal_key)

        self.rabin_public_key = self.rabin_signer.get_public_key()

        if not self.credentials_thread.isRunning():
            self.credentials_thread.start()

        # Add widgets and layouts to the main layout
        mainLayout.addWidget(self.toLabel)
        mainLayout.addWidget(self.toLineEdit)
        mainLayout.addWidget(self.subjectLabel)
        mainLayout.addWidget(self.subjectLineEdit)
        mainLayout.addWidget(self.bodyLabel)
        mainLayout.addWidget(self.bodyTextEdit)
        mainLayout.addLayout(buttonLayout)

        self.emailListWidget = QListWidget()

        # Adjust the layout to include the email list
        emailListLayout = QVBoxLayout()
        emailListLayout.addWidget(QLabel("Email list:"))
        emailListLayout.addWidget(self.emailListWidget)
        self.emailListWidget.itemClicked.connect(self.display_email_details)

        # Create and add the refresh button
        self.refreshButton = QPushButton('Refresh')
        self.refreshButton.clicked.connect(self.load_emails)  # Connect the button click to load_emails
        self.refreshButton.setFixedWidth(150)
        self.refreshButton.setFixedHeight(40)
        emailListLayout.addWidget(self.refreshButton)  # Add the refresh button to the layout
        emailListLayout.addStretch()

        # Adjust the main layout to include the new email list layout
        mainLayout.addLayout(emailListLayout)

        # Set the layout on the application's window
        self.setLayout(mainLayout)

    def load_emails(self):
        print("\nloading emails: \n")

        self.load_other_user_credentials()
        base_path = 'resources/emails/'
        self.emailListWidget.clear()  # Clear existing items before loading new ones

        # Check if the base path exists
        if not os.path.exists(base_path):
            print("Email directory does not exist.")
            return

        for root, dirs, files in os.walk(base_path):
            for file in files:
                if file.endswith('.json'):  # Ensure we're only reading JSON files
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r') as f:
                            email = json.load(f)
                            # Check if the 'to' field matches self.user



                            if email.get('to') == self.user:

                                if 'decrypted' in email:
                                    print("found decrypted email")
                                    email_entry = f"(secure) {email['subject']} - from {email['from']}"
                                    list_item = QListWidgetItem(email_entry)
                                    list_item.setData(Qt.ItemDataRole.UserRole, file_path)  # Store the file path
                                    self.emailListWidget.addItem(list_item)
                                    continue

                                blowfish_key = email['elgamal_encrypted_blowfish_key']
                                decrypted_blowfish_key = self.elgamal_decrypter.decrypt(int(blowfish_key[0]),
                                                                                        int(blowfish_key[1]),
                                                                                        int(blowfish_key[2]),
                                                                                        int(blowfish_key[3]))

                                print(email.get('elgamal_encrypted_blowfish_key'))
                                print("Decrypted key from loading emails: " + str(decrypted_blowfish_key))

                                if self.rabin_verify(email['dig_sign_elgamal_key'],
                                                     str(blowfish_key[0]) + ";" +
                                                     str(blowfish_key[1]) + ";" +
                                                     str(blowfish_key[2]) + ";" +
                                                     str(blowfish_key[3])):

                                    blowfish.init(blowfish.int_to_key(decrypted_blowfish_key))
                                    decrypted_message = blowfish.decrypt_text_with_blowfish(email['msg'])
                                    decrypted_json_message = json.loads(decrypted_message)
                                    email_entry = f"(secure) {decrypted_json_message['subject']} - from {email['from']}"

                                    new_contents = {
                                        'decrypted': True,
                                        "to": email['to'],
                                        'from': email['from'],
                                        'subject': decrypted_json_message['subject'],
                                        'message': decrypted_json_message['message']
                                    }

                                    try:
                                        with open(file_path, 'w') as new_file:
                                            json.dump(new_contents, new_file, indent=4)  # 'indent' for pretty-printing
                                        print("New file written successfully in JSON format.")
                                    except Exception as e:
                                        print(f"Error writing file in JSON format: {e}")

                                else:
                                    # if env.debug:
                                    #     print("invalid signature")
                                    # email_entry = f"(Insecure) {email.get('subject', 'No Subject')} - from {email.get('from', 'Unknown')}"
                                    continue

                                list_item = QListWidgetItem(email_entry)
                                list_item.setData(Qt.ItemDataRole.UserRole, file_path)  # Store the file path
                                self.emailListWidget.addItem(list_item)
                            f.close()
                    except Exception as e:
                        print(f"Error reading {file_path}: {e}")
                        traceback.print_exc()

        if self.emailListWidget.count() == 0:
            print(f"No emails found for user {self.user}.")

    def display_email_details(self, item):
        print("\ndisplaying emails: \n")
        file_path = item.data(Qt.ItemDataRole.UserRole)
        try:
            with open(file_path, 'r') as file:
                email = json.load(file)

                # Display the email's details
                self.toLineEdit.setText(email.get('from', ''))
                self.subjectLineEdit.setText(email.get('subject', ''))
                self.bodyTextEdit.setPlainText(email.get('message', ''))
                file.close()

        except Exception as e:
            print(f"Error loading email from {file_path}: {e}")
            traceback.print_exc()

    def string_to_int_representation(self, input_string):
        return int(''.join(f"{ord(c):03}" for c in input_string))

    # def send_email(self):
    #     print("Starting email sending process...")
    #     if not self.email_thread.isRunning():
    #         self.email_thread.start()
    def send_email(self):
        print("Starting email sending process...")
        self.load_other_user_credentials()

        # Collect the details needed for the email
        message_details = {
            "subject": self.subjectLineEdit.text(),
            "message": self.bodyTextEdit.toPlainText()
        }

        # Create a new worker each time
        self.worker = EmailWorker(message_details, self.elgamal_decrypter, self.rabin_signer, self.user,
                                  self.toLineEdit)

        # Create a new thread each time
        self.email_thread = QThread()

        # Move the worker to the thread
        self.worker.moveToThread(self.email_thread)

        # Connect signals
        self.email_thread.started.connect(self.worker.send_email)
        self.worker.finished.connect(self.email_thread.quit)  # Thread will quit when work is done
        self.worker.finished.connect(self.worker.deleteLater)  # Clean up the worker after
        self.email_thread.finished.connect(self.email_thread.deleteLater)  # Clean up the thread after

        # Start the thread
        self.email_thread.start()

    def load_other_user_credentials(self):
        # Determine the other user based on the current user
        if self.user.lower() == "alice":
            credentials_path = "resources/creds/bob/credentials.json"
        elif self.user.lower() == "bob":
            credentials_path = "resources/creds/alice/credentials.json"
        else:
            print("Invalid user")
            return

        # Load the credentials from the determined path
        try:
            with open(credentials_path, 'r') as file:
                credentials = json.load(file)
                # Assigning the credentials to the class attributes
                self.rabin_verification_public_key = credentials["rabin_public_key"]
                self.elgamal_encrypter = ElgamalEncryption(n=credentials["public_elgamal_key"][4],
                                                           base_point_x=credentials["public_elgamal_key"][0],
                                                           base_point_y=credentials["public_elgamal_key"][1],
                                                           end_point_x=credentials["public_elgamal_key"][2],
                                                           end_point_y=credentials["public_elgamal_key"][3])

        except FileNotFoundError:
            print(f"Credentials file not found: {credentials_path}")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from {credentials_path}: {e}")

    def rabin_verify(self, signature, message):
        return self.rabin_verifier.verify(signature, message)


def clean_email_resources():
    directory = "resources/emails"
    try:
        shutil.rmtree(directory)  # Remove the directory and all its contents
        os.makedirs(directory)  # Recreate the directory if you need it empty upon the next application start
        print("Email resources cleaned up successfully.")
    except Exception as e:
        print(f"Error cleaning up email resources: {e}")


def main():
    app = QApplication(sys.argv)
    # app.aboutToQuit.connect(clean_email_resources)
    # Simulate some load time
    # app.processEvents()
    window = EmailSenderGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
