from abc import ABCMeta, abstractmethod
import datetime
import cv2
import math
import os
import errno


class MediaWriter(object):
    """
    Abstract class for all media outputs. Forcing each inheritance
    to have a write class.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def write(self, content, *args):
        """
        Write method to write media to disk
        :param media: the media to be written
        :param args: additional arguments that may be helpful
        """
        pass


class NullWriter(MediaWriter):
    def write(self, content, *args):
        pass


class ImageWriter(MediaWriter):
    """
    The ImageWriter will write an image to disk.
    """
    __metaclass__ = ABCMeta

    def __init__(self, prefix, file_format):
        """
        Default initializer
        :param prefix: the filename prefix a counter will be added
        after this string and incremented after each write to disk
        :param file_format: the file format for the images.
        """
        if not file_format.startswith('.'):
            file_format = '.' + file_format
        if prefix is not None:
            setup_dirs(prefix)
            self.name = prefix + file_format

    def write(self, img, *args):
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


class CustomImageWriter(ImageWriter):
    """
    Image Writer that uses a custom name. It takes it as the first
    argument in *args in the write method.
    """
    def __init__(self, prefix=None, file_format='.jpg'):
        """
        Default initializer
        :param prefix: the file location and file name prefix
        :param file_format: the file format e.g. .jpg, .png
        """
        super(CustomImageWriter, self).__init__(prefix + '%s', file_format)

    def next_name(self, *args):
        return args[0]


class IncrementalImageWriter(ImageWriter):
    """
    The IncrementalImageWriter will write an image to disk and append a
    number to the file name. This number will be auto-incremented by the
    specified step size after each write.
    """

    def __init__(self, prefix=None, file_format='.jpg', start=0, step=1):
        """
        Default initializer
        :param prefix: the file location and file name
        :param file_format: the file format e.g. .jpg, .png
        :param start: the starting number for the incremental count
        :param step: the step by which the count should increment
        """
        self.count = start - step
        self.step = step
        if prefix is not None:
            prefix += '%d'
        super(IncrementalImageWriter, self).__init__(prefix, file_format)

    def next_name(self, *args):
        self.count += self.step
        return self.count


class TimestampImageWriter(ImageWriter):
    """
    TimestampImageWriter is a ImageWriter that adds the timestamp of when
    the image was first shown in the original stream
    """

    def __init__(self, fps, prefix=None, file_format='.jpg'):
        """
        Default initializer
        :param fps: The number of frames per second in the original stream
        :param prefix: the prefix of the path to the output location
        :param file_format: the file format of the output image
        """
        self.fps = fps

        if prefix is not None:
            prefix += '%s'
        super(TimestampImageWriter, self).__init__(prefix, file_format)

    def next_name(self, args):
        current_frame = args[0]
        seconds = current_frame / self.fps
        milliseconds = seconds - math.floor(seconds)
        if milliseconds == 0:
            milliseconds = '000'
        else:
            milliseconds = str(int(milliseconds * (10 ** 3)))
        return str(datetime.timedelta(seconds=int(seconds))) + '.' + milliseconds.zfill(3)


class TimetableWriter(MediaWriter):
    """
    The Timetable Writer outputs each slide iteratively using
    the IncrementalImageWriter. Additionally it outputs a ".txt"
    document containing the slide name and their appearances.
    """
    def __init__(self, output_dir, timetable_loc, file_format):
        """
        Default initializer
        :param output_dir: the output directory for the sorted slides
        :param timetable_file: where the timetable file should be stored
        """
        setup_dirs(timetable_loc)
        self.timetable = open(timetable_loc, 'w')
        self.img_writer = IncrementalImageWriter(prefix=output_dir, start=1, file_format=file_format)
        self.txt_writer = TextWriter(self.timetable)

    def write(self, slides, *args):
        i = 1
        for slide in slides:
            if slide.marked:
                continue
            self.img_writer.write(slide.img)
            appearances = slide.time
            for com in slide.times:
                appearances += " " + com
            self.txt_writer.write("Slide %d: %s\n" % (i, appearances))
            i += 1


    def close(self):
        self.timetable.close()


class TextWriter(MediaWriter):
    def __init__(self, output_file):
        self.output_file = output_file

    def write(self, content, *args):
        self.output_file.write(content)

def setup_dirs(path):
    """
    Takes a path and makes sure that directories to the path
    gets created and is writable.
    :param filename: the path to file
    """
    path = os.path.dirname(path)
    if path == '':
        return
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
