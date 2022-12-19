import asyncio
import json
import websockets
from typing import Union, Iterable, AsyncIterable
from websockets.typing import Data
from src.utils.messages import SSHClientConnect
from src.utils import const
from asyncssh import SSHCompletedProcess


class WsSshClient:
    def __init__(self, url: str, port: int, my_uuid: str) -> None:
        self.url: str = url
        self.port: int = port
        self.ws = None
        self.uuid: str = my_uuid

    def create_json_response(self, result):
        message = json.dumps({
            "type": "reverse-ssh",
            "action": "command_result",
            "device_id": self.uuid,
            "status": "ok",
            "std_out": result.stdout,
            "std_err": result.stderr,
        })
        return message

    async def connect(self) -> bool:
        self.ws = await websockets.connect(uri=f'{self.url}:{self.port}')

        message = SSHClientConnect(self.uuid, status=const.REQUEST_OPEN)

        await self.ws.send(str(message))
        try:
            # receive confirmation message within 3 seconds.
            response = await asyncio.wait_for(self.ws.recv(), timeout=3)
            rsp_msg = SSHClientConnect.from_json(response)
            if rsp_msg == ~message:
                print("connection open")
            else:
                print("close this connection")

        except TimeoutError:
            print('timeout')
            self.ws.close(code=1001, reason='timeout occurred')

        return True

    async def close(self) -> None:
        await self.ws.close(code=1000)

    async def send(self, message: Union[Data, Iterable[Data], AsyncIterable[Data]]) -> None:
        await self.ws.send(message=message)

    async def send_comm_response(self, result: SSHCompletedProcess):
        msg = self.create_json_response(result)
        pass
