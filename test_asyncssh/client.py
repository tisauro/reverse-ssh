import asyncio
import asyncssh
import sys


async def run_client():
    async with asyncssh.connect(host='localhost',
                                port=8022, username='guest', known_hosts=None) as conn:
        result = await conn.run('echo "Hello!"', check=True)
        print(result.stdout, end='')




# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    try:
        asyncio.run(run_client())
    except (OSError, asyncssh.Error) as exc:
        sys.exit('SSH connection failed: ' + str(exc))
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
