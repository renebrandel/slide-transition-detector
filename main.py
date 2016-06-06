import argparse
import imgcomparison as ic

from sources import AnalyzerSource
from detector import Detector
from sorter import SlideSorter
from extractor import ContentExtractor

if __name__ == "__main__":

    Parser = argparse.ArgumentParser(description="Slide Detector")
    Parser.add_argument("-d", "--device", help="video device number or path to video file")
    Parser.add_argument("-o", "--outpath", help="path to output video file", default="slides/", nargs='?')
    Parser.add_argument("-f", "--fileformat", help="file format of the output images e.g. '.jpg'",
                        default=".jpg", nargs='?')
    Parser.add_argument("-t", "--timetable",
                        help="path where the timetable should be written (default is the outpath+'timetable.txt')",
                        nargs='?', default=None)
    Args = Parser.parse_args()

    detector = Detector(Args.device, Args.outpath, Args.fileformat)
    sorter = SlideSorter(AnalyzerSource(detector), ic.AbsDiffHistComparator(0.99), "unique/", "unique/timetable.txt", Args.fileformat)
    extractor = ContentExtractor(AnalyzerSource(sorter), "contents/")
    extractor.analyze()
