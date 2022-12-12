import asyncio
import json
import websockets
from typing import Union, Iterable, AsyncIterable
from websockets.typing import Data
from src.utils.messages import SSHClientConnect


class WsSshClient:
    def __init__(self, url: str, port: int) -> None:
        self.url = url
        self.port = port
        self.ws = None

    async def connect(self) -> bool:
        self.ws = await websockets.connect(uri=f'{self.url}:{self.port}')
        # message = json.dumps({
        #     "type": "reverse-ssh",
        #     "action": "open_connection",
        #     "device_id": "my_unique_uuid",
        #     "status": "new"
        # })
        message = str(SSHClientConnect("my_unique_uuid", status="new"))
        await self.ws.send(message)
        try:
            # receive confirmation message within 3 seconds.
            message1 = await asyncio.wait_for(self.ws.recv(), timeout=3)
            event = json.loads(message1)
            print(message1)
            assert event.get('status') == 'done'

        except TimeoutError:
            print('timeout')
            self.ws.close(code=1001, reason='timeout occurred')

        return True

    async def close(self) -> None:
        await self.ws.close(code=1000)

    async def send(self, message: Union[Data, Iterable[Data], AsyncIterable[Data]]) -> None:
        await self.ws.send(message=message)
