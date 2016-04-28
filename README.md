# slide-transition-detector

This Python script will analyze a video stream of a presentation and output the presentation slides.

## Requirements
You will need to install OpenCV 3.1.0 and OpenCV Contributions 3.1.0

## Usage
### Slide Detection
#### Example:
The slide-transition-detector takes the `[input_file]` and outputs all the slides in the `slides/` directory:

`python detector.py -d [input_file]`

### Cleanup
To clean up all the files generated from the script call

`python cleanup.py`

It will delete all the files in `img/`, `matches/` and `slides/`
