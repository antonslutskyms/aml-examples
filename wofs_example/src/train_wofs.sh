cd workflow/model_training

python ../../write_config.py $1 $2 $3        
            
stdbuf -oL python -u train.py --config config.yaml