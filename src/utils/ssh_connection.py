from websockets.server import WebSocketServerProtocol
from typing import Dict, NamedTuple, Set, List
from src.utils.ssh_buffer import SSHBuffer


class SSHConnection(NamedTuple):
    device: WebSocketServerProtocol
    clients: Set[WebSocketServerProtocol] = set()
    buffer: SSHBuffer = SSHBuffer()