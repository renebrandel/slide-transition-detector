import cv2
import os
import mediaoutput
import imgcomparison as ic
import argparse
import sources
import ui
from slides import SlideDataHelper
from analyzer import Analyzer


class SlideSorter(Analyzer):
    """
    Sorts the slides according to their timestamp.
    """

    def __init__(self, source, comparator, outpath, timetable_loc, file_format):
        """
        Default initializer
        :param path: the path where the slides are located on disk
        :param comparator: the comparator to determine, if two slides
        are duplicates.
        """
        self.comparator = comparator
        self.outpath = outpath
        self.timetable_loc = timetable_loc
        self.file_format = file_format
        self.source = source

    def sort(self):
        """
        Sorting the slides and write the new slides without duplicates
        but with a timetable to disk.
        """
        progress = ui.ProgressController('Sorting Slides: ', len(self.source))
        progress.start()

        for i, _ in self.group_slides():
            progress.update(i)

        progress.finish()

    def group_slides(self):
        """
        Groups the slides by eliminating duplicates.
        :param slides: the list of slides possibly containing duplicates
        :return: a list of slides without duplicates
        """
        slides = []
        sorted_slides = []
        loop_counter = 0
        page_counter = 1
        for slide in self.source.contents():
            slides.append(slide)

            if slide.marked:
                continue
            not_found = True
            for other in slides[:-1]:
                if self.comparator.are_same(slide.img, other.img):
                    not_found = False
                    if other.marked:
                        other.reference.add_time(slide.time)
                        slide.reference = other.reference
                        slide.marked = True
                    else:
                        slide.reference = other
                        other.add_time(slide.time)
                        slide.marked = True
                    yield loop_counter, None

            if not_found:
                slide.page_number = page_counter
                yield loop_counter, slide
                sorted_slides.append(slide)
                page_counter += 1
            loop_counter += 1
        mediaoutput.setup_dirs(self.timetable_loc)
        timetable = open(self.timetable_loc, 'w')
        mediaoutput.TimetableWriter(self.outpath, timetable, self.file_format).write(sorted_slides)
        timetable.close()

    def analyze(self):
        for _, slide in self.group_slides():
            if slide is None:
                continue
            yield slide.img


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

    sorter = SlideSorter(sources.ListSource(SlideDataHelper(Args.inputslides).get_slides()),
                         ic.AbsDiffHistComparator(0.99), Args.outpath, Args.timetable, Args.fileformat)
    sorter.sort()
