import cv2
import os
import mediaoutput
import imgcomparison


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


class SlideSorter(object):
    """
    Sorts the slides according to their timestamp.
    """

    def __init__(self, path, comparator):
        """
        Default initializer
        :param path: the path where the slides are located on disk
        :param comparator: the comparator to determine, if two slides
        are duplicates.
        """
        self.comparator = comparator
        self.path = path

    def sort(self):
        """
        Sorting the slides and write the new slides without duplicates
        but with a timetable to disk.
        """
        mediaoutput.setup_dirs('unique/')

        slides = SlideDataHelper(self.path).get_slides()
        unique_slides = self.group_slides(slides)

        timetable = open('unique/timetable.txt','w')
        mediaoutput.TimetableWriter(timetable).write(unique_slides)
        timetable.close()

    def group_slides(self, slides):
        """
        Groups the slides by eliminating duplicates.
        :param slides: the list of slides possibly containing duplicates
        :return: a list of slides without duplicates
        """
        for i in xrange(len(slides)):
            slide = slides[i]
            if slide.marked:
                continue

            for j in xrange(i, len(slides)):
                other = slides[j]
                if slide == other or other.marked:
                    continue

                if self.comparator.are_same(slide.img, other.img):
                    slide.add_time(other.time)
                    other.marked = True

        unique_slides = filter(lambda x: not x.marked, slides)

        return unique_slides


class SlideParser(object):
    """
    Reverses the effect of SlideSorter. Basically takes the timetable
    and the unique set of slides and turns them back into slides with
    their name representing their timestamp. (Possibly containing
    duplicates.)
    """
    def __init__(self, slides_dir, timetable_path):
        """
        Default initializer
        :param slides_dir: where the unique slides are located
        :param timetable_path: where the timetable file is located
        """
        self.timetable_path = timetable_path
        self.slides = SlideDataHelper(slides_dir).get_slides()

    def parse(self):
        """
        Parses the timetable and writes the images to disk accordingly.
        """
        writer = mediaoutput.CustomImageWriter('reversed/')
        with open(self.timetable_path) as timetable:
            for line in timetable:
                slide = self.slides.pop(0)
                slide_times = line[line.index(':') + 2:].split(' ')
                for time in slide_times:
                    writer.write(slide.img, time)


def is_image(ext):
    """
    Checks if the file_format is a supported image to read.
    :param ext: the extension of a file.
    :return: whether or not the file is a image
    """
    return ext == '.jpeg' or ext == '.png' or ext == '.jpg' or ext == '.bmp'

if __name__ == '__main__':

    SlideSorter('slides/', imgcomparison.AbsDiffHistComparator(0.99)).sort()
    SlideParser('unique/', 'unique/timetable.txt').parse()