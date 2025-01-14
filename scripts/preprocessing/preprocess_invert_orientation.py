"""
Simple script to change the order of files.

Used to transform file names (xxx_001.tiff) to reverse their order, eg.
for a 30 image stack, xxx_001.tiff becomes xxx_030.tiff, xxx_030.tiff becomes
xxx_001.tiff, and so on.

"""

import os

import numpy as np

input_directory = "/path/to/directory"  # path to tiff files
output_directory = "/path/to/directory/new"  # output directory, must be different
file_extension = ".ome.tiff"  # file extension with dots
file_prefix = "animal0_"  # full prefix before the numbering digits
ndigits = 3  # number of digits for numbering (both inputs and outputs)
dry_run = True  # if True, do not actually rename the files

# list available files
list_files = [
    filename
    for filename in os.listdir(input_directory)
    if filename.startswith(file_prefix) & filename.endswith(file_extension)
]

# count files
nfiles = len(list_files)
# reverse indices
new_numbers = np.arange(nfiles, 0, -1)

# create output directory if necessary
if not os.path.isdir(output_directory):
    os.mkdir(output_directory)

# loop over images, build new name and rename
for oldi, newi in enumerate(new_numbers):
    old_name = f"{file_prefix}{str(oldi + 1).zfill(ndigits)}{file_extension}"
    new_name = f"{file_prefix}{str(newi).zfill(ndigits)}{file_extension}"
    old_file = os.path.join(input_directory, old_name)
    new_file = os.path.join(output_directory, new_name)

    print(f"rename: {old_name} -> {new_name}")
    if not dry_run:
        os.rename(old_file, new_file)
