import asyncio
import json

import asyncssh
import functools
import sys
import os
from typing import Optional
from src.ws_clients.ws_ssh_client import WsSshClient

IP_ADDRESS = os.environ.get('IP_ADDRESS')
USERNAME = os.environ.get('USERNAME', 'guest')
PASSWORD = os.environ.get('PASSWORD', '')
PORT = os.environ.get('PORT', 8022)


class MySSHClientSession(asyncssh.SSHClientSession):
    def __init__(self, ws_client: WsSshClient) :
        self.ws = ws_client

    def data_received(self, data: str, datatype: asyncssh.DataType) -> None:
        # print(data, end='')
        message = json.dumps({
            "type": "reverse-ssh",
            "action": "command_result",
            "device_id": "my_unique_uuid",
            "status": "ok",
            "std_out": data,
            "std_err": '',
        })
        asyncio.get_running_loop().create_task(self.ws.send(message))

    def connection_lost(self, exc: Optional[Exception]) -> None:
        if exc:
            print('SSH session error: ' + str(exc), file=sys.stderr)


class MySSHClient(asyncssh.SSHClient):

    def __init__(self, ws_client: WsSshClient):
        self.ws = ws_client

    def connection_made(self, conn: asyncssh.SSHClientConnection) -> None:
        message = json.dumps({
            "type": "reverse-ssh",
            "action": "command_result",
            "device_id": "my_unique_uuid",
            "status": "ok",
            "std_out": 'Connection made to %s.' % conn.get_extra_info('peername')[0],
            "std_err": '',
        })
        asyncio.get_running_loop().create_task(self.ws.send(message))

    def auth_completed(self) -> None:
        # asyncio.create_task(self.ws.send('Authentication successful.'))
        pass


def create_json_response(result):
    message = json.dumps({
        "type": "reverse-ssh",
        "action": "command_result",
        "device_id": "my_unique_uuid",
        "status": "ok",
        "std_out": result.stdout,
        "std_err": result.stderr,
    })
    return message


async def run_client():
    ws_client = WsSshClient(url="ws://localhost", port=8001)
    await ws_client.connect()
    conn, client = await asyncssh.create_connection(functools.partial(MySSHClient, ws_client), host=IP_ADDRESS,
                                                    port=22, username=USERNAME, password=PASSWORD, known_hosts=None)

    async with conn:
        chan, session = await conn.create_session(functools.partial(MySSHClientSession, ws_client))
        result = await conn.run('pwd')
        await ws_client.send(create_json_response(result))
        result = await conn.run('ls -la')
        await ws_client.send(create_json_response(result))
        result = await conn.run('cat test_')
        await ws_client.send(create_json_response(result))
        result = await conn.run('\t \t')
        await ws_client.send(create_json_response(result))
        # chan.close()
        await chan.wait_closed()

    pass

    # async with asyncssh.connect(host=IP_ADDRESS,
    #                             port=22, username=USERNAME, password=PASSWORD, known_hosts=None) as conn:
    #     result = await conn.run('echo "Hello!"', check=True)
    #     print(result.stdout, end='')
    #     result = await conn.run('ls -la', check=True)
    #     print(result.stdout, end='')
    # async with conn.create_process('bc') as process:
    #     for op in ['2+2', '1*2*3*4', '2^32']:
    #         process.stdin.write(op + '\n')
    #         result = await process.stdout.readline()
    #         print(op, '=', result, end='')


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    try:
        asyncio.run(run_client())
    except (OSError, asyncssh.Error) as exc:
        sys.exit('SSH connection failed: ' + str(exc))
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
