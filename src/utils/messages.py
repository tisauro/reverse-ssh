import json
# from typing import Self


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
        super().__init__(msg_type="reverse-ssh", device_id=device_id)

    @classmethod
    def from_json(cls, json_msg: str):
        msg: dict = json.loads(json_msg)
        if msg.get("type") == "reverse-ssh":
            device_id = msg.get("device_id")
            return cls(device_id)
        else:
            raise Exception


class SSHClientConnect(SSHMessage):

    def __init__(self, device_id: str, status: str) -> None:
        super().__init__(device_id)
        self.action = "open_connection"
        self.status = status

    @classmethod
    def from_json(cls, json_msg: str):
        msg: dict = json.loads(json_msg)
        if msg.get("type") == "reverse-ssh" and \
                msg.get("action") == "open_connection":
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

    def __xor__(self, other):
        print("in here")

        pass

    def __invert__(self):
        if self.status == "new":
            self.status = "done"
        else:
            self.status = 'new'
        return self
