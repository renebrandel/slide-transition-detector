import mediaoutput
import argparse
import cv2
import os

from slides import SlideDataHelper


class SlideParser(object):
    """
    Reverses the effect of SlideSorter. Basically takes the timetable
    and the unique set of slides and turns them back into slides with
    their name representing their timestamp. (Possibly containing
    duplicates.)
    """
    def __init__(self, slides_dir, timetable_path, output_dir, file_format):
        """
        Default initializer
        :param slides_dir: where the unique slides are located
        :param timetable_path: where the timetable file is located
        """
        self.timetable_path = timetable_path
        self.slides = SlideDataHelper(slides_dir).get_slides()
        self.output_dir = output_dir
        self.file_format = file_format

    def parse(self):
        """
        Parses the timetable and writes the images to disk accordingly.
        """
        writer = mediaoutput.CustomImageWriter(self.output_dir, self.file_format)
        with open(self.timetable_path) as timetable:
            for line in timetable:
                slide = self.slides.pop(0)
                slide_times = line[line.index(':') + 2:].split(' ')
                for time in slide_times:
                    writer.write(slide.img, time.rstrip())


if __name__ == '__main__':
    Parser = argparse.ArgumentParser(description="Slide Sorter")
    Parser.add_argument("-d", "--inputslides", help="path of the sequentially sorted slides", default="unique/")
    Parser.add_argument("-t", "--timetable", help="path to the timetable file", default=None, nargs='?')
    Parser.add_argument("-o", "--output_dir", help="path to which the reversed slides should be written",
                        default="reversed/")
    Parser.add_argument("-f", "--fileformat", help="file format of the output images e.g. '.jpg'",
                        default=".jpg", nargs='?')
    Args = Parser.parse_args()
    if Args.timetable is None:
        Args.timetable = os.path.join(Args.inputslides, "timetable.txt")

    SlideParser(Args.inputslides, Args.timetable, Args.output_dir, Args.fileformat).parse()

    cv2.destroyAllWindows()
