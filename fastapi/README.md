# How to Push Image to ECR
DO at the Host Machine WSL (Because it needs docker)
```
# Get ECR repository url
ECR_REPOSITORY_URL_WITH_REPONAME=<★change your ecr repository url>
echo $ECR_REPOSITORY_URL_WITH_REPONAME
ECR_REPOSITORY_URL=`echo ${ECR_REPOSITORY_URL_WITH_REPONAME%/*}`
echo $ECR_REPOSITORY_URL

# Docker Client Authentication for ECR
aws ecr get-login-password --region ap-northeast-1 | docker login --username AWS --password-stdin ${ECR_REPOSITORY_URL}

# list local image
docker image ls

# Build
cd fastapi
ls -l

docker build -t ${ECR_REPOSITORY_URL_WITH_REPONAME}:latest .

docker image ls

docker push ${ECR_REPOSITORY_URL_WITH_REPONAME}:latest
```

# Deploy App to EKS
DO at devcontainer

At first, modify fastapi.yml (replace <★change_your_ecr_repository_url>)
```
# Deploy Fast API with ALB
cd fastapi
ls -l

kubectl apply -f fastapi.yml

# Check Ingress and Pod
kubectl get ingress/ingress-fastapi -n fastapi
kubectl get deployment -n fastapi


# CURL Check
API_ENDPOINT_HOSTNAME=<HTTP_URL>
curl -w "code: %{http_code}, speed: %{time_total} sec\n" -o /dev/null -s http://${API_ENDPOINT_HOSTNAME}
curl -w "code: %{http_code}, speed: %{time_total} sec\n" \
  -X POST "http://${API_ENDPOINT_HOSTNAME}/prediction/online" -H "accept: application/json" -H "Content-Type: application/json" \
  -d @test_data.json


# After check to access the application, delete apps
kubectl delete -f fastapi.yml
```


# Delete Image from ECR
```
# Delete
aws ecr list-images \
     --repository-name ml-api-handson

aws ecr batch-delete-image \
     --repository-name ml-api-handson \
     --image-ids imageTag=latest
```
