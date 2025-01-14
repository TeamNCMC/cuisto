# Image pre-processing

Preparing slides before image acquisition can be a tedious task : it happens that some slices are flipped (either upside-down or left/right), put too close from each other (resulting in a part of a different slice being visible in an image), too close from the slide edge...
In such cases, one might need to clean the image so that only the actual slice is visible in the image.

## Pre-processing scripts
Two scripts are provided in `scripts/preprocessing` to this end. They require first to export the images from the microscope software to standard image files with metadata (eg. [OME-TIFF](tips-formats.md#metadata) files).

The process is then :

1. Split each channel in single-channel images,
1. Detect automatically the brain contour in the specified target channel,
1. Save the resulting brain mask as an image,
1. Apply the mask to all channels and save resulting cleaned images,
1. Review manually the masks, if not satisfied, manually edit the correspond single-channel image in ImageJ,
1. Rerun the brain contour detection and re-apply the masks to all channels,
1. Merge cleaned channels in a multi-channel, pyramidal OME-TIFF image ready to be used in QuPath.

The first script, `preprocess_split_channels.py` handles steps 1-6, `preprocess_merge_channel.py` takes care of the last step.

!!! info
    The reason we need to split channels is to get images that can be easily openned in a third-party software such as ImageJ for conveninent editing.

## Usage
First and foremost, export the images from the microscope software to OME-TIFF. For Zeiss ZEN, have a look at [this guide](guide-create-pyramids.md#export-czi-to-ome-tiff). Say the images were exported to a directory called `~/input_directory/`.

### Split channels and find brain mask
Copy the script `preprocess_split_channels.py` located in `scripts/preprocessing` on your computer. Read the options at the top of the script and edit according to your need.

Especially, the `TASKS` dictionnary what actions are to be performed.

This script will :

1. (if `move=True`) Move images from `~/input_directory` to `~/images/merged_original/`. The files will be renamed depending on the options set in the script header. The `IN_PREFIX` parameter allows the slice number to be parsed. The `OUT_PREFIX` is the prefix of the renamed image and all subsequent use.

    ??? Example
        ZEN exported images named : `A1A4_s1.ome.tiff`, `A1A4_s2.ome.tiff`, ...  
        Setting `IN_PREFIX` to `"_s"` and `OUT_PREFIX` to `animalid_` will result in image being moved from `~/input_directory/animalid_s1.ome.tiff` to `~/images/animalid_001.ome.tiff`, and so on. The `images` folder name is customizable but will always be in the parent directory of `input_drectory`.

2. (if `split=True`) While moving and renaming the image, it will also read the actual image data, and split each channel in separate single-channel images. The image files will have the same name and are stored in `~/ch01`, `~/ch02`... folders.
3. (if `clean=True`) The parameter `DETECTION_CHANNEL` sets which channel will be used to find the brain contour. The corresponding single-channel file is read, [brain detection](#brain-contour-detection) is performed, the resulting mask is saved in `~images/masks`. Since the image is already loaded, the mask is also applied directly to it, and the cleaned, masked image is saved in `~/images/chXX_cleaned`, where `XX` corresponds to `DETECTION_CHANNEL`.

    ??? Info
        If the mask image file already exists, the image is skipped. Likewise, if `overwrite_cleaned` is turned off (eg. set to `False`), if an image with the same name already exist in the `chXX_cleaned` folders, it will be skipped.

4. The mask is subsequently applied to all other channels in the same manner : cleaned images have the same name as the renamed original file, and stored in their respective `chXX_cleaned` folders.
5. Visually assess the quality of the masks stored in `~/images/masks/`. Previews are generated in the `previews` folder. If they are satisfactory, skip to the [next section](#merge-channels).

If for some images the mask is not satisfactory, note down their names and :

1. Delete the mask file (not the preview !).
2. Detele the corresponding cleaned images in each channel.
3. Open ImageJ, drag & drop the corresponding single-channel original image from the channel used for detection.
4. Manually edit it so that the brain slice is easily detected. This means deleting the bits not part of the slice, usually when those bits are close to the slice itself. One could for instance use the `Freehand selections` tool, select the parts to remove and hit ++del++.
5. Save the image (++ctrl+s++), overwritting the original.
6. Repeat for each un-satisfactory mask.
7. Back to the script, turn off `reformat` and `split` in `TASKS`, since that's already done. Only the missing masks will be computed, and only the missing images from the `chXX_cleaned` folders will be written (unless `overwrite_cleaned` is set to `True`).

??? Example
    Automatic brain contour detection failed for `animalid_012.tiff`.  
    I delete `~/images/masks/animalid_012.tiff`. I also delete `~/images/ch01_cleaned/animalid_012.tiff`, `~/images/ch02_cleaned/animalid_012.tiff` and `~/images/ch03_cleaned/animalid_012.tiff`.  
    I drag & drop `~/images/ch01/animalid_012.tiff` in ImageJ, draw the brain contour manually with Freehand selections tool, invert the selection, hit ++del++, save the image, overwritting it.  
    Finally, I edit the script, setting `reformat=False` and `split=False` in `TASKS`, and re-run the script. Only one mask will be computed and applied.

Now, we only have to merge all the channels back to single pyramidal OME-TIFF images ready to be used in QuPath.

### Merge channels
Copy the `preprocess_merge_channels.py` script on your computer.

This one is more straighfoward :

1. Fill the input directory. This is where the script can find each `chXX_cleaned` folders, `~/images/` in the example above.
2. Fill the output directory. This could be for instance `~/images/merged_cleaned/`.
3. Fill the `CHANNELS` parameters. This is a dictionnary, setting the name and color of each channel. The order is important, it needs to be sorted as the `chXX_cleaned` folders are.

    ??? Example
        The first channel (`ch01_cleaned`) corresponds to the NISSL staining imaged in the CFP channel, the second channel (`ch02_cleaned`) corresponds to the EGFP channel. `CHANNELS` would then look like : `{"CFP": (0, 0, 255), "EGFP": (0, 255, 0)}`.

4. Fill the pyramids and tiles options. The default value should work fine for most use cases.
5. Run the script. Images in `OUTPUT_DIRECTORY` are ready to be added to a QuPath project !

!!! danger Important
    The pixel size is read from the OME-TIFF files and propagated along the pre-processing steps until the final images, so make sure it is correct when exporting the files from the microscope software.

### Brain contour detection
The algorithm to detect the brain contour is defined in the function `find_brain_mask()` in the `preprocess_split_channels.py` script. All the parameters are customizable in the `DETECTION_PARAMETERS` variable.
In a nutshell :

1. Zeroes are replaced with a fixed background value (`bkg`). This is to account when manually removing parts in ImageJ, the image background will be high compared to the 0 induced by this operation and edge detection will be sub-optimal.
2. The image is downsampled (`downscale`) for performance -- the full resolution is not needed.
3. Edge filter with the Canny algorithm (using `cannysigma` and `cannythresh`), implemented in [scikit-image](https://scikit-image.org/docs/stable/api/skimage.feature.html#skimage.feature.canny).
4. Morphological closing (dilation followed by erosion) to keep only "big" objects, using `closeradius`.
5. Fill the holes.
6. Keep only the biggest remaining object.
7. Resize the mask to the original image resolution.

