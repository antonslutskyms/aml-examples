FROM mcr.microsoft.com/azureml/curated/acpt-pytorch-1.13-cuda11.7:latest
#FROM mcr.microsoft.com/azureml/curated/acpt-pytorch-2.2-cuda12.1:latest

RUN git clone --recurse-submodules https://github.com/microsoft/TRELLIS.git
# WORKDIR /TRELLIS

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 -y

COPY setup.sh /

RUN /setup.sh

# RUN . ./setup.sh --new-env --basic --xformers --flash-attn --diffoctreerast --spconv --mipgaussian --kaolin --nvdiffrast

