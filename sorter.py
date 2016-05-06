import cv2
import os
import imgcomparison


def sort(dir):
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
            if slide == other:
                continue

            if comparator.are_same(slide.img, other.img):
                if other.marked:
                    slide.marked = True
                other.marked = True
                print slide.name, other.name


class Slide(object):
    def __init__(self, name, img):
        self.name = name
        self.img = img
        self.marked = False


def file_supported(ext):
    return ext == '.jpeg' or ext == '.png' or ext == '.jpg' or ext == '.bmp'

if __name__ == '__main__':
    sort('slides')