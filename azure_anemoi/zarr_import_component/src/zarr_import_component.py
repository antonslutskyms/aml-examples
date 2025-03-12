import xarray as xr
import fsspec

import argparse

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

    print(f"Loading data from source: {args.source}")

    ds = xr.open_zarr(fsspec.get_mapper(args.source, anon=True), consolidated=True)
    
    output_path = f"{args.output_dir}/{args.output_zarr}"
    print(f"Saving ZARR to {output_path}")
    
    ds.to_zarr(output_path)

    print(f"Done saving ZARR to {output_path}")

if __name__ == "__main__":
    main()
    
   