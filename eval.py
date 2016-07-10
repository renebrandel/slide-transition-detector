import subprocess
import argparse
import os

png_prefix = 'slide'


def convertToPNG(pdf):
    foldername, _ = os.path.splitext(pdf)
    foldername = os.path.basename(foldername)
    foldername = os.path.join('PNG_Seq', foldername)
    subprocess.call(['mkdir', '-p' ,foldername])
    subprocess.call(['convert', pdf, foldername, os.path.join(foldername, png_prefix + '.png')], shell=False)
    return foldername

def stitch(sequence):
    subprocess.call(['./stitcher.sh', '-p', os.path.join(sequence, 'slide-'), '-f', 'png', '-i', '0', '-o', sequence])

if __name__ == "__main__":
    Parser = argparse.ArgumentParser(description="Evaluation")
    Parser.add_argument("slides", help="PDF files of the slides", nargs='+')
    Args = Parser.parse_args()
    png_sequences = []
    for slide in Args.slides:
        png_sequences.append(convertToPNG(slide))
    for sequence in png_sequences:
        stitch(sequence)

