import argparse
import random

from mediaoutput import IncrementalImageWriter
from slides import SlideDataHelper

class Aligner(object):
    
    def __init__(self, slides_descriptor, output, jump_probability, jump_range):
        self.originals = map(lambda x: x.img, SlideDataHelper(slides_descriptor).get_slides())
        assert len(jump_range) == 2
        assert len(filter(lambda x: x > 0, jump_range)) == 2
        assert jump_range[0] <= jump_range[1]
        assert jump_probability >= 0 and jump_probability <= 1
        self.lower = jump_range[0]
        self.upper = jump_range[1]
        self.threshold = jump_probability
        self.writer = IncrementalImageWriter(prefix=output, file_format="png", start=1) 

    def align_slides(self):
        aligned = []
        for idx, slide in enumerate(self.originals):
            prob = random.random()    
            if prob < self.threshold:
                prefix = self.get_jump_backs(idx)
                if prefix is not None:
                    aligned.append(slide)
                    aligned.extend(prefix)
            aligned.append(slide)
        for slide in aligned:
            self.writer.write(slide)
   
    def get_jump_backs(self, index):
        amount = random.randint(self.lower, self.upper)
        if index == 0 or index - 1 - amount < 0: 
            return None
        backwards = self.originals[index - 1:index - 1 - amount: -1]
        forwards = backwards[::-1][1:]
        backwards.extend(forwards)
        return backwards

if __name__ == "__main__":
    Parser = argparse.ArgumentParser(description="Aligner")
    Parser.add_argument("-d", "--inputslides", help="path of the sequentially sorted slides", default="slides/")
    Parser.add_argument("-l", "--lower", help="lower bound of amounts of slides to jump back", type=int, default="1")
    Parser.add_argument("-u", "--upper", help="lower bound of amounts of slides to jump back", type=int, default="5")
    Parser.add_argument("-t", "--threshold", help="probability that a jump occurs", type=float, default="0.5")
    Parser.add_argument("-o", "--output", help="output directory of the sequences", default="aligned/")
    Args = Parser.parse_args()
    Aligner(Args.inputslides, Args.output, Args.threshold, [Args.lower, Args.upper]).align_slides();
    
