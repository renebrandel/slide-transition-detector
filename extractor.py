import pyocr
import pyocr.builders
import slides
import mediaoutput
import imgprocessor

if __name__ == "__main__":

    recognizer = pyocr.get_available_tools()[0]
    contents = []

    slide_list = slides.SlideDataHelper("unique/").get_slides()

    processors = imgprocessor.ImageProcessQueue()
    processors.add(imgprocessor.GreyscaleProcessor())


    for slide in slide_list:
        processed = processors.apply(slide.img)
        processed = slides.convertToPIL(processed)
        txt = recognizer.image_to_string(processed, lang="deu", builder=pyocr.builders.TextBuilder())
        contents.append(txt)
    count = 1

    path = "contents/"
    mediaoutput.setup_dirs(path)

    for line in contents:
        file = open(path + "Slide %d.txt" % count, 'w')
        writer = mediaoutput.TextWriter(file)
        writer.write(line.encode('utf-8'))
        file.close()
        count += 1

