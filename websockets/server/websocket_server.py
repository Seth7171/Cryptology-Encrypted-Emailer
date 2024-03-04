import base64
import sys
import asyncio
from PyQt6.QtWidgets import QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget
from PyQt6.QtCore import pyqtSignal, QObject, QThread
import websockets

class LogEmitter(QObject):
    logMessage = pyqtSignal(str)

class ServerThread(QThread):
    def __init__(self, log_emitter):
        super().__init__()
        self.log_emitter = log_emitter

    def run(self):
        asyncio.run(self.start_server())

    async def start_server(self):
        async def echo(websocket, path):
            async for message in websocket:
                print(f"Received message: {message}")
                # The message is text and needs to be Base64 encoded before being sent back
                encoded_message = base64.b64encode(message.encode()).decode()
                await websocket.send(encoded_message)
                log_message = f"Sent encoded message: {encoded_message}"
                self.log_emitter.logMessage.emit(log_message)
                print(log_message)
                await websocket.send(f"Echo: {message}")

        async with websockets.serve(echo, "localhost", 6789):  # Listen on localhost port 6789
            await asyncio.Future()  # Run forever


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WebSocket Server Log")
        self.resize(350, 400)

        self.textEdit = QTextEdit()
        self.textEdit.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addWidget(self.textEdit)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.logEmitter = LogEmitter()
        self.logEmitter.logMessage.connect(self.appendLog)

        # Start the WebSocket server in a separate thread
        self.serverThread = ServerThread(self.logEmitter)
        self.serverThread.start()

    def appendLog(self, message):
        self.textEdit.append(message)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

