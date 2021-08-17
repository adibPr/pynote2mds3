# pynote2mds3

[pynote2mds3](https://github.com/adibPr/pynote2mds3) is a script to convert a python notebook into a markdown, but with local image and generated image being uploaded to S3. The original goal is to use jupyter notebook as a tool to writing my blog, wh$

## Installation

1. Download/clone the repo
2. Install with: ```python setup.py install```

## Usage

First, you need to create a configuration file. It just a .ini file with your AWS or other S3 compactible access information. You can find the example configuration on config.sample.ini. Put this file in `~/.config/pynote2mds3/config.ini`.Then you are ready to go. 

To convert a notebook, run `pynote2mds3 notes.ipynb`.
Check the `pynote2mds3 --help` for more information.

## License
[MIT](https://choosealicense.com/licenses/mit/)
