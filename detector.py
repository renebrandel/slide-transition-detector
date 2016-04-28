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


class Timeline(object):
    """
    The Timeline represents a logical sequence of frames, where the
    rendering of frames from the video stream will be done through
    lazy evaluation.
    """
    rendered_frames = []
    reader_head = 0
    
    def __init__(self, stream):
        """
        Default Constructor
        :param stream: the video stream from OpenCV
        """
        self.stream = stream

    def render_frames(self, pos):
        """
        This method evaluates the video stream and converts its values
        into frames up to the specified position.
        :param pos: the position to which the stream shall be rendered
        (including frame at pos)
        """
        assert pos >= 0
        while pos >= self.reader_head:
            self.next_frame()

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

        self.rendered_frames.append(frame)
        return frame

    def get_frame(self, pos):
        """
        Returns the frame at the given position of the frame sequence
        :param pos: the position of the frame in the sequence
        :return: the frame at the specified position
        """
        assert pos >= 0

        if pos >= self.reader_head:
            self.render_frames(pos)
        return self.rendered_frames[pos]

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

        if end >= self.reader_head:
            self.render_frames(end)
        return self.rendered_frames[start:end]


class SlidingWindow(object):

    def __init__(self, timeline, pos=0, size=2):
        self.timeline = timeline
        self.pos = pos
        self.size = size

    def move_right(self):
        self.pos += 1

    def move_left(self):
        self.pos -= 1

    def shrink_from_left(self):
        self.pos += 1
        self.size -= 1

    def shrink_from_right(self):
        self.size -= 1

    def expand_from_left(self):
        self.pos -= 1
        self.size += 1

    def expand_from_right(self):
        self.size += 1

    def action_on_frame(self, action):
        for frame in self.get_frames():
            return action(frame)

    def get_frames(self):
        return self.timeline.get_frames(self.pos, self.pos + self.size)


class Detector(object):

    def __init__(self, device):
        setup_dirs()
        self.cap = cv2.VideoCapture(sanitize_device(device))

    def detect_slides(self):

        timeline = Timeline(self.cap)
        last_frame = timeline.next_frame()

        slide_writer = ImageWriter('slides/slide ')
        slide_writer.write_image(last_frame)

        while True:
            frame = timeline.next_frame()

            if frame is None:
                break
            elif not are_same(last_frame, frame):
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
