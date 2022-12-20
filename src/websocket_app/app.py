import asyncio
import json
import logging
import signal
import websockets
from websockets.server import WebSocketServerProtocol
from websockets.exceptions import ConnectionClosedError, ConnectionClosed, ConnectionClosedOK
from typing import Dict
from src.utils.ssh_connection import SSHConnection
from src.utils import const
from src.utils.messages import SSHClientConnect, WebClientConnect, WebClientHistMessage

# logging.basicConfig(
#     level=logging.DEBUG
# )


OPEN_CONNECTIONS: Dict[str, SSHConnection] = {}


async def connect_web_client(websocket: WebSocketServerProtocol, device_id: str) -> None:
    """
    Web client connection handler
    :param websocket: web client socket
    :param device_id: device_id we want to connect to.
    :return: None
    """
    ssh_connection = OPEN_CONNECTIONS.get(device_id, None)
    # if remote device ssh channel is open
    if ssh_connection:
        try:
            # Open connection
            ssh_connection.clients.add(websocket)
            message = WebClientConnect(device_id, const.RESPONSE_OPEN)
            await websocket.send(str(message))

            # Send the history to the newly connected client
            for hist in ssh_connection.buffer:
                ## create history message
                msg = WebClientHistMessage(device_id, hist)
                await websocket.send(str(msg))

            print("Web Client connection open")
            # wait for client messages
            async for message in websocket:
                # Parse a "play" event from the UI.
                event = json.loads(message)
                print(f"WebClient sent: {event}")

        finally:
            print("Web client connection terminated")
            ssh_connection.clients.discard(websocket)
    else:
        # ssh connection is not open reject web client connection
        message = WebClientConnect(device_id, const.RESPONSE_REJECTED)
        await websocket.send(str(message))


async def broadcast(clients, message: list) -> None:

    # Todo: do this properly, should loop through the list and

    # broadcast all messages.
    for msg in message:
        message = json.dumps({
            "message": message
        })
        websockets.broadcast(clients, msg)
        print(f"remote: $ {msg}")


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
            message = SSHClientConnect(device_id=device_id, status=const.RESPONSE_OPEN)
            await websocket.send(str(message))

            async for message in websocket:
                # Parse a "play" event from the UI.
                event = json.loads(message)
                if event.get("device_id") != device_id:
                    # Todo: respond with an error message and close this connection
                    print("wrong device id")
                    pass
                if event.get('action') == 'command_result':
                    '''
                    command output received from the ssh server
                    in response to an open connection or
                    an execute command previously sent from 
                    a web client.
                    '''
                    line = event.get("std_out").split('\n')

                    await broadcast(ssh_connection.clients, line)

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

        if event["type"] == const.SSH_MSG_TYPE:
            if event.get('action') == const.ACT_CONNECTION:
                '''
                action called only by the reverse-ssh server when 
                instigated to open a connection
                '''
                await open_connection_event(websocket, event['device_id'])
        elif event.get('type') == const.WEB_MSG_TYPE:
            '''
            action called by webclients who want to send commands
            to a remote device
            '''
            if event.get('action') == const.ACT_CONNECTION:
                await connect_web_client(websocket, event['device_id'])
        else:
            raise NotImplemented

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
