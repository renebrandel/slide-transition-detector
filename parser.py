import mediaoutput

from sorter import SlideDataHelper

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
