import argparse
import cv2
import os
import numpy as np
from matplotlib import pyplot as plt


class ImageWriter:

    def __init__(self, prefix='img ', file_format='.jpg', count=0):
        self.count = count
        if not file_format.startswith('.'):
            file_format = '.' + file_format
        self.name = prefix + '%d' + file_format

    def write_image(self, img):
        cv2.imwrite(self.name % self.count, img)


def sanitize_device(device):
    """returns device id if device can be converted to an integer"""
    try:
        return int(device)
    except (TypeError, ValueError):
        return device


def main(args):
    """Main execution function"""
    setup_dirs()

    # get the video stream
    cap = cv2.VideoCapture(sanitize_device(args.device))

    # setup output video (if needed)
    """
    size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    fps = cap.get(cv2.CAP_PROP_FPS)
    codec = cv2.VideoWriter_fourcc('X', '2', '6', '4')
    out = cv2.VideoWriter(args.outfile, codec, fps, size)
    """

    _, last_frame = cap.read()

    slide_writer = ImageWriter('slides/slide ')
    slide_writer.write_image(last_frame)

    interval_writer = ImageWriter('img/out ')

    i = 0

    while True:

        ret, frame = cap.read()
        if ret:
            if i % 100 == 0:
                # every 100th frame it writes the image to disk
                interval_writer.write_image(frame)
                # out.write(frame) # write video

            if not are_same(last_frame, frame, i):
                slide_writer.write_image(frame)

            i += 1
            last_frame = frame
        else:
            break
    print ('done')

    print i
    cap.release()
    # out.release()
    cv2.destroyAllWindows()


def are_same(fst, snd, count):
    res = cv2.subtract(snd, fst)
    hist = cv2.calcHist([res], [0], None, [256], [0, 256])
    similarity = 1 - np.sum(hist[15::]) / np.sum(hist)
    print count, similarity
    if similarity > 0.99:
        return True
    return False


def setup_dirs():
    if not os.path.exists('img'):
        os.makedirs('img')

    if not os.path.exists('slides'):
        os.makedirs('slides')

    if not os.path.exists('matches'):
        os.makedirs('matches')


if __name__ == "__main__":
    Parser = argparse.ArgumentParser(description="OpenCV Test")
    Parser.add_argument("-d", "--device", help="video device number or path to video file")
    Parser.add_argument("-o", "--outfile", help="path to output video file")
    Args = Parser.parse_args()
    main(Args)
