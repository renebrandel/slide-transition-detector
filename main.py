import argparse
import os.path as p
import sources
from detector import Detector
from sorter import SlideSorter
from extractor import ContentExtractor


def execute(inputfile, extractor_out, detector_out=None, sorter_out=None):
    detector = Detector(inputfile, outpath=detector_out)
    sorter = SlideSorter(sources.ListSource(detector.detect_slides()), outpath=sorter_out)
    extractor = ContentExtractor(sources.ListSource(sorter.sort()), output_dir=extractor_out)
    extractor.analyze()


def batchExecute(inputfiles, extractor_out="contents/", detector_out="detected_slides/", sorter_out="sorted_slides"):
    for file in inputfiles:
        name = p.basename(file)
        extractor = p.join(extractor_out, name) + p.sep
        sorter = p.join(sorter_out, name) + p.sep
        detector = p.join(detector_out, name) + p.sep
        print "Analyzing " + name + ":"
        execute(file, extractor, detector, sorter)
        print

if __name__ == "__main__":

    Parser = argparse.ArgumentParser(description="Slide Detector")
    Parser.add_argument("files", help="video device number or path to video file", nargs='+')
    Args = Parser.parse_args()
    batchExecute(Args.files)
