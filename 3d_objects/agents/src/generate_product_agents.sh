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

    project_id=$1

    if [ -z "$project_id" ]; then

        project_id="pro_$(date +'%Y%m%d%H%M%S')"
        echo "Creating new project directory $project_id"
        
    else
        echo "Using existing project: $1"
    fi

    mkdir -p ./output/$project_id

    cd ./output/$project_id

    echo "Product [$i] RID:$random_letter; $project_id"

    time python -u ../../src/agents_manager.py .  
done