import os
import sys
import random
import warnings
import numpy as np
import torch
from neuralforecast import NeuralForecast, DistributedConfig
from neuralforecast.models import NBEATS, PatchTST
from neuralforecast.utils import AirPassengersDF


# Suppress all warnings globally
warnings.filterwarnings('ignore')

input_df = AirPassengersDF


#define model hyperparameters and models
model_hyperparams = {'h': 12,
                     'input_size': 24,
                     'max_steps': 100,
                     'enable_progress_bar': True,
                     }

models = [PatchTST(**model_hyperparams)]

# define the model to create an instance of NeuralForecast
nf = NeuralForecast(models = models, freq = "M", local_scaler_type = 'standard')

dist_cfg = DistributedConfig(
    partitions_path=f'./partitions',
    num_nodes=1,
    devices=4,
)

# Train the model
nf.fit(df=input_df, distributed_config=dist_cfg)