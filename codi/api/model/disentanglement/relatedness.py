from ..input.message import Message


class Relatedness:
    """
    This class represents a pair of messages which have a percentage of relatedness.
    """
    def __init__(self):
        self._message1 = None
        self._message2 = None
        self._percentage = None

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f'Relatedness: [msg1: {self._message1.processable_text}, msg2: {self._message2.processable_text}]'

    @property
    def message1(self):
        return self._message1

    @property
    def message2(self):
        return self._message2

    @property
    def percentage(self):
        return self._percentage

    @message1.setter
    def message1(self, message1: Message):
        self._message1 = message1

    @message2.setter
    def message2(self, message2: Message):
        self._message2 = message2

    @percentage.setter
    def percentage(self, percentage: float):
        self._percentage = percentage
