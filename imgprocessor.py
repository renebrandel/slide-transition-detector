from abc import ABCMeta, abstractmethod

class ImageProcessor(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def process(self, img):
        pass


class ImageProcessQueue(object):
    def __init__(self, processors=None):
        elem = []
        if not processors is None:
            elem = processors
        self.queue = elem

    def add(self, processor):
        self.queue.append(processor)

    def apply(self, imgs):
        for img in imgs:
            for processor in self.queue:
                img = processor.process(img)

        return imgs