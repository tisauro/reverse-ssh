import websockets
import asyncio
from src.utils import const
from src.utils.messages import WebClientConnect, WebClientMessage, WebClientHistMessage


class WsWebClient:
    def __init__(self, url: str, port: int, device_uuid: str):
        self.url: str = url
        self.port: int = port
        self.device_uuid: str = device_uuid
        self.ws = None

    async def connect(self):
        self.ws = await websockets.connect(uri=f'{self.url}:{self.port}')

        message = WebClientConnect(self.device_uuid, status=const.REQUEST_OPEN)

        await self.ws.send(str(message))
        try:
            # receive confirmation message within 3 seconds.
            response = await asyncio.wait_for(self.ws.recv(), timeout=3)
            rsp_msg = WebClientConnect.from_json(response)
            if rsp_msg == ~message:
                print("connection open")
            else:
                print("close this connection")
                self.ws.close(code=1001, reason='Connection refused')

        except TimeoutError:
            print('timeout')
            self.ws.close(code=1001, reason='timeout occurred')

        return True

    async def read_input(self) -> None:
        try:
            msg = await self.ws.recv()

            message = WebClientHistMessage.from_json(msg)
            print(message)
        except Exception as ex:
            print(ex)
            message = ex
        return message.message

    async def send_command(self, message: str):
        msg = WebClientMessage(self.device_uuid, message)
        await self.ws.send(str(msg))

    async def close(self) -> None:
        await self.ws.close(code=1000)

    async def await_closed(self):
        await self.ws.wait_closed()

