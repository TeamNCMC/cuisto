# cuisto

[![Python Version](https://img.shields.io/pypi/pyversions/cuisto.svg)](https://pypi.org/project/cuisto)
[![PyPI](https://img.shields.io/pypi/v/cuisto.svg)](https://pypi.org/project/cuisto/)
[![Tests](https://img.shields.io/github/actions/workflow/status/TeamNCMC/cuisto/python-publish.yml)](https://github.com/TeamNCMC/cuisto/actions/workflows/python-publish.yml)

Python package for histological quantification of objects in reference atlas regions.

`cuisto` uses data exported from [QuPath](https://qupath.github.io) used with [ABBA](https://abba-documentation.readthedocs.io/en/latest/) to pool data and derive, average and display metrics.

![Graphs generated with cuisto](docs/images/cuisto-showcase.svg)

Check the full documentation : [https://teamncmc.github.io/cuisto](https://teamncmc.github.io/cuisto)

## Install
Steps 1-3 below need to be performed only once. If Anaconda or conda is already installed, skip steps 1-2 and use the Anaconda prompt instead.
1. Install [Miniforge](https://conda-forge.org/download/), as user, add conda to PATH and make it the default interpreter.
2. Open a terminal (PowerShell in Windows). run : `conda init` and restart the terminal.
3. Create a virtual environment named "cuisto-env" with Python 3.12 :
    ```bash
    conda create -n cuisto-env python=3.12
    ```
4. Activate the environment :
    ```bash
    conda activate cuisto-env
    ```
5. Install `cuisto` :
    ```bash
    pip install cuisto
    ```
6. (Optional) Download the latest release from [here](https://github.com/TeamNCMC/cuisto/releases/latest) (choose "Source code (zip)) and unzip it on your computer. You can copy the `scripts/` folder to get access to the QuPath and Python scripts. You can check the notebooks in `docs/demo_notebooks` as well !

The `cuisto` package will be then available in Python from anywhere as long as the `cuisto-env` conda environment is activated. You can get started by looking and using the [Jupyter notebooks](#using-notebooks).

For more detailed installation instructions, see the [documentation](https://teamncmc.github.io/cuisto/guide-installation.html).

### Update
To update, simply activate your environment (`conda activate cuisto-env`) and run :
```bash
pip install cuisto --upgrade
```

## Usage
See the [Quick start](https://teamncmc.github.io/cuisto/main-quick-start.html) section in the documentation.

## Using notebooks
Some Jupyter notebooks are available in the [`docs/demo_notebooks`](https://github.com/TeamNCMC/cuisto/tree/main/docs/demo_notebooks) folder. You can open them in an IDE (such as [vscode](https://code.visualstudio.com/) with the Jupyter extension, select the "cuisto-env" environment as kernel in the top right) or in the Jupyter web interface (`jupyter notebook` in the terminal, with the "cuisto-env" environment activated).

## Brain structures
You can generate brain structures outlines coordinates in three projections (coronal, sagittal, top-view) with the [`cuisto.atlas`](https://teamncmc.github.io/cuisto/api-atlas.html) module (see usage example [here](https://teamncmc.github.io/cuisto/tips-brain-contours.html)). They are used to overlay brain regions outlines in 2D projection density maps. It requires a lot of RAM to generate them and might take a while. Those files have been pre-generated for some atlases, they are available in the separate [brain-structures](https://github.com/TeamNCMC/brain-structures) repository. They are automatically downloaded (if available) before plotting.

## Build the doc
To build and look at the documentation offline :
Download the repository, extract it and from the command line in the `cuisto-main` folder, run :
```bash
pip install .[doc]
```
Then, run :
```
mkdocs serve
```
Head to [http://localhost:8000/](http://localhost:8000/) from a web browser.
The documentation is built with [MkDocs](https://www.mkdocs.org/) using the [Material theme](https://squidfunk.github.io/mkdocs-material/). [KaTeX](https://katex.org/) CSS and fonts are embedded instead of using a CDN, and are under a [MIT license](https://opensource.org/license/MIT).

## Contributing
See [Contributing](CONTRIBUTING.md).

## Credits
`cuisto` has been primarly developed by [Guillaume Le Goc](https://legoc.fr) in [Julien Bouvier's lab](https://www.bouvier-lab.com/) at [NeuroPSI](https://neuropsi.cnrs.fr/). The clever name was found by Aurélie Bodeau.
