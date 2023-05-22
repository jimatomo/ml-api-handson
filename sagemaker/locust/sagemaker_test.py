import time
import boto3
import inspect
from locust import task
from botocore.config import Config
from locust import TaskSet, task, events
from locust.contrib.fasthttp import FastHttpUser
from locust import task, events, constant


def stopwatch(func):
    def wrapper(*args, **kwargs):
        previous_frame = inspect.currentframe().f_back
        _, _, task_name, task_func_name, _ = inspect.getframeinfo(previous_frame)
        task_func_name = task_func_name[0].split(".")[-1].split("(")[0]

        start = time.time()
        result = None

        try:
            result = func(*args, **kwargs)
            total = int((time.time() - start) * 1000)

        except Exception as e:
            events.request.fire(
                request_type=task_name,
                name=task_func_name,
                response_time=total,
                response_length=len(result),
                exception=e,
            )
        else:
            events.request.fire(
                request_type=task_name,
                name=task_func_name,
                response_time=total,
                response_length=len(result),
            )
        return result

    return wrapper


class ProtocolClient:
    def __init__(self, host):
        self.endpoint_name = host.split("/")[-1]
        self.region = "ap-northeast-1"
        self.content_type = "application/json"
        self.payload = '{"data": [{"PassengerId": 892, "Pclass": 3, "Name": "Kelly, Mr. James", "Sex": "male", "Age": 34.5, "SibSp": 0, "Parch": 0, "Ticket": 330911, "Fare": 7.8292, "Cabin": "", "Embarked": "Q"}, {"PassengerId": 893, "Pclass": 3, "Name": "Wilkes, Mrs. James (Ellen Needs)", "Sex": "female", "Age": 47, "SibSp": 1, "Parch": 0, "Ticket": 363272, "Fare": 7, "Cabin": "", "Embarked": "S"}]}'

        boto3config = Config(retries={"max_attempts": 100, "mode": "standard"})
        self.sagemaker_client = boto3.client(
            "sagemaker-runtime", config=boto3config, region_name=self.region
        )

    @stopwatch
    def sagemaker_client_invoke_endpoint(self):
        response = self.sagemaker_client.invoke_endpoint(
            EndpointName=self.endpoint_name,
            Body=self.payload,
            ContentType=self.content_type,
            Accept='application/json',
        )
        response_body = response["Body"].read()
        return response_body


class ProtocolLocust(FastHttpUser):
    abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = ProtocolClient(self.host)
        self.client._locust_environment = self.environment


class ProtocolTasks(TaskSet):
    @task
    def custom_protocol_boto3(self):
        self.client.sagemaker_client_invoke_endpoint()


class ProtocolUser(ProtocolLocust):
    wait_time = constant(0)
    tasks = [ProtocolTasks]