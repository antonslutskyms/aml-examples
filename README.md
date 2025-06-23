# AML Examples

This repository contains a collection of standalone samples for Azure Machine Learning (AML). Each folder demonstrates a different workflow, from training traditional models to using generative AI in pipelines. The notebooks and YAML files can be executed individually depending on the scenario you want to try.

## Repository Structure

- **3d_objects** – Generative AI workflow for creating 3D objects. Includes agents for idea generation, image generation, and conversion to STL files.
- **CleanData_and_TuneHyperparams_Example.ipynb** – Notebook showing how to clean data and tune hyperparameters with AML.
- **Hyper_Sweep_CLI_Example.ipynb** – Hyperparameter sweep example that uses the AzureML CLI.
- **Hyperparam_Sweep_Example.ipynb** – Notebook version of running sweeps across many parameters.
- **Job_MAE_Modified_Transforms** – Example job for training a Masked Autoencoder (MAE) with custom transforms.
- **Quota_Requests** – Instructions for requesting additional compute quota. Contains a PDF with the steps.
- **azure_anemoi** – Pipeline for the Anemoi weather model including components and Docker environments.
- **designer-pipelines** – Pipelines built with the AML designer. Provides an LLM scoring pipeline and sample components.
- **neuralforecast** – Demonstrates running the [NeuralForecast](https://github.com/Nixtla/neuralforecast) library on AML.
- **pf** – Prompt flow assets for simple text classification.
- **terraform** – Terraform templates for creating an ML workspace and registry.
- **wofs_example** – Walkthrough for training the WOFS weather forecast model.

Each subfolder may contain its own notebook and job definition files. See the documentation within those directories for details.

## Getting Started

1. Install the [AzureML Python SDK](https://learn.microsoft.com/azure/machine-learning/how-to-configure-python-environment?view=azureml-api-2) and log in with `az login`.
2. Clone this repository and open the example notebook you want to run.
3. Follow the instructions in the notebook or YAML file to submit jobs or create pipelines.

Some examples rely on Dockerfiles or Conda environments in the `environment` directories. Build these images first if required by the notebook.

## Contributing

Samples are provided as-is for learning purposes. Feel free to fork the repository and adapt them to your needs.


