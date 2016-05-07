import cv2
import os
import mediaoutput
import imgcomparison


class SlideSorter(object):

    def __init__(self, path, comparator):
        self.comparator = comparator
        self.path = path

    def sort(self):
        mediaoutput.setup_dirs('unique/')

        slides = self.get_slides()
        unique_slides = self.group_slides(slides)

        timetable = open('unique/timetable.txt','w')
        mediaoutput.TimetableWriter(timetable).write(unique_slides)
        timetable.close()

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


def file_supported(ext):
    return ext == '.jpeg' or ext == '.png' or ext == '.jpg' or ext == '.bmp'

if __name__ == '__main__':
    SlideSorter('slides', imgcomparison.AbsDiffHistComparator(0.99)).sort()