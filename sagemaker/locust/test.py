import boto3
import time

def invoke_endpoint(client, endpoint_name, test_input):
  response = client.invoke_endpoint(
                EndpointName=endpoint_name, 
                ContentType='application/json',
                Accept='application/json',
                Body=test_input # Replace with your own data.
                )

  return response["Body"].read().decode('utf-8')

def main():
  sagemaker_runtime = boto3.client("sagemaker-runtime", region_name="ap-northeast-1")
  test_input='{"data": [{"PassengerId": 892, "Pclass": 3, "Name": "Kelly, Mr. James", "Sex": "male", "Age": 34.5, "SibSp": 0, "Parch": 0, "Ticket": 330911, "Fare": 7.8292, "Cabin": "", "Embarked": "Q"}, {"PassengerId": 893, "Pclass": 3, "Name": "Wilkes, Mrs. James (Ellen Needs)", "Sex": "female", "Age": 47, "SibSp": 1, "Parch": 0, "Ticket": 363272, "Fare": 7, "Cabin": "", "Embarked": "S"}]}'
  endpoint_name="DEMO-2023-05-22-0416"

  for count in range(10):
    start_time = time.time()
    response = invoke_endpoint(sagemaker_runtime, endpoint_name, test_input)
    end_time = time.time()
    total_time = end_time - start_time
    print(response)
    print(total_time)

main()
