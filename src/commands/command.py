import abc


class Command(abc.ABC):

    @staticmethod
    @abc.abstractmethod
    def name():
        pass

    @staticmethod
    @abc.abstractmethod
    def description():
        pass

    @abc.abstractmethod
    def build_parser(self, parser):
        pass

    @abc.abstractmethod
    def run(self, args):
        pass
