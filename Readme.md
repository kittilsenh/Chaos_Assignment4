minikube start

minikube -p minikube docker-env | Invoke-Expression

docker build -t myflaskapp:latest . 

kubectl create deployment myflaskapp --image=myflaskapp:latest

kubectl expose deployment myflaskapp --type=NodePort=5000

minikube service myflaskapp-service