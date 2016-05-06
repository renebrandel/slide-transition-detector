import cv2
import os
import numpy as np


def sort(dir):
    slides = []
    for filename in sorted(os.listdir(dir)):
        file_path = os.path.join(dir, filename)
        _, ext = os.path.splitext(file_path)
        if not file_supported(ext):
            continue
        slide = Slide(filename, cv2.imread(file_path))
        slides.append(slide)

    for i in xrange(len(slides)):
        slide = slides[i]
        for j in xrange(i, len(slides)):
            other = slides[j]
            if slide == other:
                continue

            if are_same(slide.img, other.img):
                #slides.remove(other)
                print slide.name, other.name


class Slide(object):
    def __init__(self, name, img):
        self.name = name
        self.img = img




def are_same(fst, snd):
    res = cv2.absdiff(fst, snd)
    hist = cv2.calcHist([res], [0], None, [256], [0, 256])
    similarity = 1 - np.sum(hist[15::]) / np.sum(hist)
    if similarity > 0.995:
        return True
    return False


def file_supported(ext):
    return ext == '.jpeg' or ext == '.png' or ext == '.jpg' or ext == '.bmp'

if __name__ == '__main__':
    sort('slides')