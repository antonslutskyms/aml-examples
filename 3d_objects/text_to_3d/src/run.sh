./setup.sh

source activate trellis

conda env list

cp run.py /TRELLIS

cd /TRELLIS

python run.py "$1" $2