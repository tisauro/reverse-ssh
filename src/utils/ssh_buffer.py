from typing import List, Generator


class SSHBufferIterator:
    ''' Iterator class '''

    def __init__(self, buffer):
        # Team object reference
        self._buffer = buffer
        # member variable to keep track of current index
        self._index = 0

    def __next__(self):
        ''''Returns the next value from team object's lists '''
        if self._index < self._buffer.len():
            result = self._buffer.get_line(self._index)
            self._index += 1
            return result
        # End of Iteration
        raise StopIteration


class SSHBuffer:
    def __init__(self, max_size: int = 100):
        self.__max_size: int = max_size
        self.__buffer: List[str] = []

    def add_to_history(self, line: [str, List[str]]) -> None:
        if type(line) == str:
            self.__buffer.append(line)
        else:
            self.__buffer.extend(line)

        self.__buffer = self.__buffer[-self.__max_size::1]

    def len(self) -> int:
        return len(self.__buffer)

    def get_history(self) -> List[str]:
        return self.__buffer.copy()

    def get_line(self, index: int) -> str:
        if index <= self.len():
            return self.__buffer[index]

    # create iterator
    def get_iter(self) -> Generator:
        return (line for line in self.__buffer)

    def __iter__(self):
        return SSHBufferIterator(self)
