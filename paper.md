---
title: "cuisto: A Python package to quantify histological data from QuPath and ABBA"
tags:
  - Python
  - histology
  - immunochemistry
  - image
  - processing
  - neuroscience
authors:
  - name:
      given-names: Guillaume
      surname: Le Goc
    orcid: 0000-0002-6946-1142
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

Multiple software solutions exist to perform image analysis for objects detection, and tools to register 2D slices to 3D reference atlases are also available. The `cuisto` package aims at bridging these pieces of software together to provide a streamlined process, from raw images to quantification figures. It harnesses the output of the bioimage analysis software QuPath [@bankhead2017] used together with the registration toolbox ABBA [@chiaruttini2024]. Designed with users who have minimal programming knowledge in mind, it is configurable and intended to be atlas- and staining-agnostic to cover various use-cases, and provides utility scripts that can be used throughout the analysis pipeline. Furthermore, an extensive documentation is provided, and includes 1) the installation of the various pieces of software used upstream of the `cuisto` package, 2) ABBA and QuPath tutorials, 3) in-depth explanation of the data formatting requirements and 4) hands-on examples with Jupyter notebooks.

# Statement of need
As the task of counting objects in brain regions from fluorescent microscopy images is widespread, several toolboxes were specifically designed for brain-wide mapping. Regrettably however, these toolboxes often lack maintenance and/or community support, as is the case with the QUINT workflow [@yates2019] that relies on several pieces of software (including QuickNII [@puchades2019] and Ilastik [@berg2019]). Furthermore, while it was designed precisely for counting fluorescent objects, it can be rigid at times, making hard to take shortcuts during the workflow and is not interoperable with other computational neuroanatomical tools, notably reference atlases provided by Brainglobe [@claudi2020]. The latter does provide numerous tools to perform brain-wide cell counting [@tyson2021; @tyson2022] but is primarily designed for native 3D data (such as obtained from Light Sheet imaging post clearing). This approach is however not readily accessible to all laboratories and may show variable efficacy depending on the fluorophore used,  the intended resolution or the targeted brain structures.

The QuPath software provides a full-featured, user-friendly interface to perform image quantification while being extensible and scriptable. It is being actively developed and is supported by a vivid community (more than 4k topics tagged with "qupath" on the [image.sc forum](https://forum.image.sc/tag/qupath) and more than 4k citations). The Fiji [@schindelin2012] plugin Aligning Big Brain and Atlases (ABBA) allows for semi-automated registration of whole-brain 2D sections to a 3D atlas in an intuitive and interactive graphical user interface, providing both automatic in-plane registration through elastix [@klein2010] and manual adjustment with BigWarp [@bogovic2016]. It also supports the deep-learning-based automatic registration tool DeepSlice [@carey2023] and can be interfaced with Brainglobe atlases. Furthermore, it integrates seamlessly with QuPath, to both import images and export back the registration results as annotations in QuPath for further quantification.

Yet, to our knowledge, no streamlined pipeline existed to bridge those two pieces of software. The present work is two-fold :

1. Provide step-by-step guides to install and use QuPath and ABBA to quantify and format data in the scope of objects counting in a reference brain, providing automation scripts where necessary.
2. Provide a downstream Python package to use the raw counting data exported from QuPath to summarize and display derived metrics with minimal coding knowledge while being modular enough to fit more advanced users' needs.

Specifically, guides are provided to align 2D histological slices to volumetric reference atlases with ABBA, detect objects of interest in QuPath, quantify those in the registered atlas regions (either object counting for punctual objects or cumulated length for fibers-like objects), format the data to be used by `cuisto` and finally export the data as tabular data (or json files for fibers-like objects).

Subsequently, `cuisto` is used to collect the data from different subjects, pool them based on the atlas regions names and derive quantifying metrics from the raw count or cumulated length. Those metrics include, for each atlas region :

- the raw measurement,
- the areal density, e.g. the raw measurement divided by  the region area,
- the relative density, e.g. the areal density as a fraction of the total density.

Furthermore, `cuisto` leverages the atlas coordinates of each object of interest to compute and display spatial distributions in the reference atlas space.

`cuisto` processing and display is configured with human-readable configuration files that support up to two hemispheres and any number of detection channels to be able to compare different biological markers. Ultimately, this package aims to be versatile : while it was designed around Brainglobe atlases, those are not mandatory and the user can use it with custom annotated regions instead -- as long as the format requirements are met.

It is worth mentioning that BraiAn [@chiaruttini2024], a toolbox following a similar purpose, was released during the development of the present work, but also provides a Java API for the QuPath side, while `cuisto` provides simpler, standalone QuPath scripts.

# Acknowledgements
We would like to thank the original author of QuPath, Peter Bankhead and all contributors. We also thank the original author of ABBA, Nicolas Chiaruttini, especially for his support on ABBA-Python. We thank all contributors of the Brainglobe initiative, especially Adam L. Tyson and Alessandro Felder. We're grateful to members of the lab Antoine Lesage, Alexis d'Humières and Patricia del Cerro de Pablo for their early feedbacks. This work was supported by the European Research Council (ERC CoG 101089318) and the Fondation pour la Recherche Médicale (FRM EQU202203014620).

# References