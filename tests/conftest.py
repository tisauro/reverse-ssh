import pytest
import websockets

@pytest.fixture
async def ws_client():
    async with websockets.connect(uri='localhost:8081') as ws:
        yield ws
