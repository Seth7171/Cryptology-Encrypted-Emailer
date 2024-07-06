# cryptology-encrypted-emailer
A program to send encrypted emails using Blowfish OFB mode with key encryption ECC-El Gamal and Rabin signature


## Key generation
* key is generated at random every UI_with_websocket_client.py rerun

## Running the program:
* Run the following command: `pip install PyQt6 base64 websockets`
* Run the websockets/server/websocket_server.py file
* Run the UI_with_websocket_client.py file
* Send messages to the server
\
Note: 
  * Currently only the body block is being encrypted and sent.
  * Server receives the encrypted message and does not decrypt it since it should be sent to another client.
