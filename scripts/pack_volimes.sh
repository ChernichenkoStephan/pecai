mkdir temp/volumes
cp -rf deployments/neo4j_conf temp/volumes/
cp -rf deployments/neo4j_data temp/volumes/
cp -rf deployments/neo4j_plugins temp/volumes/
tar -czvf temp/volumes.tar.gz temp/volumes
  
