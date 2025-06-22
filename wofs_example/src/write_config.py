import sys

base_dir = sys.argv[1]
norm_stats_dir = sys.argv[2]
out_path = sys.argv[3]

import yaml

config_dir = "configs/template_configs"

with open(f'{config_dir}/template_train_config.yaml', 'r') as file:
    template_train_config = yaml.safe_load(file)
    template_train_config['norm_stats_path'] = f"{norm_stats_dir}/full_normalization_stats"
    template_train_config['out_path'] = out_path
    template_train_config['data_paths'] = [base_dir]
    
    # Disable WandB 
    template_train_config['use_wandb'] = False
    print(template_train_config)

with open(f'{config_dir}/config.yaml', 'w') as out_file:
    yaml.dump(template_train_config, out_file)