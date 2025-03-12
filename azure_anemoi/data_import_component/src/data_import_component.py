import xarray as xr
import fsspec

import argparse
import dask
import os

import requests
import zarr
import io
from siphon.catalog import TDSCatalog

print("Loading job script.")

def main():
    """Main function of the script."""

    print("Parsing parameters....")
    # input and output arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=str)
    parser.add_argument("--output_dir", type=str)
    parser.add_argument("--output_zarr", type=str)
    args = parser.parse_args()

    #tmp_dir = f"{args.output_dir}/tmp"
    #os.makedirs(tmp_dir)

    #os.environ["TMPDIR"] = tmp_dir

    print(f"Loading data from source: {args.source}")

    # with dask.config.set(temporary_directory=tmp_dir):
    #zarr_path = "https://data.nssl.noaa.gov/thredds/catalog/PARR/PARR/2024/essoar.172574503.30734251/v1/dataset_10min_15min_init/2021/wrfwof_2021-04-06_191500_to_2021-04-06_212500__10min__ens_mem_09.zarr/"
    zarr_path = args.source

    catUrl = "https://data.nssl.noaa.gov/thredds/catalog/PARR/PARR/2024/essoar.172574503.30734251/v1/dataset_10min_15min_init/2021/wrfwof_2021-04-06_191500_to_2021-04-06_212500__10min__ens_mem_09.zarr/COMPOSITE_REFL_10CM/catalog.xml"

    datasetName = "0.0.0"

    catalog = TDSCatalog(catUrl)
    ds = catalog.datasets[datasetName]
    print(ds.name)

    print(list(ds.access_urls))
    dataset = ds.remote_access()
    print(list(dataset.ncattrs()))
    

    #ds = xr.open_dataset(zarr_path)
    # zarr_store = zarr.open_group(
    #         store=zarr_path,
    #         mode='r',
    #         storage_options={'anon': True}
    #         )

    # ds = xr.open_zarr(zarr_store, consolidated=False)
    # output_path = f"{args.output_dir}/{args.output_zarr}"
    # print(f"Saving ZARR to {output_path}")
    
    # ds.to_zarr(output_path)

    # print(f"Done saving ZARR to {output_path}")

    # # URL of the Zarr dataset
    # url = zarr_path

    # # Send a GET request to the URL
    # response = requests.get(url)

    # # Check if the request was successful
    # if response.status_code == 200:
    #     # Load the dataset into a Zarr array
    #     zarr_array = zarr.open(io.BytesIO(response.content), mode='r')
    #     print("Zarr dataset downloaded successfully!")
    #     zarr.save(output_path, zarr_array)
    #     print("Zarr array saved!")
    # else:
    #     print(f"Failed to download dataset. Status code: {response.status_code}")

if __name__ == "__main__":
    main()
    
   