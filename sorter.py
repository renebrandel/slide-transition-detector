import cv2
import os
import mediaoutput
import imgcomparison


def sort(dir):
    mediaoutput.setup_dirs('unique/')
    slides = []
    for filename in sorted(os.listdir(dir)):
        file_path = os.path.join(dir, filename)
        _, ext = os.path.splitext(file_path)
        if not file_supported(ext):
            continue
        slide = Slide(filename, cv2.imread(file_path))
        slides.append(slide)

    comparator = imgcomparison.AbsDiffHistComparator(0.99)

    for i in xrange(len(slides)):
        slide = slides[i]
        if slide.marked:
            continue

        for j in xrange(i, len(slides)):
            other = slides[j]
            if slide == other or other.marked:
                continue

            if comparator.are_same(slide.img, other.img):
                slide.add_time(other.time)
                other.marked = True

    unique_slides = filter(lambda x: not x.marked, slides)
    out = mediaoutput.IncrementalImageWriter(prefix='unique/', start=1)
    timetable = open('unique/timetable.txt','w')
    i = 1
    for slide in unique_slides:
        out.write(slide.img)
        x = slide.time
        for com in slide.times:
            x += " " + com
        timetable.write("Slide %d: %s\n" % (i, x))
        i += 1
    timetable.close()


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
    sort('slides')