import argparse

from imgcomparison import AbsDiffHistComparator
from levenshtein import fastMemLev
from slides import SlideDataHelper
from ui import ProgressController as pc

class Evaluator(object):
    def __init__(self, source, reference):
        assert len(source) > 0
        assert len(reference) > 0
        self.source = map(lambda x: x.img, SlideDataHelper(source).get_slides())
        self.reference = map(lambda x: x.img, SlideDataHelper(reference).get_slides())
    
    def compare(self):
        lev_dist = fastMemLev(self.source, self.reference, AbsDiffHistComparator(0.99).are_same)
        print(len(self.reference))
        print("levenshtein distance: %d" % lev_dist)
        print("slide error rate: %0.4f" % (lev_dist / float(len(self.reference))))


if __name__ == "__main__":
    Parser = argparse.ArgumentParser(description="Evaluator")
    Parser.add_argument("-d", "--sourceslides", help="slides that needs to be evaluated", default="slides/")
    Parser.add_argument("-r", "--reference", help="reference slides that should be the proper outcome", nargs='?')
    Args = Parser.parse_args()

    evaluator = Evaluator(Args.sourceslides, Args.reference)
    evaluator.compare()
  
