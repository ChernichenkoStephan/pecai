mkdir temp/deployments
cp -rf deployments/.env temp/deployments
cp -rf deployments/docker-compose.yaml temp/deployments
tar -czvf temp/deployments.tar.gz temp/deployments
