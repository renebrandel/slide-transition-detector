from abc import ABCMeta, abstractmethod
import datetime
import cv2
import math
import os
import errno

class ImageWriter(object):
    """
    The ImageWriter will write an image to disk.
    """

    __metaclass__ = ABCMeta

    def __init__(self, prefix='img ', file_format='.jpg'):
        """
        Default initializer
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
        initializer
        :param img: the image that will be written to disk
        """
        cv2.imwrite(self.name % self.next_name(args), img)

    @abstractmethod
    def next_name(self, *args):
        """
        This abstract method returns the object that should be inserted
        into the filename
        :param args: the args, that is passed to write_image
        :return: the object that will be inserted into the filename
        """


class IncrementalImageWriter(ImageWriter):
    """
    The IncrementalImageWriter will write an image to disk and append a
    number to the file name. This number will be auto-incremented by the
    specified step size after each write.
    """

    def __init__(self,prefix='img ', file_format='.jpg', start=0, step=1):
        """
        Default initializer
        :param prefix: the file location and file name
        :param file_format: the file format e.g. .jpg, png
        :param start: the starting number for the incremental count
        :param step: the step by which the count should increment
        """
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


def setup_dirs(filename):
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise