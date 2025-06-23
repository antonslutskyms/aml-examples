# 3D Objects Workflow

This directory demonstrates a generative AI pipeline that creates simple 3D objects with Azure Machine Learning.
The workflow is split into several components that can be run independently or orchestrated together.

## Folder Overview

- **agents/** – Notebook and scripts that chain the steps using Semantic Kernel agents.
- **idea_gen/** – Command component that uses Azure OpenAI to generate a short object idea from a text prompt.
- **image_gen/** – Creates an image of the idea with DALL‑E via Azure OpenAI.
- **text_to_3d/** – Converts the generated image into 3D assets using the Trellis pipeline. Contains a Dockerfile and setup scripts for GPU compute.

## Running the Sample

1. Install the [AzureML CLI v2](https://learn.microsoft.com/azure/machine-learning/how-to-configure-cli) and log in with `az login`.
2. Provision a workspace and a GPU compute cluster.
3. Submit each job with the provided YAML files:
   ```bash
   az ml job create -f idea_gen/idea_gen_job.yaml
   az ml job create -f image_gen/image_gen_job.yaml
   az ml job create -f text_to_3d/3d_object_inference_job.yaml
   ```
4. Check the output directory from the `text_to_3d` step for generated `.glb`, `.ply` and video files.

The `agents` folder shows how to automate the end-to-end flow so that a single notebook can generate ideas, images and corresponding 3D models.

## Requirements

- Access to Azure OpenAI for text and image generation.
- A GPU VM size for the 3D inference step (the Trellis model).

