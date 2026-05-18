"""Load distance matrices and subject metadata."""

from pathlib import Path
import pandas as pd


def load_distance_csv(path):
    df = pd.read_csv(path, index_col=0)
    subject_names = list(df.columns)
    return df.values.astype(float), subject_names


def load_distances(dist_dir=None):
    if dist_dir is None:
        dist_dir = Path(__file__).resolve().parent.parent / "results" / "distances"
    dist_dir = Path(dist_dir)

    genetic, names_g = load_distance_csv(dist_dir / "genetic_distance.csv")
    geographic, names_geo = load_distance_csv(dist_dir / "geographic_distance.csv")

    if names_g != names_geo:
        raise ValueError("genetic and geographic matrices use different subject order")

    return genetic, geographic, names_g


def load_subject_metadata(metadata_path=None):
    if metadata_path is None:
        metadata_path = (
            Path(__file__).resolve().parent.parent
            / "DATA"
            / "processed"
            / "samples_metadata_ordered.csv"
        )
    return pd.read_csv(metadata_path)


def align_metadata(subject_names, metadata_df):
    """One row per subject, same order as distance matrix labels."""
    meta = metadata_df.set_index("SGDP_ID")
    rows = meta.loc[subject_names]
    return rows.reset_index()
