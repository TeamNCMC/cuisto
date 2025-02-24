# Contribute 

## Seeking support and report an issue
For `cuisto`-related issues, you can open an issue [here](https://github.com/TeamNCMC/cuisto/issues)
explaining your issue. Please provide as much relevant information as you can, such as platform, Python version, `cuisto` version, data sample and code snippets to help reproduce the issues.

You can also use the Issues to ask questions. We'll try to get back to you as soon as possible.

For QuPath and/or ABBA-related issues and questions, you can find support over at the [image.sc](https://image.sc) forum.

## Contribute

You can contribute a fix or a new feature to this project with the following steps:

1. Create a conda environment with Python 3.12
```bash
conda create -n cuisto-dev python=3.12
```
2. Fork the project on GitHub.
3. Clone the project
```bash
git clone https://github.com/<your-github-username>/cuisto
```
4. Activate the environement and install the package in editable mode, with the development dependencies
```bash
conda activate cuisto-dev
pip install -e .[doc,dev]
```
5. Make a new git branch where you will apply the changes
```bash
git checkout -b your-branch-name
```
6. Make your changes and test them. You can add tests in the `tests` folder and run them with `pytest`. Once done, `git add`, `git commit` and `git push` the changes.
7. Make a Pull Request from your branch to the [cuisto repository](https://github.com/TeamNCMC/cuisto/issues).

## Styleguides
### Python code
Python code should be [PEP8 compliant](https://peps.python.org/pep-0008/). We use [ruff](https://docs.astral.sh/ruff/) with a line length of 88 to format the code.

Docstrings are formatted with the [numpy convention](https://numpydoc.readthedocs.io/en/latest/format.html#docstring-standard).

### Groovy code
We use camelCase for file and variable names. The scripts should contain a docstring with the filename and a short description of what it does. See an [existing example](https://github.com/TeamNCMC/cuisto/blob/main/scripts/qupath-utils/tools/convertAnnotationsToDetections.groovy).

### Documentation
The documentation is written in Markdown, using [mkdocs](https://www.mkdocs.org/) and [mkdocs-material](https://squidfunk.github.io/mkdocs-material/).

See the existing pages to know how to format things, including :

- \`code\` for code snippets, `/file/paths` and `scriptName.groovy`. The latter should contain a backlink to the actual file in the Github repository.
