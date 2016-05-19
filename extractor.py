import pyocr
import pyocr.builders
from slides import SlideDataHelper
import mediaoutput

if __name__ == "__main__":

    recognizer = pyocr.get_available_tools()[0]
    contents = []

    slides = SlideDataHelper("unique/", image_type="pil").get_slides()
    for slide in slides:
        txt = recognizer.image_to_string(slide.img, lang="deu", builder=pyocr.builders.TextBuilder())
        contents.append(txt)
    count = 0

    path = "contents/"
    mediaoutput.setup_dirs(path)

    for line in contents:
        file = open(path + "Slide %d.txt" % count, 'w')
        writer = mediaoutput.TextWriter(file)
        writer.write(line.encode('utf-8'))
        file.close()
        count += 1

