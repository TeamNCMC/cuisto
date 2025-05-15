# Brain contours
With `cuisto`, it is possible to plot 2D heatmaps on brain contours.

All the detections are projected in a single plane, thus it is up to you to select a relevant data range. It is primarily intended to give a quick, qualitative overview of the spreading of your data.

To do so, it requires the brain regions outlines, stored in a hdf5 file. This can be generated with [`brainglobe-atlasapi`](https://brainglobe.info/documentation/brainglobe-atlasapi/index.html#brainglobe-atlas-api-brainglobe-atlasapi). The [`cuisto.atlas`](api-atlas.md) module allows you to do so.

You can generate this file beforehand, using the following code snippet :
```python
from cuisto import atlas
atlas.generate_outlines("allen_mouse_10um", "/path/to/output/file.h5")
```

!!! info inline end
    If the file `/path/to/output/file.h5` already exists, nothing will happen.

The [`cuisto.display`](api-display.md) module can use this file to draw structures outlines projected in three point of view (coronal, sagittal and top-view). The structures drawn are defined in the [configuration file](main-configuration-files.md#configtoml) in the `[atlas]` section. If no atlas is specified, no outlines will be shown, nor if the `outline_structures` parameter is empty. The latter can be used to disable structure contours drawing.

The path to the hdf5 file should be specified in the `[files]` section of the [configuration file](main-configuration-files.md#configtoml).

!!! tip
    You can download the outline file for :

    - `allen_mouse_10um` here : [https://arcus.neuropsi.cnrs.fr/s/TYX95k4QsBSbxD5](https://arcus.neuropsi.cnrs.fr/s/TYX95k4QsBSbxD5)
    - `allen_cord_20um` here : [https://arcus.neuropsi.cnrs.fr/s/EoAfMkESzJZG74Q](https://arcus.neuropsi.cnrs.fr/s/EoAfMkESzJZG74Q)

Alternatively it is possible to directly plot density maps without `cuisto`, using [`brainglobe-heatmap`](https://brainglobe.info/documentation/brainglobe-heatmap/index.html#brainglobe-heatmap). An example is shown [here](demo_notebooks/density_map.ipynb).