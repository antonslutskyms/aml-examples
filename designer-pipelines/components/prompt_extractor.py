
# Read all the csvs in the data folder into a pandas dataframe
import glob
import os
import pandas as pd
import argparse
import mlflow
from pathlib import Path

def main():
    """Main function of the script."""

    # input and output arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompts", type=str, help="path to prompts input")
    parser.add_argument("--output", type=str, help="path to output")
    args = parser.parse_args()

    # Start Logging
    mlflow.start_run()


    print("input data:", args.prompts)

    batch_df = pd.read_parquet(args.prompts, engine='pyarrow')

    print(batch_df.head())

    batch_df = batch_df["prompt"][:10]

    #batch_input_file = "batch_input.csv"

    batch_input_file = f"{args.output}/batch_input.csv"

    batch_df.to_csv(batch_input_file, header=False, index=False)

    print(f"Saved prompts to {batch_input_file}.")

    mlflow.end_run()

if __name__ == "__main__":
    main()
