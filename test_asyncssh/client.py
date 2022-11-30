import asyncio
import asyncssh
import sys


async def run_client():
    async with asyncssh.connect(host='172.17.0.2',
                                port=8022, username='guest', password='', known_hosts=None) as conn:
        # result = await conn.run('echo "Hello!"', check=True)
        # print(result.stdout, end='')
        async with conn.create_process('bc') as process:
            for op in ['2+2', '1*2*3*4', '2^32']:
                process.stdin.write(op + '\n')
                result = await process.stdout.readline()
                print(op, '=', result, end='')




# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    try:
        asyncio.run(run_client())
    except (OSError, asyncssh.Error) as exc:
        sys.exit('SSH connection failed: ' + str(exc))
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
