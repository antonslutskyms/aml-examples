
# Read all the csvs in the data folder into a pandas dataframe
import glob
import os
import pandas as pd
import argparse
import mlflow
from pathlib import Path
import torch

def main():
    """Main function of the script."""

    # input and output arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--mlflow_model", type=str, help="mlflow model")
    parser.add_argument("--prompts", type=str, help="path to prompts input")
    parser.add_argument("--predictions", type=str, help="path to predictions output")
    args = parser.parse_args()

    # Start Logging
    mlflow.start_run()



    print(f"Got prompts: {args.prompts}")

    batch_df = pd.read_json(args.prompts, lines=True)

    model = mlflow.pyfunc.load_model(args.mlflow_model)
    
    print(f"Loaded model object: {model}")

    batch_df['input_string'] = batch_df['text'].astype(str)

    batch_df = batch_df[["input_string"]]
    
    predictions = model.predict(batch_df)

    print(f"Predictions DF: {predictions.columns}")

    print(f"Predictions: {predictions.head()}")

    print(f"Predictions[0]: {predictions[0]}")


    print(f"Predictions[0][0]:\n----------------------------------------\n{predictions[0][0]}\n----------------------------------------\n")

    for i in range(len(predictions[0])):
        print("********************************************************************")
        p_clean = predictions[0][i].replace('\n', '')
        print(f"Input String{i}: {batch_df['input_string'][i]}")
        print(f"Prediction {i}: {p_clean}")
        print("********************************************************************")

    predictions_df = pd.DataFrame(predictions[0])
    predictions_df["input_string"] = batch_df["input_string"]

    predictions_df.to_csv(args.predictions, index=False, header=False)
    
    mlflow.end_run()

if __name__ == "__main__":
    main()
