# slide-transition-detector

This Python script will analyze a video stream of a presentation and output the presentation slides. Furthermore, it will also use OCR to detect contents on the slide for further processing.
This project can be roughly broken down into 3 consecutive pipeline processes. 

|**Process**|Slide Detection|Slide Grouping|Content Extraction|
|---|:---:|:---:|:---:|
|**Input**|Video of presentation|Slides in sequencial order|Slides in logical order w/ timestamp| 
|**Output**|Slides in sequencial order|Slides in logical order w/ timestamp|Slides and their contents|

* Slide Detection (works good for simple use cases)
 * It detects the different slides consectutively and outputs each slide as its own image. One slide that is shown at two different times will generate two images.
* Slide Sorting/Grouping (works great)
 * It will take the output of the first process and group the same slides together and generate an additional document (timetable.txt) showing the timestamp of which slide is shown when.
* OCR (minumum viable product available)

## Requirements
You will need to install OpenCV 3.1.0, OpenCV 3.1.0 Contributions, NumPy and ProgressBar library.
### OpenCV

Since the installation process of OpenCV is different from platform to platform, I would recommend checking out the [OpenCV homepage](http://opencv.org)

It is important to note that the contributions packages are required to support different types of encoding.

I personally used the method described in [this tutorial](http://embedonix.com/articles/image-processing/installing-opencv-3-1-0-on-ubuntu/) to install it on my Ubuntu system.

### NumPy
Simply install NumPy using the following command. NumPy is required to evaluate large arrays.
`pip install numpy`
### ProgressBar
`pip install progressbar`
### Tesseract-OCR
`sudo apt-get install libtesseract3 tesseract-ocr tesseract-ocr-[lang]`

More information can be found [here](https://github.com/tesseract-ocr/tesseract)

### PyOCR
PyOCR is a Python Wrapper for the tesseract (Optical Character Recognition) library. This is used in third process in the pipeline.
PyOCR can be installed from [here](https://github.com/jflesch/pyocr).


## Usage
### Slide Detection
#### Command
The slide-transition-detector takes the `[input_file]` and outputs all the slides in the `[output_dir]` directory with the file format specified in `[file_format]`:

`python detector.py -d [input_file] -o [output_dir] -f [file_format]`

The cleanup tool will be used to remove any file from a previous session before the beginnig of a new slide detection session.

#### Defaults
* `[output_dir]`: `slides/`
* `[file_format]`: `.jpg`

### Slide Sorting
It takes the output of the slide detection process and sorts them in the order of appearence. It removes all duplicate slides and the outputs a timetable.txt where the exact timestamp of each appearance time of each slide is shown.

#### Command
The sorter.py will take all images from `[input_dir]` and sort them and export them in `[output_dir]` with `[file_format]` along with the timetable at `[timetable_path]`.

`python sorter.py -d [input_dir] -o [output_dir] -f [file_format] -t [timetable_loc]`

#### Defaults
* `[input_dir]`: `slides/`
* `[output_dir]`: `unique/`
* `[file_format]`: `.jpg`
* `[timetable_loc]`: `[ouput_dir]/timetable.txt`

### Slide Parser
To read the `timetable.txt` you can parse the file as the following:

1. Read the `timetable.txt` line by line.
2. Everything until the first `:` is the name of the slide. After that you can split the rest of the string after the first colon with ` ` (space) as a seperator.
3. Each element from the split is the timestamp of when the specific slide should appear (string trimming required).

#### Command
The Parser reverses the effects of the files written by the sorter into `[input_dir]` and the `[timetable_loc]`. It exports the files into `[output_dir]` with `[file_format`]

`python parser.py -d [input_dir] -t [timetable_loc] -o [output_dir] -f [file_format]`


### Cleanup
To clean up all the files generated from the script call

`python cleanup.py`

It will delete all the files in `img/`, `matches/` and `slides/`
