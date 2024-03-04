# cryptology-encrypted-emailer
A program to send encrypted emails using cobra cypher


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

# To-do:
* Add key swapping between two clients.
  * For example when a client connects it sends everyone its public key (after EC-Elgamal & rabin)
* Add addressing clients using e-mail address to emulate e-mail sending
* Add Received messages window in UI_with_websocket_client.py 