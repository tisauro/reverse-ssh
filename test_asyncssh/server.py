# To run this program, the file ``ssh_host_key`` must exist with an SSH
# private key in it to use as a server host key. An SSH host certificate
# can optionally be provided in the file ``ssh_host_key-cert.pub``.

import crypt
import asyncio
import asyncssh
import os
import sys
from typing import Optional

passwords = {'guest': '',  # guest account with no password
             'user123': 'qV2iEadIGV2rw'  # password of 'secretpw'
             }

this_dir = os.path.dirname(os.path.abspath(__file__))
print(this_dir)

async def handle_client(process: asyncssh.SSHServerProcess) -> None:
    # process.stdout.write('Welcome to my SSH server, %s!\n' %
    #                      process.get_extra_info('username'))
    # process.exit(0)
    process.stdout.write('Enter numbers one per line, or EOF when done:\n')

    total = 0

    try:
        async for line in process.stdin:
            line = line.rstrip('\n')
            if line:
                try:
                    total += int(line)
                except ValueError:
                    process.stderr.write('Invalid number: %s\n' % line)
    except asyncssh.BreakReceived:
        pass

    process.stdout.write('Total = %s\n' % total)
    process.exit(0)

class MySSHServer(asyncssh.SSHServer):
    def connection_made(self, conn: asyncssh.SSHServerConnection) -> None:
        print('SSH connection received from %s.' %
              conn.get_extra_info('peername')[0])

    def connection_lost(self, exc: Optional[Exception]) -> None:
        if exc:
            print('SSH connection error: ' + str(exc), file=sys.stderr)
        else:
            print('SSH connection closed.')

    def begin_auth(self, username: str) -> bool:
        # If the user's password is the empty string, no auth is required
        print("SSH password check")
        return passwords.get(username) != ''

    def password_auth_supported(self) -> bool:
        print("in here")
        return True

    def validate_password(self, username: str, password: str) -> bool:
        print("Validate password")
        pw = passwords.get(username, '*')
        return crypt.crypt(password, pw) == pw


async def start_server() -> None:
    await asyncssh.create_server(MySSHServer, '', 8022,
                                 server_host_keys=[os.path.join(this_dir, 'ssh_host_key')],
                                 process_factory=handle_client)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(start_server())
    except (OSError, asyncssh.Error) as exc:
        sys.exit('Error starting server: ' + str(exc))

    loop.run_forever()