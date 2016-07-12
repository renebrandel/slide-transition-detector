import pyocr
import pyocr.builders
import subprocess
import mediaoutput
import imgprocessor
import ui
import argparse
import sources
import codecs
import tempfile
import os

from slides import SlideDataHelper
from slides import convert_to_PIL
from analyzer import Analyzer

FNULL = open(os.devnull, 'w')

def temp_file(suffix):
    ''' Returns a temporary file '''
    return tempfile.NamedTemporaryFile(prefix='tess_', suffix=suffix)

class ContentExtractor(Analyzer):

    def __init__(self, source, output_dir, lang="eng"):
        self.source = source
        self.output_dir = output_dir
        self.recognizer = pyocr.get_available_tools()[0]
        self.lang = lang
        mediaoutput.setup_dirs(self.output_dir)

    def analyze(self):
        progress = ui.ProgressController('Extracting Content: ', len(self.source))
        progress.start()

        processors = imgprocessor.ImageProcessQueue()
        processors.add(imgprocessor.GrayscaleProcessor())
        count = 0
        for slide in self.source.contents():
            progress.update(count)
            count += 1
            self.extract(slide, processors, count)
        progress.finish()

    def extract(self, slide, processors, count):
        processed = processors.apply(slide.img)
        processed = convert_to_PIL(processed)
        image = temp_file('.bmp')
        processed.save(image)
        subprocess.call(['tesseract', '-l', self.lang, image.name, os.path.join(self.output_dir, '%d' % count), 'hocr'], stdout=FNULL, stderr=subprocess.STDOUT)
        subprocess.call(['tesseract', '-l', self.lang, image.name, os.path.join(self.output_dir, '%d' % count)], stdout=FNULL, stderr=subprocess.STDOUT)
        return slide

if __name__ == "__main__":
    Parser = argparse.ArgumentParser(description="Slide Sorter")
    Parser.add_argument("-d", "--inputslides", help="path of the sequentially sorted slides", default="unique/")
    Parser.add_argument("-o", "--outpath", help="path to output the content of the slides", default="contents/", nargs='?')
    Parser.add_argument("-l", "--lang", help="language to be analyzed", default="eng", nargs='?')
    Args = Parser.parse_args()
    ContentExtractor(sources.ListSource(SlideDataHelper(Args.inputslides).get_slides()), Args.outpath, lang=Args.lang).analyze()

