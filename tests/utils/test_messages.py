import json

from src.utils.messages import SSHClientConnect, BaseMessage, SSHMessage


def test_base_message():
    message = BaseMessage(msg_type="test", device_id="dummy_device")
    print(message)


def test_ssh_client_connect():
    message = SSHClientConnect(device_id="dummy_device", status="new")
    print(message)


def test_ssh_message_class_constructor():
    message = json.dumps({
        "type": "reverse-ssh",
        "device_id": "dummy_device"
    })
    ssh_message = SSHMessage.from_json(message)
    print(ssh_message)
    assert str(ssh_message) == message


def test_ssh_client_from_json_construtor():
    message = json.dumps({
        "type": "reverse-ssh",
        "device_id": "dummy_device",
        "action": "open_connection",
        "status": "new"
    })
    ssh_client_message = SSHClientConnect.from_json(message)
    print(ssh_client_message)
    assert str(ssh_client_message) == message

    print("")
    print(dir(ssh_client_message))


def test_ssh_client_not():
    ss_client_1 = SSHClientConnect(device_id="dummy_device", status="new")
    #ss_client_2 = SSHClientConnect(device_id="dummy_device", status="open")
    ss_client_2 = ~ss_client_1
    assert ss_client_2 == ~ss_client_1
    print(ss_client_2)
