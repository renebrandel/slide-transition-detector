import argparse
import imgcomparison as ic
import imgprocessor as ip

from levenshtein import ls
from slides import SlideDataHelper
from slides import numericalSort

class Evaluator(object):
    def __init__(self, source, reference):
        assert len(source) > 0
        assert len(reference) > 0
        processor = ip.GrayscaleProcessor()
        self.source = map(lambda x: processor.process(x.img), SlideDataHelper(source).get_slides())
        self.reference = map(lambda x: processor.process(x.img), SlideDataHelper(reference).get_slides())
    
    def compare(self):
        lev_dist = ls(self.source, self.reference, ic.AbsDiffHistComparator(0.99).are_same)
        ser = lev_dist / float(len(self.reference))

        print("levenshtein distance: %d" % lev_dist)
        print("slide error rate: %0.4f" % ser)
        
        return ser

if __name__ == "__main__":
    Parser = argparse.ArgumentParser(description="Evaluator")
    Parser.add_argument("-d", "--sourceslides", help="slides that needs to be evaluated", default="slides/", nargs='+')
    Parser.add_argument("-r", "--reference", help="reference slides that should be the proper outcome", nargs='+')
    Args = Parser.parse_args()
    
    assert len(Args.sourceslides) == len(Args.reference)
    evaluations = zip(sorted(Args.sourceslides, key=numericalSort), sorted(Args.reference, key=numericalSort))
    results = []
    for (source, ref) in evaluations:
        print source, ref, ":"
        evaluator = Evaluator(source, ref)
        results.append(evaluator.compare())
        
    print(sum(results) / float(len(results)))
