import json

import pytest
import websockets


@pytest.mark.asyncio
async def test_open_connection():
    async with websockets.connect(uri='ws://localhost:8001') as ws:
        message = json.dumps({
            "type": "open_connection",
            "device_id": "my_unique_uuid"
        })
        await ws.send(message)


