# -*- coding: utf-8 -*-

import argparse
import cv2
import numpy as np
import progressbar as pb
import cleanup
import timeline
import mediaoutput
import ui


class InfiniteCounter(object):
    """
    InfiniteCounter is a class that represents a counter that will
    return the next number indefinitely. When the user calls count()
    return the current number. Then it will increment the current
    number by the specified steps.
    """

    def __init__(self, start=0, step=1):
        """
        Default Initializer
        :param start: the starting value of the counter
        :param step: the amount that should be added at each step
        """
        self.current = start
        self.step = step

    def count(self):
        """
        The count method yields the current number and then
        increments the current number by the specified step in the
        default initializer
        :return: the successor from the previous number
        """
        while True:
            yield self.current
            self.current += self.step


class Detector(object):

    def __init__(self, device):
        self.cap = cv2.VideoCapture(sanitize_device(device))

    def detect_slides(self):

        sequence = timeline.Timeline(self.cap)
        last_frame = sequence.next_frame()

        slide_writer = mediaoutput.TimestampImageWriter(sequence.fps, 'slides/')
        # slide_writer = IncrementalImageWriter('slides/slide ')
        slide_writer.write_image(last_frame, 0)

        progress = ui.ProgressController('Analyzing Video: ', sequence.len)
        progress.start()

        frame_counter = InfiniteCounter()
        for frame_count in frame_counter.count():

            frame = sequence.next_frame()

            if frame is None:
                break
            elif not are_same(last_frame, frame):
                slide_writer.write_image(frame, frame_count)

            last_frame = frame
            progress.update(frame_count)

        progress.finish()

        self.cap.release()


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
    if similarity > 0.99:
        return True
    return False


if __name__ == "__main__":
    Parser = argparse.ArgumentParser(description="OpenCV Test")
    Parser.add_argument("-d", "--device", help="video device number or path to video file")
    Parser.add_argument("-o", "--outfile", help="path to output video file")
    Args = Parser.parse_args()

    cleanup.remove_dirs()

    detector = Detector(Args.device)
    detector.detect_slides()

    cv2.destroyAllWindows()
