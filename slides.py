import os
import cv2


class Slide(object):
    """
    Represents a slide
    """
    def __init__(self, time, img):
        """
        Default initializer for a slide representation
        :param time: the time when the slide appears
        :param img: the image representing the slide
        """
        self.time, _ = os.path.splitext(time)
        self.img = img
        self.marked = False
        self.times = []

    def add_time(self, time):
        """
        Add an additional instance in time, when the slide
        is displayed.
        :param time: the time when the slide is displayed
        """
        self.times.append(time)


class SlideDataHelper(object):
    """
    The helps to get slides from data.
    """
    def __init__(self, path):
        """
        Default initializer
        :param path: the path, where the slide is stored on disk
        """
        self.path = path

    def get_slides(self):
        """
        Gets the slide from disk and returns them as list of "Slide"
        objects.
        :return: The slides stored on disk as list of "Slide" objects.
        """
        slides = []
        for filename in sorted(os.listdir(self.path)):
            file_path = os.path.join(self.path, filename)
            _, ext = os.path.splitext(file_path)
            if not is_image(ext):
                continue
            slide = Slide(filename, cv2.imread(file_path))
            slides.append(slide)

        return slides


def is_image(ext):
    """
    Checks if the file_format is a supported image to read.
    :param ext: the extension of a file.
    :return: whether or not the file is a image
    """
    return ext == '.jpeg' or ext == '.png' or ext == '.jpg' or ext == '.bmp'
