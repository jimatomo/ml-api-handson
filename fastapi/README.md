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
```

# Taurus API Test

Connect EC2 Instance
```
sudo apt-get update
sudo apt-get install python3 default-jre-headless python3-tk python3-pip python3-dev libxml2-dev libxslt-dev zlib1g-dev net-tools python3-venv

# Venv
python3 -m venv taurus
source ./taurus/bin/activate

# install taurus
pip install --upgrade wheel setuptools Cython
pip install bzt

# set script
# taurus_script.yml
cat << EOF > taurus_script.yml
execution:
- concurrency: 1
  ramp-up: 1s
  hold-for: 1s
  iterations: 30
  scenario: fastapi-test

scenarios:
  fastapi-test:
    timeout: 5s
    retrieve-resources: false
    store-cache: false
    store-cookie: false
    default-address: http://internal-k8s-fastapi-ingressf-f385b3472b-565323687.ap-northeast-1.elb.amazonaws.com # modify
    headers:
      Content-Type: application/json
      accept: application/json
    requests:
    - url: '/prediction/online'
      method: POST
      body:
        data: 
        - PassengerId: "892"
          Pclass: "3"
          Name: "Kelly, Mr. James"
          Sex: "male"
          Age: "34.5"
          SibSp: "0"
          Parch: "0"
          Ticket: "330911"
          Fare: "7.8292"
          Cabin: ""
          Embarked: "Q"

reporting:
- console
- module: final-stats
  summary: true  # overall samples count and percent of failures
  percentiles: true  # display average times and percentiles
  summary-labels: true # provides list of sample labels, status, percentage of completed, avg time and errors
  failed-labels: ture  # provides list of sample labels with failures
  test-duration: true  # provides test duration
  dump-csv: dump-csv_2.csv

EOF

ls -l

# execute script
bzt taurus_script.yml
```


# locust
```
# python3 -m venv locust
source locust/bin/activate
pip install -U pip
pip install locust

locust -f fastapi_test.py \
  --host="http://${API_ENDPOINT_HOSTNAME}/prediction/online"
```


# Delete API
```
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
