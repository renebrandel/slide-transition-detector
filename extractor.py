import pyocr
import pyocr.builders
from slides import SlideDataHelper


if __name__ == "__main__":

    recognizer = pyocr.get_available_tools()[0]
    contents = []

    slides = SlideDataHelper("unique/", image_type="pil").get_slides()
    for slide in slides:
        txt = recognizer.image_to_string(slide.img, lang="deu", builder=pyocr.builders.TextBuilder())
        contents.append(txt)
    count = 0
    for line in contents:
        print "Slide %d" % count
        print line
        print "--------------------------------------"
        print
        count += 1