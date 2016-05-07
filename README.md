# slide-transition-detector

This Python script will analyze a video stream of a presentation and output the presentation slides. Furthermore, it will also use OCR to detect contents on the slide for further processing.
This project can be roughly broken down into 3 consecutive pipeline processes. 

|**Process**|Slide Detection|Slide Grouping|Content Extraction|
|---|:---:|:---:|:---:|
|**Input**|Video of presentation|Slides in sequencial order|Slides in logical order w/ timestamp| 
|**Output**|Slides in sequencial order|Slides in logical order w/ timestamp|Slides and their contents|

* Slide Detection (works good for simple use cases)
 * It detects the different slides consectutively and outputs each slide as its own image. One slide that is shown at two different times will generate two images.
* Slide Sorting/Grouping (works roughly)
 * It will take the output of the first process and group the same slides together and generate an additional document showing the timestamp of which slide is shown when.
* OCR (not started)

## Requirements
You will need to install OpenCV 3.1.0, OpenCV Contributions 3.1.0, Numpy and ProgressBar library.
### Setup
#### OpenCV
#### OpenCV Contributions
#### Numpy
`pip install numpy`
#### ProgressBar
`pip install progressbar`

## Usage
### Slide Detection
#### Example:
The slide-transition-detector takes the `[input_file]` and outputs all the slides in the `slides/` directory:

`python detector.py -d [input_file]`

The cleanup tool will be used to remove any file from a previous session before the beginnig of a new slide detection session.

### Slide Sorting
#### Example:

### Cleanup
To clean up all the files generated from the script call

`python cleanup.py`

It will delete all the files in `img/`, `matches/` and `slides/`
