import asyncio
import json
import logging
import websockets
from websockets.server import WebSocketServerProtocol
from typing import Dict

# logging.basicConfig(
#     level=logging.DEBUG
# )

OPEN_CONNECTIONS: Dict[str, set] = {}


async def open_connection_event(websocket: WebSocketServerProtocol, device_id: str) -> None:
    pass


async def handler(websocket: WebSocketServerProtocol) -> None:
    # Receive and parse the "init" event from the UI.
    message = await websocket.recv()
    event = json.loads(message)
    assert event["type"] == "open_connection"
    print(f'message received {str(message)}')
    connected = {websocket}
    print(type(connected))
    if "open_connection" in event:
        await open_connection_event(websocket, event['device_id'])

    pass


async def main():
    async with websockets.serve(handler, "", 8001):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
