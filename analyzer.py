from abc import ABCMeta, abstractmethod


class Analyzer(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def analyze(self):
        pass
