
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
    parser.add_argument("--task_def", type=str, help="path to task instructions")
    parser.add_argument("--predictions", type=str, help="path to predictions output")
    args = parser.parse_args()

    # Start Logging
    mlflow.start_run()

    task_def = open(args.task_def).read()

    print(f"Task def: {task_def}")

    print(f"Got prompts: {args.prompts}")

    batch_df = pd.read_parquet(args.prompts, engine='pyarrow')

    print("Loaded columns: ", batch_df.columns)

    batch_df = batch_df[["prompt"]]

    batch_df['prompt'] = task_def + batch_df['prompt'].astype(str)

    batch_df = batch_df.head()

    print("Head:")

    print(batch_df.head())

    for i in range(len(batch_df)):
        print(f"Prompt {i}: {batch_df['prompt'][i]}")

    print(f"{args.mlflow_model}")


    model_contents = os.listdir(args.mlflow_model)
    print(f"{model_contents}")

    if "MLmodel" in model_contents:
        print("MLmodel found")

        print(f"{open(f'{args.mlflow_model}/MLmodel').read()}")

    

    model = mlflow.pyfunc.load_model(args.mlflow_model)
    
    print(f"Loaded model object: {model}")
    
    predictions = model.predict(batch_df)

    print(f"Predictions DF: {predictions.columns}")

    print(f"Predictions: {predictions.head()}")

    print(f"Predictions[0]: {predictions[0]}")


    print(f"Predictions[0][0]:\n----------------------------------------\n{predictions[0][0]}\n----------------------------------------\n")

    for i in range(len(predictions[0])):
        print("********************************************************************")
        print(f"Prediction {i}: {predictions[0][i]}")
        print("********************************************************************")

    predictions_df = pd.DataFrame(predictions[0])

    predictions_df.to_csv(args.predictions, index=False, header=False)
    
    mlflow.end_run()

if __name__ == "__main__":
    main()
