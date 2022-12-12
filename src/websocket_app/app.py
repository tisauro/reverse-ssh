import asyncio
import json
import logging
import signal
import websockets
from websockets.server import WebSocketServerProtocol
from websockets.exceptions import ConnectionClosedError, ConnectionClosed, ConnectionClosedOK
from typing import Dict
from src.utils.ssh_connection import SSHConnection

# logging.basicConfig(
#     level=logging.DEBUG
# )


OPEN_CONNECTIONS: Dict[str, SSHConnection] = {}


async def connect_client(websocket: WebSocketServerProtocol, device_id: str) -> None:
    """
    Web client connection handler
    :param websocket: web client socket
    :param device_id: device_id we want to connect to.
    :return: None
    """
    ssh_connection = OPEN_CONNECTIONS.get(device_id, None)
    if ssh_connection:
        ssh_connection.clients.add(websocket)
        message = json.dumps({
            "type": "web_client",
            "action": "connect_client",
            "device_id": device_id,
            "status": "connected",
            "output": "connection not found"
        })
    else:
        message = json.dumps({
            "type": "web_client",
            "action": "connect_client",
            "device_id": device_id,
            "status": "error",
            "output": "connection not found"
        })
    await websocket.send(message)


async def open_connection_event(websocket: WebSocketServerProtocol, device_id: str) -> None:
    """
    Connection from one of the data loggers on site
    :param websocket: server connection
    :param device_id: unique identifier of the device, used to create a websocket room
    :return: None
    """
    ssh_connection = SSHConnection(websocket)
    OPEN_CONNECTIONS[device_id] = ssh_connection
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
                if event.get('action') == 'command_result':
                    '''
                    command output received from the ssh server
                    in response to an open connection or
                    an execute command previously sent from 
                    a web client.
                    '''
                    line = event.get("std_out").split('\n')
                    # Todo: do this properly, should loop through the list and

                    # broadcast all messages.
                    message = json.dumps({
                        "message": line
                    })
                    websockets.broadcast(ssh_connection.clients, message)

                    ssh_connection.buffer.add_to_history(line)

                elif event.get('action') == 'command_execute':
                    line = ""
                    ssh_connection.buffer.add_to_history(line)
                    await websocket.send(line)
                else:
                    pass
                #ssh_connection.buffer.print_history()

        except Exception as e:
            print(e)
    finally:
        del OPEN_CONNECTIONS[device_id]
    pass


async def handler(websocket: WebSocketServerProtocol) -> None:
    # Receive and parse the "init" event from the UI.
    try:
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
        elif event.get('action') == "connect_client":
            '''
            action called by webclients who want to send commands
            to a remote device
            '''
            await connect_client(websocket)
    except ConnectionClosedOK:
        print("Connection OK")

    except ConnectionClosedError:
        print("Connection Error")
    except Exception as e:
        print(f"General Exception {e}")


class GracefulExit(SystemExit):
    code = 1


def raise_graceful_exit(*args):
    loop = asyncio.get_running_loop()
    loop.stop()
    print("Gracefully shutdown")
    raise GracefulExit()


async def ws_app_main():
    # Set the stop condition when receiving SIGTERM.
    print("starting websocket app!")

    signal.signal(signal.SIGINT, raise_graceful_exit)
    signal.signal(signal.SIGTERM, raise_graceful_exit)

    async with websockets.serve(handler, "", 8001):
        await asyncio.Future()  # run forever

        # await stop
