export $(cat ./deployments/.env.plain | xargs)
echo $ENVIROMENT

python3 src/apps/travel.py
