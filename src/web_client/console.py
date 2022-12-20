import asyncio
import aconsole
from src.web_client.ws_web_client import WsWebClient
from dataclasses import dataclass


# WsWebClientConnectionDetails = namedtuple("WsWebClientConnectionDetails",
#                                         ['ws_url',
#                                          'ws_port',
#                                          'device_uui'])

# or dataclass makes it easier to specify typing
@dataclass
class WsWebClientConnectionDetails:
    ws_url: str
    ws_port: int
    device_uui: str  # device to connect to


class WebClient:
    def __init__(self, url, port, my_console):
        self.url = url
        self.port = port
        self.console = my_console
        self.cwait = asyncio.Future()
        self.web_client: [WsWebClient, None] = None
        self.device_uuid = None
        # creates the task but it doesn't run until loop is started
        self.loop = asyncio.get_event_loop()
        self.loop.create_task(self.connector())

    async def wait_close(self):
        await self.cwait

    async def connector(self):
        try:
            self.device_uuid = await self.console.input("Device_uuid:")
            self.web_client = WsWebClient(self.url, self.port, self.device_uuid)
            await self.web_client.connect()
            self.loop.create_task(self.send_input())
            self.loop.create_task(self.read_input())
            # flow continues after creating a task
            # if exits than task is deleted?
            # hence we wait in here until connection is closed
            await self.web_client.await_closed()
            self.console.cancel_input()
            raise ConnectionAbortedError

        except Exception as ex:
            self.cwait.set_exception(ex)

    async def read_input(self):

        while True:
            try:
                msg = await self.web_client.read_input()
                console.print(f"> {msg}")
            except Exception as ex:
                console.print(f"> {ex}")

    async def send_input(self):
        while True:
            message = await self.console.input("> ")
            if message:
                try:
                    await self.web_client.send_command(message)
                except Exception as ex:
                    print(ex)


if __name__ == '__main__':
    conn_details: WsWebClientConnectionDetails = WsWebClientConnectionDetails(
        ws_url="ws://localhost",
        ws_port=8001,
        device_uui="random_uuid")

    # async def run_web_client(conn_details: WsWebClientConnectionDetails):
    loop = asyncio.get_event_loop()
    console = aconsole.AsyncConsole()
    console.title('Web client ssh')
    console.set_alpha(0.9)
    run_task = console.mainloop()
    WebClient(conn_details.ws_url, conn_details.ws_port, console)
    loop.run_until_complete(run_task)

    # async def echo():
    #     while True:
    #         result = await console.input('echo: ')
    #         console.print('you typed:', result)
    #
    #
    # run_task = console.mainloop()
    # loop.create_task(echo())
    # loop.run_until_complete(run_task)
