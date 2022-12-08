import json

import pytest
from unittest.mock import AsyncMock
from src.websocket_app import app
from src.websocket_app.app import handler, open_connection_event
from websockets.exceptions import ConnectionClosedError
from websockets.frames import Close


@pytest.mark.asyncio
async def test_handler_connection_close_error():
    mock_obj = AsyncMock()
    mock_obj.recv.side_effect = ConnectionClosedError(rcvd=Close(code=1001, reason="dummy error"),
                                                      sent=Close(code=1001, reason="another reason"))
    with pytest.raises(ConnectionClosedError) as E:
        await handler(mock_obj)
    print(E)


@pytest.mark.asyncio
async def test_handler_unknown_message():
    mock_websocket = AsyncMock()
    mock_websocket.recv.return_value = json.dumps({
        "wrong": "message"
    })

    await handler(mock_websocket)


@pytest.mark.asyncio
async def test_handler_open_connection_event():
    mock_websocket = AsyncMock()
    mock_websocket.recv.return_value = json.dumps({
        "type": "reverse-ssh",
        "action": "open_connection",
        "device_id": "my_unique_uuid",
        "status": "new"
    })

    app.open_connection_event = AsyncMock()
    await handler(mock_websocket)
    app.open_connection_event.assert_called_once()
