# -*- coding: utf-8 -*-

import argparse
import cv2
import os
import numpy as np
import progressbar as pb
import datetime
import math
import errno
import cleanup
from abc import ABCMeta, abstractmethod


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


class ProgressController(object):
    def __init__(self, title, total):
        self.widgets = [title, pb.Percentage(), ' - ', pb.Bar(), ' ']
        self.total = total
        self.progress = None

    def start(self):
        print
        self.progress = pb.ProgressBar(widgets=self.widgets,maxval=self.total).start()

    def update(self, i):
        assert self.progress is not None
        self.progress.update(i)

    def finish(self):
        assert self.progress is not None
        self.progress.finish()
        print


class ImageWriter(object):
    """
    The ImageWriter will write an image to disk and auto-increments
    the filename.
    """

    __metaclass__ = ABCMeta

    def __init__(self, prefix='img ', file_format='.jpg'):
        """
        Default constructor
        :param prefix: the filename prefix a counter will be added
        after this string and incremented after each write to disk
        :param file_format: the file format for the images.
        :param count: the starting number of the counter
        """
        if not file_format.startswith('.'):
            file_format = '.' + file_format
        setup_dirs(prefix)
        self.name = prefix + file_format

    def write_image(self, img, *args):
        """
        Writes the given image to the location specified through the
        constructor
        :param img: the image that will be written to disk
        """
        cv2.imwrite(self.name % self.next_name(args), img)

    @abstractmethod
    def next_name(self, *args): pass


class IncrementalImageWriter(ImageWriter):
    def __init__(self,prefix='img ', file_format='.jpg', start=0, step=1):
        self.count = start - step
        self.step = step
        super(IncrementalImageWriter, self).__init__(prefix + '%d', file_format)

    def next_name(self, *args):
        self.count += self.step
        return self.count


class TimestampImageWriter(ImageWriter):
    def __init__(self, max_frames, fps, prefix='img ', file_format='.jpg'):
        self.max_frames = max_frames
        self.fps = fps
        super(TimestampImageWriter, self).__init__(prefix + '%s', file_format)

    def next_name(self, args):
        current_frame = args[0]
        seconds = current_frame / self.fps
        milliseconds = seconds - math.floor(seconds)
        if milliseconds == 0:
            milliseconds = '000'
        else:
            milliseconds = str(int(milliseconds * (10 ** 3)))
        return str(datetime.timedelta(seconds=int(seconds))) + '.' + milliseconds.zfill(3)


class Timeline(object):
    """
    The Timeline represents a logical sequence of frames, where the
    rendering of frames from the video stream will be done through
    lazy evaluation.
    """
    reader_head = 0
    
    def __init__(self, stream):
        """
        Default Constructor
        :param stream: the video stream from OpenCV
        """
        self.stream = stream
        self.stream_len = stream.get(cv2.CAP_PROP_FRAME_COUNT)
        self.stream_fps = stream.get(cv2.CAP_PROP_FPS)

    def next_frame(self):
        """
        This method reads the next frame from the video stream and
        append it to the rendered_frames list. It also increments the
        reader_head by 1.
        :return: Usually the recently evaluated frame.
        If the video stream has been completely read, it will return
        None
        """
        ret, frame = self.stream.read()
        self.reader_head += 1

        if not ret:
            return None

        return frame

    def get_frame(self, pos):
        """
        Returns the frame at the given position of the frame sequence
        :param pos: the position of the frame in the sequence
        :return: the frame at the specified position
        """
        assert pos >= 0
        self.stream.set(cv2.CAP_PROP_POS_FRAMES, self.stream_len - 1)
        _, frame = self.stream.read()
        self.reader_head = pos + 1
        return frame


    def get_frames(self, start, end):
        """
        Returns the list of frames at between the specified start and
        end position in the frame sequence.
        :param start: Where the frame sequence should start
        :param end: Where the frame sequence should end
        :return: the frame sequence from start to end
        """
        assert end >= start
        assert start >= 0

        result = []
        for i in xrange(start, end, 1):
            result.append(self.get_frame(i))
        return result


class SlidingWindow(object):
    """
    This class represents an adaptive sliding window. Meaning
    that it has a pointer to the start position of the window
    and its size. The size of the window can be changed at any
    time. Move operations and shrink and expand operations are
    included.
    """
    def __init__(self, timeline, pos=0, size=2):
        """
        Default constructor for the sliding window
        :param timeline: the timeline where the sliding window
        should be applied
        :param pos: the position where the beginning of the
        window points to
        :param size: the size of the window
        """
        self.timeline = timeline
        self.pos = pos
        self.size = size

    def move_right(self):
        """
        This method does this:
        ░|░|█|█|░|░ => ░|░|░|█|█|░
        1 2 3 4 5 6    1 2 3 4 5 6
        :return: the changed list of frame
        """
        self.pos += 1

    def move_left(self):
        """
        This method does this:
        ░|░|█|█|░|░ => ░|█|█|░|░|░
        1 2 3 4 5 6    1 2 3 4 5 6
        :return: the changed list of frame
        """
        self.pos -= 1

    def shrink_from_left(self):
        """
        This method does this:
        ░|░|█|█|░|░ => ░|░|░|█|░|░
        1 2 3 4 5 6    1 2 3 4 5 6
        :return: the changed list of frame
        """
        self.pos += 1
        self.size -= 1

    def shrink_from_right(self):
        """
        This method does this:
        ░|░|█|█|░|░ => ░|░|█|░|░|░
        1 2 3 4 5 6    1 2 3 4 5 6
        :return: the changed list of frame
        """
        self.size -= 1

    def expand_to_left(self):
        """
        This method does this:
        ░|░|█|█|░|░ => ░|█|█|█|░|░
        1 2 3 4 5 6    1 2 3 4 5 6
        :return: the changed list of frame
        """
        self.pos -= 1
        self.size += 1

    def expand_to_right(self):
        """
        This method does$$ this:
        ░|░|█|█|░|░ => ░|░|█|█|█|░
        1 2 3 4 5 6    1 2 3 4 5 6
        :return: the changed list of frame
        """
        self.size += 1

    def get_frames(self):
        """
        Retrieves all the frames that are currently in this adaptive
        sliding window.
        :return: the frames in the sliding window
        """
        return self.timeline.get_frames(self.pos, self.pos + self.size)


class Detector(object):

    def __init__(self, device):
        self.cap = cv2.VideoCapture(sanitize_device(device))

    def detect_slides(self):

        timeline = Timeline(self.cap)
        last_frame = timeline.next_frame()

        slide_writer = TimestampImageWriter(timeline.stream_len, timeline.stream_fps, 'slides/')
        # slide_writer = IncrementalImageWriter('slides/slide ')
        slide_writer.write_image(last_frame, 0)

        progress = ProgressController('Analyzing Video: ', timeline.stream_len)
        progress.start()

        frame_counter = InfiniteCounter()
        for frame_count in frame_counter.count():

            frame = timeline.next_frame()

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


def setup_dirs(filename):
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise


if __name__ == "__main__":
    Parser = argparse.ArgumentParser(description="OpenCV Test")
    Parser.add_argument("-d", "--device", help="video device number or path to video file")
    Parser.add_argument("-o", "--outfile", help="path to output video file")
    Args = Parser.parse_args()

    cleanup.remove_dirs()

    detector = Detector(Args.device)
    detector.detect_slides()

    cv2.destroyAllWindows()
