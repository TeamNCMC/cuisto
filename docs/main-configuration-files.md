# The configuration files

There are three configuration files : `altas_blacklist`, `atlas_fusion` and a modality-specific file, that we'll call `config` in this document. The former two are related to the atlas you're using, the latter is what is used by `cuisto` to know what and how to compute and display things. There is a fourth, optional, file used to provide some information on a specific experiment, `info`.

The configuration files are in the TOML file format, that are basically text files formatted in a way that is easy to parse in Python. See [here](tips-formats.md#toml-toml-files) for a basic explanation of the syntax.

Most lines of each template file are commented to explain what each parameter do.

## config.toml
??? abstract "Click to see an example file"
    ```toml title="config_template.toml"
    --8<-- "configs/config_template.toml"
    ```
This file is used to configure `cuisto` behavior. It specifies what to compute, how, and display parameters such as colors associated to each classifications, hemisphere names, distributions bins limits...

Keep in mind the [QuPath requirements](guide-prepare-qupath.md#qupath-requirements) : 

- Only one `object type`, any number of `markers` (channels).
- Annotations have a *Name* `region name`, and a *Classification* `Hemisphere: region name` where "Hemisphere" is either "Left" or "Right".
- Annotations measurements are in the form `object type: marker measurement name`.
- Detections have *Classifications* in the form `object type: marker`.
- Detections have atlas coordinates as measurements called "Atlas_X", "Atlas_Y", "Atlas_Z". "Atlas_Y" always corresponds to the dorso-ventral axis. For ABBA atlas (eg. "Allen Brain Atlas V3p1" in ABBA used from Fiji), "Atlas_X" and "Atlas_Z" are the rostro-caudal and medio-lateral axis, respectively. For Brainglobe altases (eg. "allen_mouse_10um" or any other Brainglobe atlas in ABBA used from Python), "Atlas_X" and "Atlas_Z" are the medio-lateral and rostro-caudal axis, respectively.

!!! warning
    When editing your config.toml file, you're allowed to modify the *keys* **only** in the `[channels]` section.

The template file is thoroughly commented to explain what each line does. Nevertheless, additional information for some of the parameters is provided below.

??? tips
    "marker" and "channel" are used interchangeably but in the configuration file, "channel" is used.
    ### `[atlas]` section
    - `name` corresponds to the exact name of the Brainglobe atlas that was used for registration (check the full list [here](https://brainglobe.info/documentation/brainglobe-atlasapi/usage/atlas-details.html#available-atlases)). If the regular "Allen Brain Atlas V3p1" atlas was used in ABBA-Fiji, choose "allen_mouse_10um". It can be left empty to use `cuisto` with custom Annotations, in that case, atlas-related features will be disabled (see for instance the [fusion configuration file](#atlas_fusiontoml)).
    - `type` depends on the type of atlas used, see more information on [this page](tips-abba.md#cuisto-configuration).

    ### `[channels]` section
    This configures channels names, eg. biological markers and detection channels. This is the only place you can change the keys.

    - `[channels.names]` maps the names of the markers in QuPath (`marker`) to a name displayed in the graphs.
    - `[channels.colors]` maps the names of the markers in QuPath (`marker`) to a color displayed in the graphs.

    ### `[hemispheres]` section
    Same as the `[channels]` section, but the "Left" and "Right" keys are hardcoded an cannot be modified.

    ### `[distributions]` and `[regions]` sections
    Those two sections configure how to compute and plot normalized spatial distributions (pdf) and metrics by regions derived from the base measurement in QuPath (typically count or cumulated length).  
    They rely on the concept of hue used in [seaborn](https://seaborn.pydata.org/tutorial/color_palettes.html#vary-hue-to-distinguish-categories), the Python library used to plot the results. In most plots, there are two axes, 'X' and 'Y', that could be for instance 'Region names' and 'Object count'. A third dimension can be shown using different colors, or *hue*, that can either color data given their `channel` (or marker) or `hemisphere`.

    - `hue` may only be "channel" or "hemisphere".
    - `hue_filter` applies either to "channel" or "hemisphere", given `hue` :
        - if `hue = "channel"` : `hue_filter` can be a hemisphere name (as written in `[hemispheres.names]`) or "both" to use data pooled from both hemispheres. Only the selected data will be used.
        - if `hue = "hemisphere"` : `hue_filter` can be a channel name (as written in `[channels.names]`), "all" to use data pooled from all channels or a list of channel names. Only the selected data will be used.

    #### `[distributions]` section
    - `common_norm` : whether to use a global normalization for all `hue`. This results in the sum of the areas under each individual curves being equal to 1. Alternatively, each curve is normalized independently.

    #### `[regions]` section
    - `base_measurement` : matches exactly the name of the measurement in QuPath Annotations (`measurement name` above) from which metrics are derived.
    - `[regions.metrics]` : the keys cannot be changed, but the names that appear on the graph can. Given the units in which `base_measurement` is expressed, the derived metric (for instance `base_measurement` / area) can have different name and units.
    - `nregions` : only the regions with the highest metrics will be displayed.
    - `order` : "max" or "ontology". "ontology" requires an atlas, the regions are sorted given the ontology (for example the Allen brain sorts regions in the rostro-caudal direction). "max" sorts the regions by descending values. Choose the later to be able to override the order with the `names_list` argument of the [`cuisto.display.plot_regions()`](api-display.md#cuisto.display.plot_regions) method.
        

??? example "Click for a more readable parameters explanation"
    --8<-- "docs/api-config-config.md"

You can check supplementary configuration file examples in the [`resources`](https://github.com/TeamNCMC/cuisto/tree/main/resources) folder, that are ones used in the [examples](main-using-notebooks.md).

## atlas_blacklist.toml
??? abstract "Click to see an example file"
    ```toml title="atlas_blacklist.toml"
    --8<-- "atlas/atlas_blacklist.toml"
    ```
This file is used to filter out specified regions and objects belonging to them.

+ The atlas regions present in the `members` keys will be ignored. Objects whose parents are in here will be ignored as well.
+ In the `[WITH_CHILDS]` section, regions and objects belonging to those regions **and** all descending regions (child regions, as per the altas hierarchy) will be removed.
+ In the `[EXACT]` section, only regions and objects belonging to those **exact** regions are removed. Descendants regions are not taken into account.

## atlas_fusion.toml
??? abstract "Click to see an example file"
    ```toml title="atlas_blacklist.toml"
    --8<-- "atlas/atlas_fusion.toml"
    ```
This file is used to group regions together, to customize the atlas hierarchy. It is particularly useful to group smalls brain regions that are impossible to register precisely.
Keys `name`, `acronym` and `members` should belong to a `[section]`.

+ `[section]` is just for organizing, the name does not matter but should be unique.
+ `name` should be a human-readable name for your new region.
+ `acronym` is how the region will be refered to. It can be a new acronym, or an existing one.
+ `members` is a list of acronyms of atlas regions that should be part of the new one.

Note that the fusion will happen *after* filtering out the data. By default, when using an atlas, `cuisto` will remove any annotations that are *not* leaf regions, eg. only regions without children will be kept for analysis. This is because in most of the atlases, leaf regions pave all the image : parent regions exist merely to group leaf regions in coarser ensemble. Merging regions happens after this filter, thus, even if the new regions have names that are not in the original atlas ontology, they will be kept.

## info.toml
??? abstract "Click to see an example file"
    ```toml title="info_template.toml"
    --8<-- "configs/infos_template.toml"
    ```
This file is used to specify injection sites for each animal and each channel, to display it in distributions.
