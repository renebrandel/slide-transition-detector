import cv2
import os
import mediaoutput
import imgcomparison as ic
import argparse
import ui
from slides import SlideDataHelper


class SlideSorter(object):
    """
    Sorts the slides according to their timestamp.
    """

    def __init__(self, path, comparator, outpath, timetable_loc, file_format):
        """
        Default initializer
        :param path: the path where the slides are located on disk
        :param comparator: the comparator to determine, if two slides
        are duplicates.
        """
        self.comparator = comparator
        self.inpath = path
        self.outpath = outpath
        self.timetable_loc = timetable_loc
        self.file_format = file_format

    def sort(self):
        """
        Sorting the slides and write the new slides without duplicates
        but with a timetable to disk.
        """
        slides = SlideDataHelper(self.inpath).get_slides()
        unique_slides = self.group_slides(slides)

        mediaoutput.setup_dirs(self.timetable_loc)
        timetable = open(self.timetable_loc, 'w')
        mediaoutput.TimetableWriter(self.outpath, timetable, self.file_format).write(unique_slides)
        timetable.close()

    def group_slides(self, slides):
        """
        Groups the slides by eliminating duplicates.
        :param slides: the list of slides possibly containing duplicates
        :return: a list of slides without duplicates
        """

        progress = ui.ProgressController('Sorting Slides: ', len(slides))
        progress.start()
        for i in xrange(len(slides)):
            progress.update(i)
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
        progress.finish()
        return unique_slides


if __name__ == '__main__':

    Parser = argparse.ArgumentParser(description="Slide Sorter")
    Parser.add_argument("-d", "--inputslides", help="path of the sequentially sorted slides", default="slides/")
    Parser.add_argument("-o", "--outpath", help="path to output slides", default="unique/", nargs='?')
    Parser.add_argument("-f", "--fileformat", help="file format of the output images e.g. '.jpg'",
                        default=".jpg", nargs='?')
    Parser.add_argument("-t", "--timetable",
                        help="path where the timetable should be written (default is the outpath+'timetable.txt')",
                        nargs='?', default=None)
    Args = Parser.parse_args()
    if Args.timetable is None:
        Args.timetable = os.path.join(Args.outpath, "timetable.txt")

    sorter = SlideSorter(Args.inputslides, ic.AbsDiffHistComparator(0.99), Args.outpath, Args.timetable, Args.fileformat)
    sorter.sort()