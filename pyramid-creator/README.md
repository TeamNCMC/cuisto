# pyramid_creator

[![Python Version](https://img.shields.io/pypi/pyversions/pyramid-creator.svg)](https://pypi.org/project/pyramid-creator)
[![PyPI](https://img.shields.io/pypi/v/pyramid-creator.svg)](https://pypi.org/project/pyramid-creator/)

This script is used to convert regular OME-TIFF files (exported from Zeiss ZEN for example) into pyramidal OME-TIFF ready to use in QuPath (see more information [here](https://teamncmc.github.io/cuisto/guide-create-pyramids.html)).

It uses either QuPath in console mode (eg. without graphical user interface), calling the bundled `createPyramids.groovy` script on each images found in the input directory, or using `tifffile` in Python.

Specify the path to a directory with .ome.tiff files, then the script will create a "pyramidal" subfolder with your pyramidalized images in it.

## Install

### Install `conda`
If not installed already, install [Miniforge](https://conda-forge.org/download/), as user, add to PATH and make it the default interpreter. For more information, you can check [this page](https://teamncmc.github.io/histoquant/main-getting-started.html#python-virtual-environment-manager-conda). Open a terminal, run `conda init` and restart the terminal.

Create a virtual environment (that can be the same than the one for [`cuisto`](https://github.com/TeamNCMC/cuisto) if you plan to use that later on) :
```bash
conda create -n cuisto-env python=3.12
```

### Install `pyramid-creator`
Within a virtual environment with Python 3.12, install with `pip` from the terminal :
```bash
pip install pyramid-creator
```
To enable the Python backend, ask for the required dependencies instead :
```bash
pip install pyramid-creator[python_backend]
```

To use the QuPath backend, a working QuPath installation is required, and the `pyramid-creator` command needs to be aware of its location.

To do so, first, install [QuPath](https://qupath.github.io). By default, it will install in `~\AppData\QuPath-0.X.Y`. In any case, note down the installation location.

Then, you have several options :
- Create a file in your user directory called "QUPATH_PATH" (without extension), containing the full path to the QuPath console executable. In my case, it reads : `C:\Users\glegoc\AppData\Local\QuPath-0.5.1\QuPath-0.5.1 (console).exe`. Then, the `pyramid-creator` script will read this file to find the QuPath executable.
- Specify the QuPath path as an option when calling the command line interface (see the [Usage](#usage) section) :
```bash
pyramid-creator /path/to/your/images --qupath-path "C:\Users\glegoc\AppData\Local\QuPath-0.5.1\QuPath-0.5.1 (console).exe"
```
- Specify the QuPath path as an option when using the package in a Python script (see the [Usage](#usage) section) :
```python
from pyramid_creator import pyramidalize_directory
pyramidalize_directory("/path/to/your/images/", qupath_path="C:\Users\glegoc\AppData\Local\QuPath-0.5.1\QuPath-0.5.1 (console).exe")
```
- If you're using Windows, using QuPath v0.6.0, v0.5.1 or v0.5.0 and chose the default installation location, `pyramid-creator` *should* find it automatically and write it down in the "QUPATH_PATH" file by itself.

## Usage
### As a command line interface (CLI)
From a terminal within the virtual environment in which you installed `videocutter`, you can check the default values with :
```bash
pyramid-creator --help
```
Then, here are some examples of usage :
- Pyramidalize all .ome.tiff files found in a directory, using default values (therefore using QuPath backend)
```bash
pyramid-creator /path/to/your/images
```
- Change the tile size
```bash
pyramid-creator /path/to/your/images --tile-size 1024
```
- Specify the path to a custom groovy script. The latter should take exactly the same number of arguments as `pyramid-creator/scripts/createPyramids.groovy`
```bash
pyramid-creator /path/to/your/images --script-path /path/to/your/custom/script.groovy
```
- Use the Python backend instead of QuPath :
```bash
pyramid-creator /path/to/your/images --no-use-qupath
```

### From a Python script
Copy the example from `examples/create_pyramids.py`, fill in the parameters and run the script.

## Credits
`pyramid-creator` is basically a wrapper around [QuPath](https://qupath.github.io) or [tifffile](https://github.com/cgohlke/tifffile) for the Python backend.
