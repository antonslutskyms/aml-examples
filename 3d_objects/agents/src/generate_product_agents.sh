set -a
source .env
set +a

source activate azure_sk_agents

l1=$(tr -dc 'a-zA-Z' < /dev/urandom | head -c 1)
l2=$(tr -dc 'a-zA-Z' < /dev/urandom | head -c 1)
l3=$(tr -dc 'a-zA-Z' < /dev/urandom | head -c 1)

random_letter="${l1}${l2}${l3}"


for i in {1..1}
do

    echo "Product: $i"
    time python -u ./src/agents_manager.py $* "$random_letter" 
done