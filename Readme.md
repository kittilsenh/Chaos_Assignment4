minikube start

minikube -p minikube docker-env | Invoke-Expression

docker build -t myflaskapp:latest . 

cd k8s 

kubectl apply -f deployment.yaml

kubectl apply -f service.yaml

kubectl create deployment myflaskapp --image=myflaskapp:latest

kubectl expose deployment myflaskapp --type=NodePort=5000

minikube service myflaskapp-service

# In the program use bankcard "4242 4242 4242 4242"