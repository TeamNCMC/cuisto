This file might no be up to date nor complete. Please check the Releases page for more information on versions.

## Version 2025.05.16
- Moved the `segment_images.py` script into the `cuisto.segmentation` module
- Moved the atlas structures outlines generation script into the `cuisto.atlas` module
- THe `cuisto.atlas` can download pre-generated outlines
- Outlines drawing can be disabled by setting 'structures' to an empty array

## Version 2024.12.19
- Renamed the package to cuisto (because histoquant is already the name of a commercial software).

## Version 2024.12.10
- Fixed offset writing geojson file in segmentation module.
- Added original_pixelsize parameters to rescale coordinates to match final image size. This allows the use of QuPath pixel classifier trained on resized image, eg. with a lower Resolution parameter (higher pixel size).

## Version 2024.11.19
- Initial public release.