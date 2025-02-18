from typing import Dict, Set

from aiohttp.web_ws import WebSocketResponse


class WebSocketClientSet:
    websocket_set: Set[WebSocketResponse] = set()

    def __init__(self):
        pass

    def add_client(self, client: WebSocketResponse):
        self.websocket_set.add(client)

    def remove_client(self, client: WebSocketResponse):
        self.websocket_set.remove(client)


class WebSocketClientDict:
    websocket_dict: Dict[str, WebSocketResponse] = dict()

    def __init__(self):
        pass

    def add_client(self, client: WebSocketResponse, uuid: str):
        self.websocket_dict[uuid] = client

    def remove_client(self, client: WebSocketResponse):
        for uuid, ws in self.websocket_dict.items():
            if ws == client:
                del self.websocket_dict[uuid]
                break