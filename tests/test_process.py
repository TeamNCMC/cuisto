from pathlib import Path

import pandas as pd
import pytest

from cuisto import config, process


@pytest.fixture
def cells_res_regions():
    return load_results("cells_df_regions.tsv")


@pytest.fixture
def cells_res_distributions():
    return [
        load_results("cells_df_distribution_" + name + ".tsv")
        for name in ("AP", "DV", "ML")
    ]


@pytest.fixture
def cells_res_coordinates():
    return load_results("cells_df_coordinates.tsv")


@pytest.fixture
def cells_annotations():
    return load_data("cells_measurements_annotations.tsv")


@pytest.fixture
def cells_detections():
    return load_data("cells_measurements_detections.tsv")


@pytest.fixture
def cells_config():
    config_file = Path(__file__).parent.parent / "resources" / "test_config_cells.toml"
    return config.Config(config_file)


@pytest.fixture
def fibers_res_regions():
    return load_results("fibers_multi_df_regions.tsv")


@pytest.fixture
def fibers_config():
    config_file = Path(__file__).parent.parent / "resources" / "test_config_multi.toml"
    return config.Config(config_file)


@pytest.fixture
def cells_animalid():
    return "animalid0"


def load_results(fname: str):
    filename = Path(__file__).parent.parent / "resources" / "results" / fname
    return pd.read_csv(filename, sep="\t")


def load_data(fname: str):
    filename = Path(__file__).parent.parent / "resources" / fname
    return pd.read_csv(filename, index_col="Object ID", sep="\t")


def test_process_animal(
    cells_annotations,
    cells_detections,
    cells_res_regions,
    cells_res_distributions,
    cells_res_coordinates,
    cells_config,
    cells_animalid,
):
    cells_detections[["Atlas_X", "Atlas_Y", "Atlas_Z"]] = cells_detections[
        ["Atlas_X", "Atlas_Y", "Atlas_Z"]
    ].multiply(1000)
    df_regions, dfs_distributions, df_coordinates = process.process_animal(
        cells_animalid,
        cells_annotations,
        cells_detections,
        cells_config,
        compute_distributions=True,
    )

    pd.testing.assert_frame_equal(
        df_regions.reset_index(drop=True), cells_res_regions, check_dtype=False
    )
    for df, res in zip(dfs_distributions, cells_res_distributions):
        pd.testing.assert_frame_equal(df.reset_index(drop=True), res, check_dtype=False)
    pd.testing.assert_frame_equal(
        df_coordinates.reset_index(drop=True), cells_res_coordinates, check_dtype=False
    )


def test_process_animals(fibers_res_regions, fibers_config):
    animals = ["mouse0", "mouse1"]
    wdir = Path(__file__).parent.parent / "resources" / "multi"

    df_regions, _, _ = process.process_animals(
        wdir, animals, fibers_config, compute_distributions=False
    )

    pd.testing.assert_frame_equal(
        df_regions.reset_index(drop=True), fibers_res_regions, check_dtype=False
    )
