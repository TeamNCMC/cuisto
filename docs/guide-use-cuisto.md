# Using `cuisto`

## Prerequisites checklist
Prior to use `cuisto`, check that you have :

- [x] [installed](main-getting-started.md#installation) `cuisto`
- [x] set up a [QuPath project](guide-qupath-objects.md#qupath-project)
- [x] [detected objects of interest](guide-qupath-objects.md#detect-objects) as Detections in the QuPath project
- [x] made sure Detections are [properly formatted](guide-prepare-qupath.md#detections) : their classification is in the form `object type: marker`
- [x] [added atlas coordinates](guide-prepare-qupath.md#detections) to Detections as measurements called "Atlas_X", "Atlas_Y" and "Atlas_Z" in millimeters (mm) (to plot spatial distributions only)
- [x] [Annotations](guide-prepare-qupath.md#annotations) (regions of interest), either with [ABBA](guide-register-abba.md#export-registration-back-to-qupath) or [custom ones](https://qupath.readthedocs.io/en/stable/docs/starting/annotating.html)
- [x] made sure Annotations are [properly formatted](guide-prepare-qupath.md#detections#annotations), including a classification formatted as `Hemisphere: Name`
- [x] [added measurements](guide-prepare-qupath.md#adding-measurements) to the Annotations. The measurements are [properly formatted](guide-prepare-qupath.md#annotations) : their name is in the form `object type: marker measurement name`
- [x] [exported](guide-prepare-qupath.md#qupath-export) the Annotations and Detections measurements as tables, either as individual files (one file per subject) or following the [directory structure](guide-pipeline.md#directory-structure) if using the [pipeline mode](guide-pipeline.md)

## Usage
### Configuration
Retrieve a copy of the `config_template.toml` file located in the `configs` folder, as well as atlas-related configuration files in the `atlas` folder. Edit them according to your need.

More details about those files are given in the [configuration section](main-configuration-files.md).

### Examples
If the quantification process was done following the full [pipeline guideline](guide-pipeline.md#usage) (including following the [directory structure](guide-pipeline.md#directory-structure)), check [this code snippet](guide-pipeline.md#__codelineno-1-1) or check the demo notebook showcasing a minimal example [here](demo_notebooks/fibers_length_multi.ipynb).

Alternatively, if you have only one data table exported from QuPath (thus one animal), check the [cells quantification](demo_notebooks/cells_distributions.ipynb) or the [fibers coverage](demo_notebooks/fibers_coverage.ipynb) examples.

In the event you have several QuPath project that should be pooled together to average metrics across animals but did not follow the expected [directory structure](guide-pipeline.md#directory-structure), [export](guide-prepare-qupath.md#qupath-export) the annotations measurements tables (and the detections if spatial distributions are of interest) from QuPath. Then, check the [Batch-process animals section](guide-pipeline.md#batch-process-animals) and the example script `batch_process_animal.py` located in the [`examples`](https://github.com/TeamNCMC/cuisto/tree/main/examples) folder.