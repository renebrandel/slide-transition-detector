import pyocr
import pyocr.builders
import mediaoutput
import imgprocessor
import ui
import argparse
import sources

from slides import SlideDataHelper
from slides import convert_to_PIL
from analyzer import Analyzer


class ContentExtractor(Analyzer):

    def __init__(self, source, output_dir, lang="deu"):
        self.source = source
        self.output_dir = output_dir
        self.recognizer = pyocr.get_available_tools()[0]
        self.builder = pyocr.builders.TextBuilder()
        self.lang = lang

    def analyze(self):

        progress = ui.ProgressController('Extracting Content: ', len(self.source))
        progress.start()

        processors = imgprocessor.ImageProcessQueue()
        processors.add(imgprocessor.GreyscaleProcessor())
        count = 0
        for slide in self.source.contents():
            progress.update(count)
            count += 1
            self.extract(slide, processors, count)
        progress.finish()

    def extract(self, slide, processors, count):
        processed = processors.apply(slide)
        processed = convert_to_PIL(processed)
        content = self.recognizer.image_to_string(processed, lang=self.lang, builder=self.builder)
        self.export(content, count)
        return content, slide

    def export(self, content, count):
        mediaoutput.setup_dirs(self.output_dir)
        file = open(self.output_dir + "Slide %d.txt" % count, 'w')
        writer = mediaoutput.TextWriter(file)
        writer.write(content.encode('utf-8'))
        file.close()
        count += 1

if __name__ == "__main__":
    Parser = argparse.ArgumentParser(description="Slide Sorter")
    Parser.add_argument("-d", "--inputslides", help="path of the sequentially sorted slides", default="unique/")
    Parser.add_argument("-o", "--outpath", help="path to output the content of the slides", default="contents/", nargs='?')
    Args = Parser.parse_args()
    ContentExtractor(sources.ListSource(SlideDataHelper(Args.inputslides).get_slides()), Args.outpath).analyze()

