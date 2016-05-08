import cv2
import numpy as np
from abc import ABCMeta, abstractmethod
import operator


class ImageComparator(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def are_similar(self, first, second):
        pass

    def __init__(self, threshold):
        self.threshold = threshold

    def are_same(self, first, second, op=operator.ge):
        return op(self.are_similar(first, second), self.threshold)


class AbsDiffHistComparator(ImageComparator):

    def __init__(self, threshold):
        super(AbsDiffHistComparator, self).__init__(threshold)

    def are_similar(self, first, second):
        res = cv2.absdiff(first, second)
        hist = cv2.calcHist([res], [0], None, [256], [0, 256])
        return 1 - np.sum(hist[15::]) / np.sum(hist)






class HistComparator(ImageComparator):

    __metaclass__ = ABCMeta

    def __init__(self, threshold):
        super(HistComparator, self).__init__(threshold)

    @abstractmethod
    def get_technique(self):
        pass

    def are_similar(self, first, second):

        result = 0
        for i in xrange(3):
            hist1 = cv2.calcHist([first], [i], None, [256], [0,256])
            hist2 = cv2.calcHist([second], [i], None, [256], [0,256])
            result += cv2.compareHist(hist1, hist2, self.get_technique())

        return result / 3


class CorrelationHistComparator(HistComparator):

    def __init__(self, threshold):
        super(CorrelationHistComparator, self).__init__(threshold)

    def get_technique(self):
        return cv2.HISTCMP_CORREL


class ChiHistComparator(HistComparator):

    def __init__(self, threshold):
        super(ChiHistComparator, self).__init__(threshold)

    def get_technique(self):
        return cv2.HISTCMP_CHISQR


class IntersectionHistComparator(HistComparator):

    def __init__(self, threshold):
        super(IntersectionHistComparator, self).__init__(threshold)

    def get_technique(self):
        return cv2.HISTCMP_INTERSECT


class BhattacharyyaHistComparator(HistComparator):

    def __init__(self, threshold):
        super(BhattacharyyaHistComparator, self).__init__(threshold)

    def get_technique(self):
        return cv2.HISTCMP_BHATTACHARYYA
