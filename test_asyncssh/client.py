import asyncio
import asyncssh
import sys
import os
from typing import Optional

IP_ADDRESS='82.70.57.134'

USERNAME = os.environ.get('USERNAME', 'guest')
PASSWORD = os.environ.get('PASSWORD', '')
PORT= os.environ.get('PORT', 8022)


class MySSHClientSession(asyncssh.SSHClientSession):
    def data_received(self, data: str, datatype: asyncssh.DataType) -> None:
        print(data, end='')

    def connection_lost(self, exc: Optional[Exception]) -> None:
        if exc:
            print('SSH session error: ' + str(exc), file=sys.stderr)

class MySSHClient(asyncssh.SSHClient):
    def connection_made(self, conn: asyncssh.SSHClientConnection) -> None:
        print('Connection made to %s.' % conn.get_extra_info('peername')[0])

    def auth_completed(self) -> None:
        print('Authentication successful.')

async def run_client():
    conn, client = await asyncssh.create_connection(MySSHClient, host=IP_ADDRESS,
                                port=22, username=USERNAME, password=PASSWORD, known_hosts=None)

    async with conn:
        chan, session = await conn.create_session(MySSHClientSession)
        result = await conn.run('pwd')
        print(result.stdout, end='')
        result = await conn.run('ls -la')
        print(result.stdout, end='')
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
