# -*- coding: utf-8 -*-

import cv2


class Timeline(object):
    """
    The Timeline represents a logical sequence of frames, where the
    rendering of frames from the video stream will be done through
    lazy evaluation.
    """
    reader_head = 0

    def __init__(self, stream):
        """
        Default Initializer
        :param stream: the video stream from OpenCV
        """
        self.stream = stream
        self.len = stream.get(cv2.CAP_PROP_FRAME_COUNT)
        self.fps = stream.get(cv2.CAP_PROP_FPS)

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
        self.stream.set(cv2.CAP_PROP_POS_FRAMES, self.len - 1)
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

    def release_stream(self):
        self.stream.release()


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
        Default Initializer for the sliding window
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

    def get_frame(self, pos):
        return self.timeline.get_frame(self.pos)

    def get_start_frame(self):
        return self.timeline.get_frame(self.pos)

    def get_end_frame(self):
        return self.timeline.get_frame(self.pos + self.size - 1)

    def at_end(self):
        return self.pos + self.size == self.timeline.len
