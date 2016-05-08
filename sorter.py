import cv2
import os
import mediaoutput
import imgcomparison
import cleanup


class SlideSorter(object):

    def __init__(self, path, comparator):
        self.comparator = comparator
        self.path = path

    def sort(self):
        mediaoutput.setup_dirs('unique/')

        slides = SlideDataHelper(self.path).get_slides()
        unique_slides = self.group_slides(slides)

        timetable = open('unique/timetable.txt','w')
        mediaoutput.TimetableWriter(timetable).write(unique_slides)
        timetable.close()

    def group_slides(self, slides):
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


class Slide(object):

    def __init__(self, time, img):
        self.time, _ = os.path.splitext(time)
        self.img = img
        self.marked = False
        self.times = []

    def add_time(self, time):
        self.times.append(time)


class SlideParser(object):

    def __init__(self, slides_dir, timetable_path):
        self.timetable_path = timetable_path
        self.slides = SlideDataHelper(slides_dir).get_slides()

    def parse(self):
        writer = mediaoutput.CustomImageWriter('reversed/')
        with open(self.timetable_path) as timetable:
            for line in timetable:
                slide = self.slides.pop(0)
                slide_times = line[line.index(':') + 2:].split(' ')
                #slide_times[-1] = slide_times[-1][:-2] #removing the "\n" in the line
                for time in slide_times:
                    writer.write(slide.img, time)


class SlideDataHelper(object):

    def __init__(self, path):
        self.path = path

    def get_slides(self):
        slides = []
        for filename in sorted(os.listdir(self.path)):
            file_path = os.path.join(self.path, filename)
            _, ext = os.path.splitext(file_path)
            if not file_supported(ext):
                continue
            slide = Slide(filename, cv2.imread(file_path))
            slides.append(slide)

        return slides


def file_supported(ext):
    return ext == '.jpeg' or ext == '.png' or ext == '.jpg' or ext == '.bmp'

if __name__ == '__main__':

    SlideSorter('slides/', imgcomparison.AbsDiffHistComparator(0.99)).sort()
    SlideParser('unique/', 'unique/timetable.txt').parse()