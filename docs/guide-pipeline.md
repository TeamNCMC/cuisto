# Pipeline
While you can use QuPath and `cuisto` functionalities as you see fit, there exists a pipeline version of those. It requires a specific structure to store files (so that the different scripts know where to look for data). It also requires that you have detections stored as [geojson](tips-formats.md#json-and-geojson-files) files, which can be achieved using a pixel classifier and further segmentation (see [here](guide-qupath-objects.md#probability-map-segmentation)) for example.

In the event you can't or don't want to follow the pipeline depicted below, but still want to be able to batch-process animals, check the [last section](#batch-process-animals).

## Purpose
This is especially useful to perform quantification for several animals at once, where you'll only need to specify the root directory and the animals identifiers that should be pooled together, instead of having to manually specify each detections and annotations files.

Three main parts are used within the pipeline :

+ [`exportPixelClassifierProbabilities.groovy`](https://github.com/TeamNCMC/cuisto/blob/main/scripts/qupath-utils/segmentation/exportPixelClassifierProbabilities.groovy) to create prediction maps of objects of interest
+ The [`cuisto.segmentation` module](api-segmentation.md) to segment those maps and create [geojson files](tips-formats.md#json-and-geojson-files) to be imported back to QuPath as detections
+ [`pipelineImportExport.groovy`](https://github.com/TeamNCMC/cuisto/blob/main/scripts/qupath-utils/workflow/pipelineImportExport.groovy) to :
    - clear all objects
    - import ABBA regions
    - mirror regions names
    - import geojson detections (from `$folderPrefix$segmentation/$segTag$/geojson`)
    - add measurements to detections
    - add atlas coordinates to detections
    - add hemisphere to detections' parents
    - add regions measurements 
        * count for punctual objects
        * cumulated length for lines objects
    - export detections measurements
        * as CSV for punctual objects
        * as JSON for lines
    - export annotations as CSV

## Directory structure
Following a specific directory structure ensures subsequent scripts and functions can find required files. The good news is that this structure will mostly be created automatically using the segmentation scripts (from QuPath and Python), as long as you stay consistent filling the parameters of each script.
The structure expected by the groovy all-in-one script and `cuisto` batch-process function is the following :

```
some_directory/
    ├──AnimalID0/  
    │   ├── animalid0_qupath/
    │   └── animalid0_segmentation/  
    │       └── segtag/  
    │           ├── annotations/  
    │           ├── detections/  
    │           ├── geojson/  
    │           └── probabilities/  
    ├──AnimalID1/  
    │   ├── animalid1_qupath/
    │   └── animalid1_segmentation/  
    │       └── segtag/  
    │           ├── annotations/  
    │           ├── detections/  
    │           ├── geojson/  
    │           └── probabilities/  
```

!!! info
    Except the root directory and the QuPath project, the rest is automatically created based on the parameters provided in the different scripts. Here's the description of the structure and the requirements :

+ `animalid0` should be a convenient animal identifier.
+ The hierarchy must be followed.
+ The experiment root directory, `AnimalID0`, can be anything but should correspond to one and only one animal.
+ Subsequent `animalid0` should be **lower case**.
+ `animalid0_qupath` can be named as you wish in practice, but should be the QuPath project.
+ `animalid0_segmentation` should be called *exactly* like this -- replacing `animalid0` with the actual animal ID. It will be created automatically with the [`exportPixelClassifierProbabilities.groovy`](https://github.com/TeamNCMC/cuisto/blob/main/scripts/qupath-utils/segmentation/exportPixelClassifierProbabilities.groovy) script.
+ `segtag` corresponds to the type of segmentation (cells, fibers...). It is specified in the [`exportPixelClassifierProbabilities.groovy`](https://github.com/TeamNCMC/cuisto/blob/main/scripts/qupath-utils/segmentation/exportPixelClassifierProbabilities.groovy) script. It could be anything, but to recognize if the objects are polygons (and should be counted per regions) or polylines (and the cumulated length should be measured), there are some hardcoded keywords in the [`cuisto.segmentation` module](api-segmentation.md) and the [`pipelineImportExport.groovy`](https://github.com/TeamNCMC/cuisto/blob/main/scripts/qupath-utils/workflow/pipelineImportExport.groovy) script :
    + Cells-like when you need measurements related to its shape (area, circularity...) : `cells`, `cell`, `polygons`, `polygon`
    + Cells-like when you consider them as punctual : `synapto`, `synaptophysin`, `syngfp`, `boutons`, `points`
    + Fibers-like (polylines) : `fibers`, `fiber`, `axons`, `axon`
+ `annotations` contains the atlas regions measurements as [TSV](tips-formats.md#csv-csv-tsv-files) files.
+ `detections` contains the objects atlas coordinates and measurements as [CSV](tips-formats.md#csv-csv-tsv-files) files (for punctal objects) or [JSON](tips-formats.md#json-and-geojson-files) (for polylines objects).
+ `geojson` contains objects stored as [geojson](tips-formats.md#json-and-geojson-files) files. They could be generated with the pixel classifier prediction map segmentation.
+ `probabilities` contains the prediction maps to be segmented by the [`cuisto.segmentation` module](api-segmentation.md).

!!! tip
    You can see an example minimal directory structure with only annotations stored in [`resources/multi`](https://github.com/TeamNCMC/cuisto/tree/main/resources/multi).

## Usage
!!! tip
    Remember that this is merely an example pipeline, you can shortcut it at any points, as long as you end up with TSV files following the [requirements](guide-prepare-qupath.md#qupath-requirements) for `cuisto`.

1. [Create](guide-qupath-objects.md#qupath-project) a QuPath project.
2. [Register](guide-register-abba.md) your images on an atlas with ABBA and export the registration back to QuPath.
3. [Use](guide-qupath-objects.md#pixel-classifier) a pixel classifier and export the prediction maps with the [`exportPixelClassifierProbabilities.groovy`](https://github.com/TeamNCMC/cuisto/blob/main/scripts/qupath-utils/segmentation/exportPixelClassifierProbabilities.groovy) script. You need to get a pixel classifier or [create one](guide-qupath-objects.md#train-a-model).
4. [Segment](guide-qupath-objects.md#probability-map-segmentation) those maps with the [`segmentation` module](api-segmentation.md) (see [an example](https://github.com/TeamNCMC/cuisto/blob/main/examples/segment_images.py)) to generate the [geojson files](tips-formats.md#json-and-geojson-files) containing the objects of interest.
5. [Run](tips-qupath.md#custom-scripts) the [`pipelineImportExport.groovy`](https://github.com/TeamNCMC/cuisto/blob/main/scripts/qupath-utils/workflow/pipelineImportExport.groovy) script on your QuPath project.
6. Set up your [configuration files](main-configuration-files.md).
7. Then, analysing your data with any number of animals should be as easy as executing those lines in Python (either from IPython directly or in a script to easily run it later) :

```python linenums="1"
import cuisto

# Parameters
wdir = "/path/to/some_directory"
animals = ["AnimalID0", "AnimalID1"]
config_file = "/path/to/your/config.toml"
output_format = "h5"  # to save the quantification values as hdf5 file

# Processing
cfg = cuisto.Config(config_file)
df_regions, dfs_distributions, df_coordinates = cuisto.process.process_animals(
    wdir, animals, cfg, out_fmt=output_format
)

# Display
cuisto.display.plot_regions(df_regions, cfg)
cuisto.display.plot_1D_distributions(dfs_distributions, cfg, df_coordinates=df_coordinates)
cuisto.display.plot_2D_distributions(df_coordinates, cfg)
```

!!! tip
    You can see a live example in [this demo notebook](demo_notebooks/fibers_length_multi.ipynb).

## Batch-process animals
It is still possible to process several subjects at once without using the directory structure specified [above](#directory-structure). The [`cuisto.process.process_animals()`](api-process.md#cuisto.process.process_animals) (plural) method is merely a wrapper around [`cuisto.process.process_animal()`](api-process.md#cuisto.process.process_animal) (singular). The former fetch the data from the expected locations, the latter is where the analysis actually happens. Therefore, it is possible to fetch your data yourself and feed it to `process_animal()`.

For example, say you used the QuPath `Measure > Export measurements` for each of your animals. For each individual, this builds a single file with all your images. Let's collect those individual files in a single directory called "results", and name the files in a consistent manner that allows you to identify "Annotations" and "Detections", as well as the animal identifier, for instance "animal0_annotations.tsv".

!!! important
    The [configuration file](main-configuration-files.md#configtoml) is mandatory, even for single-animal analysis.

The script [`batch_process_animals.py`](https://github.com/TeamNCMC/cuisto/blob/main/examples/batch_process_animals.py) located in the [examples](https://github.com/TeamNCMC/cuisto/tree/main/examples) will mimick `process_animals()` functionnality.

??? example "Click to show the file"

    ```python title="batch_process_animals.py" linenums="1"
    --8<-- "examples/batch_process_animals.py"
    ```