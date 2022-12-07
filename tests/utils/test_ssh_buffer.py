from src.utils.ssh_buffer import SSHBuffer, SSHBufferIterator
from types import GeneratorType


def test_add_line():
    ssh_buffer = SSHBuffer(10)
    ssh_buffer.add_to_history("hello")
    assert ssh_buffer.len() == 1


def test_always_max_size():
    ssh_buffer = SSHBuffer(10)
    lines = [x for x in range(12)]
    assert type(lines) == list
    ssh_buffer.add_to_history(lines)
    assert ssh_buffer.len() == 10
    lines = lines[-10::1]
    assert ssh_buffer.get_history() == lines
    print(ssh_buffer.__dir__())
    print(ssh_buffer.__dict__)


def test_generator():
    ssh_buffer = SSHBuffer(10)
    lines = [x for x in range(15)]
    ssh_buffer.add_to_history(lines)
    line_iter = ssh_buffer.get_iter()
    print(line_iter)
    assert isinstance(line_iter, GeneratorType)


def test_iterator():
    ssh_buffer = SSHBuffer(10)
    lines = [x for x in range(10)]
    ssh_buffer.add_to_history(lines)

    res = iter(ssh_buffer)
    assert isinstance(res, SSHBufferIterator)
    print('\n buffer')
    for lines1 in ssh_buffer:
        print(lines1, end=' ')

    print('\n lines')
    for x in lines:

        print(x, end=' ')
