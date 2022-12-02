import asyncio
import json
import pytest
import websockets

from src.ws_clients.ws_ssh_client import WsSshClient
@pytest.mark.asyncio
async def test_open_connection():
    async with websockets.connect(uri='ws://localhost:8001') as ws:
        message = json.dumps({
            "type": "reverse-ssh",
            "action": "open_connection",
            "device_id": "my_unique_uuid",
            "status": "new"
        })
        await ws.send(message)
        try:
            # receive confirmation message within 3 seconds.
            message1 = await asyncio.wait_for(ws.recv(), timeout=3)
            event = json.loads(message1)
            print(message1)
            assert event.get('status') == 'done'
        except TimeoutError:
            print('timeout')
            ws.close(code=1001, reason='timeout occurred')


@pytest.mark.asyncio
async def test_client_connection():
    client = WsSshClient(url='ws://localhost', port=8001)
    res = await client.connect()
    assert res
    await client.close()