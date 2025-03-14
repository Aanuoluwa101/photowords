container_name=lambda_docker 
docker_image=aws_lambda_builder_image 
docker run -td -v private_key.pem:/private_key.pem --name=$container_name $docker_image
docker cp ./requirements.txt $container_name:/

docker exec -i $container_name bin/bash < ./install.sh 
docker cp $container_name:/python.zip python.zip 
docker stop $container_name
docker rm $container_name