import asyncio
import json
import logging
import signal
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
        except Exception as e:
            print(e)
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


class GracefulExit(SystemExit):
    code = 1


def raise_graceful_exit(*args):
    loop = asyncio.get_running_loop()
    loop.stop()
    print("Gracefully shutdown")
    raise GracefulExit()


async def main():
    # Set the stop condition when receiving SIGTERM.

    signal.signal(signal.SIGINT, raise_graceful_exit)
    signal.signal(signal.SIGTERM, raise_graceful_exit)

    async with websockets.serve(handler, "", 8001):
        await asyncio.Future()  # run forever


        # await stop


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except GracefulExit:
        pass