import json
from src.utils import const


class BaseMessage:
    def __init__(self, msg_type: str, device_id: str):
        self.type = msg_type
        self.device_id = device_id

    def __str__(self):
        """

        :return: json object of the class
        """
        return json.dumps(self.__dict__)


class SSHMessage(BaseMessage):
    def __init__(self, device_id: str):
        super().__init__(msg_type=const.SSH_MSG_TYPE, device_id=device_id)

    @classmethod
    def from_json(cls, json_msg: str):
        msg: dict = json.loads(json_msg)
        if msg.get("type") == const.SSH_MSG_TYPE:
            device_id = msg.get("device_id")
            return cls(device_id)
        else:
            raise Exception


class SSHClientConnect(SSHMessage):

    def __init__(self, device_id: str, status: str) -> None:
        super().__init__(device_id)
        self.action = const.ACT_CONNECTION
        self.status = status

    @classmethod
    def from_json(cls, json_msg: str):
        msg: dict = json.loads(json_msg)
        if msg.get("type") == const.SSH_MSG_TYPE and \
                msg.get("action") == const.ACT_CONNECTION:
            status = msg.get("status")
            device_id = msg.get("device_id")
            return cls(device_id, status)
        else:
            raise Exception

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SSHClientConnect):
            return False
        return self.status == other.status and self.action == other.action \
               and self.type == other.type and self.device_id == other.device_id

    def __invert__(self):
        if self.status == const.REQUEST_OPEN:
            self.status = const.RESPONSE_OPEN
        else:
            self.status = const.REQUEST_OPEN
        return self


class WebMessage(BaseMessage):
    def __init__(self, device_id: str):
        super().__init__(msg_type=const.WEB_MSG_TYPE, device_id=device_id)

    @classmethod
    def from_json(cls, json_msg: str):
        msg: dict = json.loads(json_msg)
        if msg.get("type") == const.WEB_MSG_TYPE:
            device_id = msg.get("device_id")
            return cls(device_id)
        else:
            raise Exception


class WebClientConnect(WebMessage):

    def __init__(self, device_id: str, status: str) -> None:
        super().__init__(device_id)
        self.action = const.ACT_CONNECTION
        self.status = status

    @classmethod
    def from_json(cls, json_msg: str):
        msg: dict = json.loads(json_msg)
        if msg.get("type") == const.WEB_MSG_TYPE and \
                msg.get("action") == const.ACT_CONNECTION:
            status = msg.get("status")
            device_id = msg.get("device_id")
            return cls(device_id, status)
        else:
            raise Exception

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, WebClientConnect):
            return False
        return self.status == other.status and self.action == other.action \
               and self.type == other.type and self.device_id == other.device_id

    def __invert__(self):
        if self.status == const.REQUEST_OPEN:
            self.status = const.RESPONSE_OPEN
        else:
            self.status = const.REQUEST_OPEN
        return self


class WebClientMessage(WebMessage):
    def __init__(self, device_id: str, message: str) -> None:
        super().__init__(device_id)
        self.action = const.ACT_CONNECTION
        self.message = message


class WebClientHistMessage(WebMessage):
    def __init__(self, device_id: str, message: str) -> None:
        super().__init__(device_id)
        self.action = const.ACT_HISTORY
        self.message = message
    @classmethod
    def from_json(cls, json_msg: str):
        msg: dict = json.loads(json_msg)
        if msg.get("type") == const.WEB_MSG_TYPE and \
                msg.get("action") == const.ACT_HISTORY:
            message = msg.get("message")
            device_id = msg.get("device_id")
            return cls(device_id, message)
        else:
            raise Exception