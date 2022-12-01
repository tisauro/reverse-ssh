import json

import pytest
import websockets


@pytest.mark.asyncio
async def test_init():
    async with websockets.connect(uri='localhost:8001') as ws:
        message = json.dumps({
            "type": "init",
            "command": "hello world"
        })
        res = await ws.send(message)
        print(res)

