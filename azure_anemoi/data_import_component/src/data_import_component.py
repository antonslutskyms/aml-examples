import xarray as xr
import sys

output_zarr = sys[0]

ds = xr.open_zarr("https://storage.googleapis.com/noaa-ufs-gefsv13replay/ufs-hr1/0.25-degree/03h-freq/zarr/fv3.zarr/")

ds_small = ds.sel(time="2023-01-01T00:00")

ds_small.to_zarr(output_zarr)