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
    connected = {websocket}
    OPEN_CONNECTIONS[device_id] = connected
    try:
        message = json.dumps({
            "type": "reverse-ssh",
            "action": "open_connection",
            "device_id": "my_unique_uuid",
            "status": "done"
        })
        await websocket.send(message)
        async for message in websocket:
            # Parse a "play" event from the UI.
            event = json.loads(message)
            print(event)
    finally:
        del OPEN_CONNECTIONS[device_id]
    pass


async def handler(websocket: WebSocketServerProtocol) -> None:
    # Receive and parse the "init" event from the UI.
    message = await websocket.recv()
    event = json.loads(message)
    # Todo: remove assert add if with logging.
    assert event["type"] == "reverse-ssh"
    print(f'message received {str(message)}')
    # connected = {websocket}
    # print(type(connected))
    if event.get('action') == "open_connection":
        '''
        action called only by the reverse-ssh server when 
        instigated to open a connection
        '''
        await open_connection_event(websocket, event['device_id'])

    pass


async def main():
    async with websockets.serve(handler, "", 8001):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
