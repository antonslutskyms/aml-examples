FROM mcr.microsoft.com/azureml/curated/acpt-pytorch-2.2-cuda12.1:30
#FROM mcr.microsoft.com/azureml/curated/acpt-pytorch-2.2-cuda12.1:7
#FROM mcr.microsoft.com/azureml/curated/acpt-pytorch-1.13-cuda11.7:latest

# Install pip dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir

# Inference requirements
COPY --from=mcr.microsoft.com/azureml/o16n-base/python-assets:20230419.v1 /artifacts /var/
RUN /var/requirements/install_system_requirements.sh && \
    cp /var/configuration/rsyslog.conf /etc/rsyslog.conf && \
    cp /var/configuration/nginx.conf /etc/nginx/sites-available/app && \
    ln -sf /etc/nginx/sites-available/app /etc/nginx/sites-enabled/app && \
    rm -f /etc/nginx/sites-enabled/default
ENV SVDIR=/var/runit
ENV WORKER_TIMEOUT=400
ENV AZUREML_ARTIFACTS_DEFAULT_TIMEOUT=3600
RUN echo "AZUREML_ARTIFACTS_DEFAULT_TIMEOUT is set to $AZUREML_ARTIFACTS_DEFAULT_TIMEOUT"
EXPOSE 5001 8883 8888

# support Deepspeed launcher requirement of passwordless ssh login
RUN apt-get update
RUN apt-get install -y openssh-server openssh-client

RUN pip install -q anemoi-inference[huggingface]==0.4.3 anemoi-models==0.2.1
RUN pip install -q earthkit-regrid==0.3.4 ecmwf-opendata
RUN pip install -q flash_attn
RUN pip install -q cartopy