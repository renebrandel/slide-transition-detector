import pyocr
import pyocr.builders
import slides
import mediaoutput
import imgprocessor
import ui
import argparse


class ContentExtractor(object):

    def __init__(self, input_dir, output_dir, lang="deu"):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.recognizer = pyocr.get_available_tools()[0]
        self.builder = pyocr.builders.TextBuilder()
        self.lang = lang

    def analyze(self):

        slide_list = slides.SlideDataHelper(self.input_dir).get_slides()

        progress = ui.ProgressController('Extracting Content: ', len(slide_list))
        progress.start()

        processors = imgprocessor.ImageProcessQueue()
        processors.add(imgprocessor.GreyscaleProcessor())
        count = 0
        for slide in slide_list:
            progress.update(count)
            count += 1
            self.extract(slide, processors, count)

        progress.finish()

    def extract(self, slide, processors, count):
        processed = processors.apply(slide.img)
        processed = slides.convert_to_PIL(processed)
        content = self.recognizer.image_to_string(processed, lang=self.lang, builder=self.builder)
        self.export(content, count)

    def export(self, content, count):

        mediaoutput.setup_dirs(self.output_dir)

        file = open(self.output_dir + "Slide %d.txt" % count, 'w')
        writer = mediaoutput.TextWriter(file)
        writer.write(content.encode('utf-8'))
        file.close()
        count += 1

if __name__ == "__main__":
    ContentExtractor("unique/", "contents/").analyze()

