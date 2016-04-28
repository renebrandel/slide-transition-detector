import argparse
import cv2
import os
import numpy as np

class InfiniteCounter:

    def __init__(self, start=0, step=1):
        self.current = start
        self.step = step

    def count(self):
        while True:
            yield self.current
            self.current += self.step

class ImageWriter:

    def __init__(self, prefix='img ', file_format='.jpg', count=0):
        if not file_format.startswith('.'):
            file_format = '.' + file_format
        self.count = count
        self.name = prefix + '%d' + file_format

    def write_image(self, img):
        cv2.imwrite(self.name % self.count, img)
        self.count += 1


class Detector:

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

            if not are_same(last_frame, frame, i):
                slide_writer.write_image(frame)
            last_frame = frame

        self.cap.release()


class DetectionStrategy:

    pass


def sanitize_device(device):
    """returns device id if device can be converted to an integer"""
    try:
        return int(device)
    except (TypeError, ValueError):
        return device


def are_same(fst, snd, count):
    res = cv2.subtract(snd, fst)
    hist = cv2.calcHist([res], [0], None, [256], [0, 256])
    similarity = 1 - np.sum(hist[15::]) / np.sum(hist)
    print count, similarity
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
