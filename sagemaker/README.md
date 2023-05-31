# Deploy
```
from sagemaker.model import Model
from sagemaker import get_execution_role

# Get SageMaker Execution Role
sagemaker_role = get_execution_role()

# Container Image URI
IMAGE_URI="<account_id>.dkr.ecr.ap-northeast-1.amazonaws.com/byol-ml-model:latest"

# Create Model Object
model = Model(image_uri=IMAGE_URI, 
              role=sagemaker_role)
```

```
# Define Endpoint name
# The name of the endpoint. The name must be unique within an AWS Region in your AWS account. 
from datetime import datetime

endpoint_name = f"DEMO-{datetime.utcnow():%Y-%m-%d-%H%M}"
print("EndpointName =", endpoint_name)
```

```
# Initial Instance Count
initial_instance_count=1

# Instance Type
instance_type='ml.t2.medium'
# instance_type='ml.m4.xlarge' # Example

model.deploy(
    initial_instance_count=initial_instance_count,
    instance_type=instance_type,
    endpoint_name=endpoint_name
)
```

```
import json
# Test Data
test_input_str = '''{
    "data": [
        {
            "PassengerId": 892,
            "Pclass": 3,
            "Name": "Kelly, Mr. James",
            "Sex": "male",
            "Age": 34.5,
            "SibSp": 0,
            "Parch": 0,
            "Ticket": 330911,
            "Fare": 7.8292,
            "Cabin": "",
            "Embarked": "Q"
        },
        {
            "PassengerId": 893,
            "Pclass": 3,
            "Name": "Wilkes, Mrs. James (Ellen Needs)",
            "Sex": "female",
            "Age": 47,
            "SibSp": 1,
            "Parch": 0,
            "Ticket": 363272,
            "Fare": 7,
            "Cabin": "",
            "Embarked": "S"
        }
    ]
}'''
test_input_dict = json.loads(test_input_str)
test_input = json.dumps(test_input_dict)
test_input
```

```
import boto3

# Create a low-level client representing Amazon SageMaker Runtime
sagemaker_runtime = boto3.client("sagemaker-runtime", region_name="ap-northeast-1")

# After you deploy a model into production using SageMaker hosting 
# services, your client applications use this API to get inferences 
# from the model hosted at the specified endpoint.
response = sagemaker_runtime.invoke_endpoint(
                            EndpointName=endpoint_name, 
                            ContentType='application/json',
                            Accept='application/json',
                            Body=test_input # Replace with your own data.
                            )

# Optional - Print the response body and decode it so it is human read-able.
print(response['Body'].read().decode('utf-8'))
```

# Test on Locust
```
pip install locust
pip install boto3
```

```
# change --host option to your endpoint name
locust -f sagemaker_test.py \
  -u 1 \
  --headless \
  --host='http://DEMO-2023-05-22-0416' \
  --stop-timeout 60 \
  -t 3m \
  --logfile=logfile.log \
  --csv=locust.csv \
  --csv-full-history \
  --reset-stats
```

```
# open web ui
locust -f sagemaker_test.py
```

# Destroy Endpoint
Management Console

