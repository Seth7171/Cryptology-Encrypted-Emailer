









# OLD advanced server
# import base64
# import sys
# import asyncio
# import json
# from PyQt6.QtWidgets import QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget
# from PyQt6.QtCore import pyqtSignal, QObject, QThread
# import websockets
#
# class LogEmitter(QObject):
#     logMessage = pyqtSignal(str)
#
# class ServerThread(QThread):
#     def __init__(self, log_emitter):
#         super().__init__()
#         self.log_emitter = log_emitter
#
#     def run(self):
#         asyncio.run(self.start_server())
#
#     async def start_server(self):
#         async def echo(websocket, path):
#             print(f"New client connected: {websocket.remote_address}")
#             # TODO: each message is being detected as a new client
#             self.log_emitter.logMessage.emit(f"New client connected: {websocket.remote_address}")
#
#             async for message in websocket:
#                 try:
#                     # Parse the message as JSON
#                     data = json.loads(message)
#                     # Check if the message has a "type" field
#                     if "type" in data:
#                         message_type = data["type"]
#                         print(f"Message type: {message_type}")
#                         self.log_emitter.logMessage.emit(f"Message type: {message_type}")
#                         # Add your logic here based on the message type
#                         if message_type == "creds":
#                             response = {"status": "Received"}
#                             await websocket.send(json.dumps(response))
#
#                         if message_type == "email":
#                             response = {"status": "Received"}
#                             await websocket.send(json.dumps(response))
#                     else:
#                         print("Message does not contain a 'type' field.")
#                         self.log_emitter.logMessage.emit("Message does not contain a 'type' field.")
#                 except json.JSONDecodeError:
#                     print("Received message is not in valid JSON format.")
#                     self.log_emitter.logMessage.emit("Received message is not in valid JSON format.")
#                     response = {"status": "not json"}
#                     await websocket.send(json.dumps(response))
#
#         async with websockets.serve(echo, "localhost", 6789):
#             await asyncio.Future()
#
# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("WebSocket Server Log")
#         self.resize(350, 400)
#
#         self.textEdit = QTextEdit()
#         self.textEdit.setReadOnly(True)
#
#         layout = QVBoxLayout()
#         layout.addWidget(self.textEdit)
#
#         container = QWidget()
#         container.setLayout(layout)
#         self.setCentralWidget(container)
#
#         self.logEmitter = LogEmitter()
#         self.logEmitter.logMessage.connect(self.appendLog)
#
#         # Start the WebSocket server in a separate thread
#         self.serverThread = ServerThread(self.logEmitter)
#         self.serverThread.start()
#
#     def appendLog(self, message):
#         self.textEdit.append(message)
#
# def main():
#     app = QApplication(sys.argv)
#     window = MainWindow()
#     window.show()
#     sys.exit(app.exec())
#
# if __name__ == "__main__":
#     main()
