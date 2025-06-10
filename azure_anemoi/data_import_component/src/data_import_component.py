"""Utility script that writes a subset of a reference Zarr archive to disk.

The output directory path must be provided as the first command line argument. If
no argument is supplied the script exits with a usage message.
"""

import sys
import xarray as xr


def main() -> None:
    """Export a single time slice of the sample dataset to the given Zarr path."""

    if len(sys.argv) < 2:
        print("Usage: python data_import_component.py <output_zarr_path>")
        sys.exit(1)

    output_zarr = sys.argv[1]

    ds = xr.open_zarr(
        "https://storage.googleapis.com/noaa-ufs-gefsv13replay/ufs-hr1/0.25-degree/03h-freq/zarr/fv3.zarr/"
    )
    ds_small = ds.sel(time="2023-01-01T00:00")

    ds_small.to_zarr(output_zarr)


if __name__ == "__main__":
    main()
