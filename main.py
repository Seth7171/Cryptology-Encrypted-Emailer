import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton, \
    QSplashScreen
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
import time  # Import time for a delay to show the splash screen


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
        # Implementation of email sending functionality
        print("Sending Email...")
        print(f"To: {self.toLineEdit.text()}")
        print(f"Subject: {self.subjectLineEdit.text()}")
        print(f"Body: {self.bodyTextEdit.toPlainText()}")


def main():
    app = QApplication(sys.argv)

    # Assuming you have a splash image called "splash_image.png"
    splash_pix = QPixmap("splash_image.png")
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