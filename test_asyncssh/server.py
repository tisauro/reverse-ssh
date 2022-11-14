# To run this program, the file ``ssh_host_key`` must exist with an SSH
# private key in it to use as a server host key. An SSH host certificate
# can optionally be provided in the file ``ssh_host_key-cert.pub``.

import asyncio, asyncssh, crypt, sys
from typing import Optional

passwords = {'guest': '',  # guest account with no password
             'user123': 'qV2iEadIGV2rw'  # password of 'secretpw'
             }


def handle_client(process: asyncssh.SSHServerProcess) -> None:
    process.stdout.write('Welcome to my SSH server, %s!\n' %
                         process.get_extra_info('username'))
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
        return passwords.get(username) != ''

    def password_auth_supported(self) -> bool:
        return True

    def validate_password(self, username: str, password: str) -> bool:
        pw = passwords.get(username, '*')
        return crypt.crypt(password, pw) == pw


async def start_server() -> None:
    await asyncssh.create_server(MySSHServer, '', 8022,
                                 server_host_keys=['ssh_host_key'],
                                 process_factory=handle_client)


if __name__ == '__main__':

    try:
        asyncio.run(start_server())
    except (OSError, asyncssh.Error) as exc:
        sys.exit('Error starting server: ' + str(exc))
