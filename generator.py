import subprocess
import argparse
import os

from ui import ProgressController as pc
from alignment import Aligner


png_prefix = 'slide'
FNULL = open(os.devnull, 'w')

def convertToPNG(pdf):
    foldername, _ = os.path.splitext(pdf)
    foldername = os.path.basename(foldername)
    foldername = os.path.join('PNG_Seq', foldername)
    subprocess.call(['mkdir', '-p' ,foldername])
    subprocess.call(['convert', pdf, foldername, os.path.join(foldername, png_prefix + '.png')], stdout=FNULL, stderr=subprocess.STDOUT)
    return foldername

def align(folder_desc):
    foldername = os.path.basename(folder_desc)
    foldername = os.path.join('aligned/', foldername)
    outputname = os.path.join(foldername, "")
    aligner = Aligner(folder_desc, outputname, 0.2, [1,5])
    aligner.align_slides()
    return foldername

def stitch(sequence):
    subprocess.call(['./stitcher.sh', '-p', os.path.join(sequence, ''), '-f', 'png', '-i', '0', '-o', sequence], stdout=FNULL, stderr=subprocess.STDOUT)


if __name__ == "__main__":
    Parser = argparse.ArgumentParser(description="Generator")
    Parser.add_argument("slides", help="PDF files of the slides", nargs='+')
    Args = Parser.parse_args()
    progress = pc("Generating Videos", len(Args.slides))
    progress.start() 
    counter = 0
    for slide in Args.slides:
        stitch(align(convertToPNG(slide)))
        counter += 1
        progress.update(counter)
    progress.finish()
