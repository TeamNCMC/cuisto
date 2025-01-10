# Prepare QuPath data

## QuPath basics
`cuisto` uses some QuPath classifications concepts, make sure to be familiar with them with the [official documentation](https://qupath.readthedocs.io/en/stable/docs/concepts/classifications.html#classifications-derived-classifications). Notably, we use the concept of primary classification and derived classification : an object classified as `First: second` is of classification `First` and of derived classification `second`.

In a nutshell, QuPath has two main objects type, Annotations and Detections. The former are flexible, editable and can be easily moved around but are memory-intensive so they are not made to handle thousands of them. They are used to define regions of interest such as brain regions - ABBA imports registered brain regions as Annotations. On the other hand, Detections objects are optimized so that a single image can contain thousands of them without any problem, at the expense of being harder to modify (they can't be moved nor removed from the GUI). Those are used for objects of interest (the things you want to count, cells, fibers...).

Both types have an *Object ID* (an unique identifier), a *Name*, a *Classification* and a *Parent*. Those are strings, eg. letters and words. Then comes any number of numeric measurements that can have arbitrary names (that could be the area, length, count...).

!!! info
    QuPath Annotations include dynamic measurements, eg. measurement that are updated live, such as "Num Detections" and so on. Those can be handy but are not used downstream with `cuisto` - you will need to add your own count with specific measurement names so that it can work with `cuisto`, see [below](#adding-measurements).

## QuPath requirements
`cuisto` assumes a specific way of storing regions and objects information in the TSV files exported from QuPath. Note that only one primary classification is supported, but you can have any number of derived classifications.

### Annotations
Annotations correspond to the regions of interest, typically the brain regions. They are used to count objects of interest (Detections) within each of them in QuPath, then with `cuisto` to compute and display the measurement (or a derived metric such as the density) per region.
They usually are created importing the registration with the ABBA plugin from the QuPath "Extension" menu or with the `importAbba.groovy` script located in `scripts/qupath-utils/atlas`, but can also be drawn manually, imported from ImageJ ROIs (see the `importImageJRois.groovy` script in `scripts/qupath-utils/tools`) or any other methods, as long as the following requirements are met (note that the *Name* and *Classification* are already correctly set when using the ABBA plugin) :

+ The *Name* should be the atlas acronym, unless you are not using any atlas. In any case, regions are pooled across images and animals based on their *Name* (eg. all Annotations, from all images and all subjects, with the same *Name* are pooled together).
+ The *Classification* must be in the form `Hemisphere: Name`, where `Hemisphere` must be either "Left" or "Right". Even in the case where "Left" and "Right" do not make sense for you, "Left" and "Right" are used internally by `cuisto` to be able to distinguish the two hemispheres. Note that those can be renamed in the display parameters of the [configuration file](main-configuration-files.md#configtoml). `Name` must correspond to the actual Annotation *Name*.
!!! tip
    There are some Groovy scripts in `scripts/qupath-utils/tools` showing how to manipulate Annotations' *Name* and *Classification* to make them suitable for `cuisto` when using custom Annotations (eg. not from ABBA).

+ Measurements names should be formatted as :  
`object type: marker measurement name`. `measurement name` is the bit you will report in the [configuration file](main-configuration-files.md#configtoml) as `base_measurement` under the `[regions]` section.
For instance :  
    + if one has *cells* with *some marker* and *count* them in each atlas regions, the measurement name would be :  
    `Cells: some marker Count`.
    + if one segments *fibers* revealed in the *EGFP* channel and measures the cumulated *length* in µm in each atlas regions, the measurement name would be :  
`Fibers: EGFP Length µm`.  
    Any number of markers or channels is supported but only one `object type`.

### Detections
Detections are the objects of interest. They are used in QuPath to count them in each regions, and can be used with `cuisto` to compute and display the spatial distrubutions based on the atlas coordinates.

The measurement you're interested in (count, cumulated fiber length...) will be added to the Annotations objects (brain regions). In order to get the measurement properly formatted (eg. with the correct measurement name so that it is compatible with `cuisto`, see [above](#annotations)), Detections objects need to respect the following :

+ The *Classification* must be a derived classification formatted like so : `object type: marker`. It can't have column other than the one separating the primary classification (`object type`) and the secondary classification (`marker`). `object type` corresponds to the type of objects of interested that are counted (eg. "Cells", "Fibers", ...), `marker` corresponds to a biological marker or a detection channel (eg. "EGFP", "positive", "marker1+", ...).
+ Only one primary classification can be analyzed at once with `cuisto`, eg. only objects classified as `object type: ...` will be taken into account. Examples : `Cells: marker 1` and `Cells: marker 2`, or `Fibers: EGFP` and `Fibers: DsRed`.

Those information are used to perform the quantification in each Annotation within QuPath. `cuisto` can use only the Annotations data afterwards if you're only interested in the quantification in each regions. However, if you also want the spatial distributions of the objects in the atlas space, Detections objects will also need :

+ The atlas coordinates, stored as `Atlas_X`, `Atlas_Y` and `Atlas_Z`, expressed in millimetres (mm). They correspond for the Allen Brain atlas, respectively, to the anterio-posterior (rostro-caudal) axis, the inferio-superior (dorso-ventral) axis and the left-right (medio-lateral) axis. You can add those coordinates to the Detections as a measurement with the `addAtlasCoordinates.groovy` script located in `scripts/qupath-utils/atlas`.

## Measurements

### Metrics supported by `cuisto`
While you're free to add any measurements as long as they follow [the requirements](#qupath-requirements), keep in mind that for atlas regions quantification, `cuisto` will only compute, pool and average the following metrics :

- the base measurement itself
    - if "µm" is contained in the measurement name, it will also be converted to mm (\(\div\)1000)
- the base measurement divided by the region area in µm² (density in something/µm²)
- the base measurement divided by the region area in mm² (density in something/mm²)
- the squared base measurement divided by the region area in µm² (could be an index, in weird units...)
- the relative base measurement : the base measurement divided by the total base measurement across all regions *in each hemisphere*
- the relative density : density divided by total density across all regions *in each hemisphere*

It is then up to you to select which metrics among those to compute and display and name them, via the [configuration file](main-configuration-files.md#configtoml).

For punctual detections (eg. objects whose only the centroid is considered), only the atlas coordinates are used, to compute and display spatial distributions of objects across the brain (using their classifications to give each distributions different hues).  
For fibers-like objects, it requires to export the lines detections atlas coordinates as JSON files, with the `exportFibersAtlasCoordinates.groovy` script (this is done automatically when using the [pipeline](guide-pipeline.md)).

### Adding measurements
#### Count for cell-like objects
The groovy script under `scripts/qupath-utils/measurements/addRegionsCount.groovy` will add a properly formatted count of objects of selected classifications in all atlas regions. This is used for punctual objects (polygons or points), for example objects created in QuPath or with the [segmentation script](api-script-segment.md).

#### Cumulated length for fibers-like objects
The groovy script under `scripts/qupath-utils/measurements/addRegionsLength.groovy` will add the properly formatted cumulated lenghth in microns of fibers-like objects in all atlas regions. This is used for polylines objects, for example generated with the [segmentation script](api-script-segment.md).

#### Custom measurements
Keeping in mind [`cuisto` limitations](#metrics-supported-by-cuisto), you can add any measurements you'd like.

For example, you can run a [pixel classifier](https://qupath.readthedocs.io/en/stable/docs/tutorials/pixel_classification.html) in all annotations (eg. atlas regions). Using the `Measure` button, it will add a measurement of [the area covered by classified pixels](https://qupath.readthedocs.io/en/stable/docs/tutorials/measuring_areas.html#generating-results) (see [here](guide-qupath-objects.md#measure)). Then, you can use the script located under `scripts/qupath-utils/measurements/renameMeasurements.groovy` to rename the generated measurements with a [properly-formatted name](#annotations). Finally, you can [export](#qupath-export) regions measurements.

Since `cuisto` will compute a "density", eg. the measurement divided by the region area, in this case, it will correspond to the fraction of surface occupied by classified pixels. This is showcased in the [Examples](demo_notebooks/fibers_coverage.ipynb).

## QuPath export
Once you imported atlas regions registered with ABBA, detected objects in your images and added [properly formatted](#qupath-requirements) measurements to detections and annotations, you can : 

+ Head to `Measure > Export measurements`
+ Select relevant images
+ Choose the `Output file` (specify in the file name if it is a detections or annotations file)
+ Choose either `Detections` or `Annoations` in `Export type`
+ Click `Export`

Do this for both Detections and Annotations, you can then use those files with `cuisto` (see the [Examples](main-using-notebooks.md)).

Alternatively, if using QuPath as intended for the [pipeline](guide-pipeline.md), the final script `pipelineImportExport.groovy` will automatically export the data, following the [file structure](guide-pipeline.md#directory-structure) expected by `cuisto` used in "pipeline mode", eg. to easily analyse several animals at once (to do so without using the pipeline, check [this section](guide-pipeline.md#batch-process-animals)).