import asyncio
import websockets

async def hello():
    uri = "ws://localhost:6789"
    async with websockets.connect(uri) as websocket:
        message = "Hello World!"
        await websocket.send(message)
        print(f"> {message}")

        greeting = await websocket.recv()
        print(f"< {greeting}")

asyncio.get_event_loop().run_until_complete(hello())
