# Brain contours
With `cuisto`, it is possible to plot 2D heatmaps on brain contours.

All the detections are projected in a single plane, thus it is up to you to select a relevant data range. It is primarily intended to give a quick, qualitative overview of the spreading of your data.

To do so, it requires the brain regions outlines, stored in a hdf5 file. This can be generated with [`brainglobe-atlasapi`](https://brainglobe.info/documentation/brainglobe-atlasapi/index.html#brainglobe-atlas-api-brainglobe-atlasapi). The [`cuisto.atlas`](api-atlas.md) module allows you to do so.

You can generate this file beforehand, using the following code snippet :
```python
from cuisto import atlas
atlas.generate_outlines("allen_mouse_10um", "/path/to/output/file.h5")
```

!!! danger
    Note that while the output file is relatively small (<100MB), it requires a lot of RAM. Make sure to use a powerful workstation (>32GB RAM) to avoid crashing your computer.

The [`cuisto.display`](api-display.md) module can use this file to draw structures outlines projected in three points of view (coronal, sagittal and top-view). The structures drawn are defined in the [configuration file](main-configuration-files.md#configtoml) in the `[atlas]` section. If the `outline_structures` parameter is empty, no outlines will be shown -- this can be used to disable structure contours drawing.

The path to the hdf5 file should be specified in the `[files]` section of the [configuration file](main-configuration-files.md#configtoml).

!!! tip
    If the parameter `outlines` in the `[files]` section is left empty, it will be looked up in the default directory, `$HOME/.cuisto/{atlas_name}_outlines.h5`.
    If the file does not exist, it will be attempted to download it from the [brain-structures](https://github.com/TeamNCMC/brain-structures/) repository, though to date, only `allen_mouse_10um` and `allen_cord_20um` are available. 

Alternatively it is possible to directly plot density maps without `cuisto`, using [`brainglobe-heatmap`](https://brainglobe.info/documentation/brainglobe-heatmap/index.html#brainglobe-heatmap). An example is shown [here](demo_notebooks/density_map.ipynb).