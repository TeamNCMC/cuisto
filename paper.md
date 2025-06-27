---
title: "cuisto: A Python package to quantify neurohistological data from QuPath and ABBA"
tags:
  - Python
  - histology
  - immunochemistry
  - microscopy
  - image analysis
  - neuroscience
authors:
  - name:
      given-names: Guillaume
      surname: Le Goc
    orcid: 0000-0002-6946-1142
    affiliation: 1
    corresponding: true
  - name: Alexis d'Humières
    orcid: 0009-0006-3860-2084
    affiliation: 1
  - name: Antoine Lesage
    orcid: 0009-0000-7362-3215
    affiliation: 1
  - name: Julien Bouvier
    orcid: 0000-0002-1307-4426
    affiliation: 1
    corresponding: true
affiliations:
  - name: Université Paris-Saclay, CNRS, Institut des Neurosciences Paris-Saclay, 91400, Saclay, France
    index: 1
bibliography: paper.bib
---

# Summary
Fluorescent labeling techniques, including immunohistochemistry and endogenously fluorescent proteins, are key assets in neuroscience. Combined to genetic toolboxes, they enable the anatomical identification of specific neurons and neuronal processes, shedding light on neural networks organization and linking behavior to brain structures. Advances in imaging techniques and numerical tools have enabled the creation of volumetric, annotated, whole-brain atlases of various animal models [@wang2020; @kleven2023; @kunst2019; @lazcano2021] facilitating brain-wide mapping of labeled elements to a reference three-dimensional space. In this framework, a common task is to count, in the reference brain regions, objects of interest (be it whole cells, nuclei, axons, synaptic puncta...) detected in 2D histological slices imaged with fluorescence microscopy.

Multiple software solutions exist to perform image analysis for object detection, and tools to register 2D slices to 3D reference atlases are also available. The `cuisto` package aims at bridging these pieces of software together to provide a streamlined process, from raw images to quantification figures. It harnesses the output of the bioimage analysis software QuPath [@bankhead2017] used together with the registration toolbox ABBA [@chiaruttini2024]. Designed with users who have minimal programming knowledge in mind, it is configurable and intended to be atlas- and staining-agnostic to cover various use-cases, and provides utility scripts that can be used throughout the analysis pipeline. Furthermore, extensive documentation is provided, and includes 1) the installation of the various pieces of software used upstream of the `cuisto` package, 2) ABBA and QuPath tutorials, 3) in-depth explanation of the data formatting requirements and 4) hands-on examples with Python scripts and Jupyter notebooks.

# Statement of need
As the task of counting objects in brain regions from fluorescent microscopy images is widespread, several toolboxes have been developed for brain-wide object quantification such as the QUINT workflow [@yates2019]. The pipeline relies on QuickNII and VisuAlign [@puchades2019] for the registration and Ilastik [@berg2019] for the segmentation. While effective for specific tasks, such as counting punctal objects, its architecture offers limited flexibility, making it hard to take shortcuts during the workflow, and it is not interoperable with other computational neuroanatomical tools, notably reference atlases provided by BrainGlobe [@claudi2020]. The latter does provide numerous tools to perform brain-wide cell counting [@tyson2021; @tyson2022] but is primarily designed for native 3D data (such as obtained from light sheet imaging of optically cleared tissue). This approach is however not readily accessible to all laboratories and may show variable efficacy depending on the fluorophore used, the intended resolution, or the targeted brain structures.

The QuPath software provides a full-featured, user-friendly interface to perform image quantification while being extensible and scriptable. It is being actively developed and is supported by a vibrant community (more than 4k topics tagged with "qupath" on the [image.sc forum](https://forum.image.sc/tag/qupath) and more than 4k citations). This software  supports a variety of segmentation strategies, from basic thresholding to pixel classification and advanced deep learning methods such as CellPose [@stringer2021], StarDist [@schmidt2018] and InstanSeg [@goldsborough2024a]. The Fiji [@schindelin2012] plugin Aligning Big Brain and Atlases (ABBA) allows for semi-automated registration of whole-brain 2D sections to a 3D atlas in an intuitive and interactive graphical user interface using native full-resolution multichannel images, providing both automatic in-plane registration through elastix [@klein2010] and manual adjustment with BigWarp [@bogovic2016]. It also supports the deep-learning-based automatic registration tool DeepSlice [@carey2023] and can be interfaced with BrainGlobe atlases. Furthermore, it integrates seamlessly with QuPath, to both import images and export back the registration results as annotations in QuPath for further quantification.

Yet, to our knowledge, no streamlined pipeline existed to bridge the image processing and registration with the region-based quantification and data visualization. The present work is two-fold:

1. Provide step-by-step guides to install and use QuPath and ABBA to quantify and format data for counting objects in a reference brain, providing automation scripts where necessary.
2. Provide a downstream Python package to use the raw counting data exported from QuPath to summarize and display derived metrics with minimal coding knowledge, while being modular enough to fit more advanced users' needs.

Specifically, guides are provided to align 2D histological slices to volumetric reference atlases with ABBA and detect objects of interest in QuPath. `cuisto` includes an image processing module to segment objects from the prediction maps generated with QuPath’s pixel classifier, supporting punctal objects, polygons, and fibers. Guides further cover how to quantify those in the registered atlas regions (either object counting for punctual objects or cumulative length for fiber-like objects), format the data to be used by `cuisto`, and finally export the results as tabular data (or json files for fiber-like objects).

Subsequently, `cuisto` is used to collect the data from different subjects, pool them based on the atlas region names, and derive quantifying metrics from the raw count or cumulative length. Those metrics include, for each atlas region:

- the raw measurement,
- the areal density, i.e. the raw measurement divided by  the region area,
- the relative density, i.e. the areal density as a fraction of the total density.

Furthermore, `cuisto` leverages the atlas coordinates of each object of interest to compute and display spatial distributions in the reference atlas space. 2D projection heatmaps are also generated and overlaid on the atlas region contours.

`cuisto` processing and display is configured with human-readable configuration files that support up to two hemispheres and any number of detection channels to be able to compare different biological markers. Ultimately, this package aims to be versatile: while it was designed around BrainGlobe atlases, those are not mandatory and the user can use it with custom annotated regions instead — as long as the format requirements are met.

It is worth mentioning that BraiAn [@chiaruttini2025], a toolbox following a similar purpose, was released during the development of the present work, but also provides a Java API for the QuPath side, while `cuisto` provides simpler, standalone QuPath scripts.

The documentation and the examples provide toy data, derived from datasets acquired on mice models. All procedures were approved by the French Ethical Committee (“Comité d’éthique en Expérimentation Animale”, CEEA #59, authorization 2020-022410231878) and conducted in accordance with EU Directive 2010/63/EU.

# Acknowledgements
We would like to thank the original author of QuPath, Peter Bankhead, and all contributors. We also thank the original author of ABBA, Nicolas Chiaruttini, especially for his support on ABBA-Python. We thank all contributors of the BrainGlobe Initiative. We're grateful to member of the lab Patricia del Cerro de Pablo for her early feedback. This work has received funding from the European Research Council (ERC) under the European Union's Horizon Europe research and innovation program (grant agreement No 101089318), the Fondation pour la Recherche Médicale (FRM EQU202203014620 and ECO202206015594), the CNRS and the University Paris-Saclay.

# References
