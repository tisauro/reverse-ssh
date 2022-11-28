import asyncio
import asyncssh
import sys
from asyncio.subprocess import PIPE


async def handle_request(process: asyncssh.SSHServerProcess) -> None:
    """Run a command on the client, piping I/O over an SSH session"""

    assert process.command is not None

    local_proc = await asyncio.create_subprocess_shell(
        process.command, stdin=PIPE, stdout=PIPE, stderr=PIPE)

    await process.redirect(stdin=local_proc.stdin, stdout=local_proc.stdout,
                           stderr=local_proc.stderr)

    process.exit(await local_proc.wait())
    await process.wait_closed()


async def run_reverse_client() -> None:
    """Make an outbound connection and then become an SSH server on it"""

    conn = await asyncssh.connect_reverse(
        host='localhost', port=8022, server_host_keys=None, #['client_host_key'],
        authorized_client_keys=None, #'trusted_server_keys',
        process_factory=handle_request, encoding=None)

    await conn.wait_closed()

if __name__ == '__main__':
    try:
        asyncio.get_event_loop().run_until_complete(run_reverse_client())
    except (OSError, asyncssh.Error) as exc:
        sys.exit('Reverse SSH connection failed: ' + str(exc))
