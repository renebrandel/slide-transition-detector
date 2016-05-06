import cv2
import numpy as np
from abc import ABCMeta, abstractmethod


class ImageComparator(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def are_similar(self, first, second):
        pass

    def __init__(self, threshold):
        self.threshold = threshold

    def are_same(self, first, second):
        return self.are_similar(first, second) >= self.threshold


class AbsDiffHistComparator(ImageComparator):

    def __init__(self, threshold):
        super(AbsDiffHistComparator, self).__init__(threshold)

    def are_similar(self, first, second):
        res = cv2.absdiff(first, second)
        hist = cv2.calcHist([res], [0], None, [256], [0, 256])
        return 1 - np.sum(hist[15::]) / np.sum(hist)

