import asyncio
import signal
import asyncssh
import functools
import sys
from typing import Optional
from src.ws_clients.ws_ssh_client import WsSshClient
from asyncssh import SSHCompletedProcess
from collections import namedtuple
from dataclasses import dataclass


# SSHClientConnectionDetails = namedtuple("SSHClientConnectionDetails",
#                                         ['ssh_ip_address',
#                                          'ssh_username',
#                                          'ssh_password',
#                                          'ssh_port',
#                                          'ws_url',
#                                          'ws_port',
#                                          'device_uui'])

## or dataclass makes it easier to specify typing
@dataclass
class SSHClientConnectionDetails:
    ssh_ip_address: str
    ssh_username: str
    ssh_password: str
    ssh_port: int
    ws_url: str
    ws_port: int
    device_uui: str


class MySSHClientSession(asyncssh.SSHClientSession):
    def __init__(self, ws_client: WsSshClient):
        self.ws = ws_client

    def data_received(self, data: str, datatype: asyncssh.DataType) -> None:
        # print(data, end='')
        result = SSHCompletedProcess()
        result.stdout = data

        asyncio.get_running_loop().create_task(self.ws.send_comm_response(result))

    def connection_lost(self, exc: Optional[Exception]) -> None:
        if exc:
            print('SSH session error: ' + str(exc), file=sys.stderr)


class MySSHClient(asyncssh.SSHClient):

    def __init__(self, ws_client: WsSshClient):
        self.ws = ws_client

    def connection_made(self, conn: asyncssh.SSHClientConnection) -> None:
        result = SSHCompletedProcess()
        result.stdout = 'Connection made to %s.' % conn.get_extra_info('peername')[0]

        asyncio.get_running_loop().create_task(self.ws.send_comm_response(result))

    def auth_completed(self) -> None:
        # asyncio.create_task(self.ws.send('Authentication successful.'))
        pass


async def run_ssh_client(conn_details: SSHClientConnectionDetails):
    signal.signal(signal.SIGINT, raise_graceful_exit)
    signal.signal(signal.SIGTERM, raise_graceful_exit)

    # Websocket connection
    ws_client = WsSshClient(url=conn_details.ws_url,
                            port=conn_details.ws_port,
                            my_uuid=conn_details.device_uui)
    await ws_client.connect()

    # Ssh connection
    conn, client = await asyncssh.create_connection(functools.partial(MySSHClient, ws_client),
                                                    host=conn_details.ssh_ip_address,
                                                    port=int(conn_details.ssh_port),
                                                    username=conn_details.ssh_username,
                                                    password=conn_details.ssh_password,
                                                    known_hosts=None)

    async with conn:
        chan, session = await conn.create_session(functools.partial(MySSHClientSession, ws_client))

        # Process messages received on the connection.

        result = await conn.run('pwd')

        await ws_client.send_comm_response(result)
        result = await conn.run('ls -la')
        await ws_client.send_comm_response(result)
        result = await conn.run('cat test_')
        await ws_client.send_comm_response(result)
        result = await conn.run('\t \t')
        await ws_client.send_comm_response(result)
        # chan.close()
        try:
            await chan.wait_closed()
        except Exception as e:
            print(e)

    pass


class GracefulExit(SystemExit):
    code = 1


def raise_graceful_exit(*args):
    loop = asyncio.get_running_loop()
    loop.stop()
    print("Gracefully shutdown")
    raise GracefulExit()
