# -*- coding: utf-8 -*-

import argparse
import cv2
import imgcomparison
import timeline
import mediaoutput
import ui

from slides import Slide
from analyzer import Analyzer


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

    def increment(self):
        self.current += self.step

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


class Detector(Analyzer):

    def __init__(self, device, outpath=None, fileformat=".png"):
        cap = cv2.VideoCapture(sanitize_device(device))
        self.sequence = timeline.Timeline(cap)
        self.writer = mediaoutput.NullWriter()
        if outpath is not None:
            self.writer = mediaoutput.TimestampImageWriter(self.sequence.fps, outpath, fileformat)
        self.comparator = imgcomparison.AbsDiffHistComparator(0.99)

    def detect_slides(self):
        progress = ui.ProgressController('Analyzing Video: ', self.sequence.len)
        progress.start()
        frames = []
        name_getter = mediaoutput.TimestampImageWriter(self.sequence.fps)
        for i, frame in self.check_transition():
            progress.update(i)
            if frame is not None:
                frames.append(Slide(name_getter.next_name([i]), frame))

        progress.finish()

        self.sequence.release_stream()
        return frames

    def check_transition(self):
        prev_frame = self.sequence.next_frame()
        self.writer.write(prev_frame, 0)
        yield 0, prev_frame

        frame_counter = InfiniteCounter()
        for frame_count in frame_counter.count():

            frame = self.sequence.next_frame()

            if frame is None:
                break
            elif not self.comparator.are_same(prev_frame, frame):

                while True:
                    if self.comparator.are_same(prev_frame, frame):
                        break
                    prev_frame = frame
                    frame = self.sequence.next_frame()
                    frame_counter.increment()
                self.writer.write(frame, frame_count)
                yield frame_count, frame

            prev_frame = frame

            yield frame_count, None

    def analyze(self):
        for i, frame in self.check_transition():
            time = mediaoutput.TimestampImageWriter(self.sequence.fps).next_name([i])
            yield Slide(time, frame)


def sanitize_device(device):
    """returns device id if device can be converted to an integer"""
    try:
        return int(device)
    except (TypeError, ValueError):
        return device


if __name__ == "__main__":
    Parser = argparse.ArgumentParser(description="Slide Detector")
    Parser.add_argument("-d", "--device", help="video device number or path to video file")
    Parser.add_argument("-o", "--outpath", help="path to output video file", default="slides/", nargs='?')
    Parser.add_argument("-f", "--fileformat", help="file format of the output images e.g. '.jpg'",
                        default=".jpg", nargs='?')
    Args = Parser.parse_args()

    detector = Detector(Args.device, Args.outpath, Args.fileformat)
    detector.detect_slides()
