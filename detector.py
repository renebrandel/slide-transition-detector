import argparse
import cv2
import os
import numpy as np


class InfiniteCounter(object):
    """
    InfiniteCounter is a class that represents a counter that will
    return the next number indefinitely. When the user calls count()
    return the current number. Then it will increment the current
    number by the specified steps.
    """

    def __init__(self, start=0, step=1):
        """
        Default Constructor
        :param start: the starting value of the counter
        :param step: the amount that should be added at each step
        """
        self.current = start
        self.step = step

    def count(self):
        """
        The count method yields the current number and then
        increments the current number by the specified step in the
        default constructor
        :return: the successor from the previous number
        """
        while True:
            yield self.current
            self.current += self.step


class ImageWriter(object):
    """
    The ImageWriter will write an image to disk and auto-increments
    the filename.
    """
    def __init__(self, prefix='img ', file_format='.jpg', count=0):
        """
        Default constructor
        :param prefix: the filename prefix a counter will be added
        after this string and incremented after each write to disk
        :param file_format: the file format for the images.
        :param count: the starting number of the counter
        """
        if not file_format.startswith('.'):
            file_format = '.' + file_format
        self.count = count
        self.name = prefix + '%d' + file_format

    def write_image(self, img):
        """
        Writes the given image to the location specified through the
        constructor
        :param img: the image that will be written to disk
        """
        cv2.imwrite(self.name % self.count, img)
        self.count += 1


class Detector(object):

    def __init__(self, device):
        setup_dirs()
        self.cap = cv2.VideoCapture(sanitize_device(device))

    def detect_slides(self):
        _, last_frame = self.cap.read()

        slide_writer = ImageWriter('slides/slide ')
        slide_writer.write_image(last_frame)

        slide_counter = InfiniteCounter()

        for i in slide_counter.count():
            ret, frame = self.cap.read()

            if not ret:
                break
            print i,
            if not are_same(last_frame, frame):
                slide_writer.write_image(frame)
            last_frame = frame

        self.cap.release()


class DetectionStrategy(object):

    pass


def sanitize_device(device):
    """returns device id if device can be converted to an integer"""
    try:
        return int(device)
    except (TypeError, ValueError):
        return device


def are_same(fst, snd):
    res = cv2.subtract(snd, fst)
    hist = cv2.calcHist([res], [0], None, [256], [0, 256])
    similarity = 1 - np.sum(hist[15::]) / np.sum(hist)
    print similarity
    if similarity > 0.99:
        return True
    return False


def setup_dirs():
    if not os.path.exists('img'):
        os.makedirs('img')

    if not os.path.exists('slides'):
        os.makedirs('slides')

    if not os.path.exists('matches'):
        os.makedirs('matches')


if __name__ == "__main__":
    Parser = argparse.ArgumentParser(description="OpenCV Test")
    Parser.add_argument("-d", "--device", help="video device number or path to video file")
    Parser.add_argument("-o", "--outfile", help="path to output video file")
    Args = Parser.parse_args()

    detector = Detector(Args.device)
    detector.detect_slides()

    cv2.destroyAllWindows()
