set -a
source .env
set +a

source activate azure_rrag

l1=$(tr -dc 'a-zA-Z' < /dev/urandom | head -c 1)
l2=$(tr -dc 'a-zA-Z' < /dev/urandom | head -c 1)
l3=$(tr -dc 'a-zA-Z' < /dev/urandom | head -c 1)

random_letter="${l1}${l2}${l3}"


for i in {1..1}
do

    echo "Product: $i"
    time python -u ./src/generate_product.py "$random_letter" || 0
done
 