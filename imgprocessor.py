from abc import ABCMeta, abstractmethod
import cv2


class ImageProcessor(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def process(self, img):
        pass


class GrayscaleProcessor(ImageProcessor):

    def process(self, img):
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


class ImageProcessQueue(object):

    def __init__(self, processors=None):
        elem = []
        if not processors is None:
            elem = processors
        self.queue = elem

    def add(self, processor):
        self.queue.append(processor)

    def apply(self, img):
        for processor in self.queue:
            img = processor.process(img)
        return img